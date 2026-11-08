"""Render master data as the systems hold it (messy) + golden truth files for the answer key."""
import csv
import os
from collections import defaultdict
from core import *
import refdata as RD
import catalog as CAT
import world as W
from view import pname, stint_name, ROLE_LABEL
from world import stint_active

O = None
SPECIAL = {}
IND_LEGACY = {"Healthcare": ["Health Care", "Hospital & Health Care", "Medical"], "Technology": ["Hi-Tech", "Computer Software", "Information Technology"],
              "Financial Services": ["Banking", "Finance", "Financial"], "Manufacturing": ["Industrial", "Mfg"], "State & Local Government": ["Government", "Public Sector", "SLED"],
              "Education": ["Higher Ed", "K12", "Education - Public"], "Transportation & Logistics": ["Transportation", "Logistics"],
              "Professional Services": ["Consulting", "Services"], "Energy & Utilities": ["Utilities", "Oil & Gas"], "Life Sciences": ["Pharma", "Biotech"]}
COUNTRY_VARIANTS = {"United States": ["United States", "United States", "United States", "US", "USA", "U.S.", "United States of America", "us"],
                    "Canada": ["Canada", "Canada", "CA", "CAN", "canada"]}


def special_users():
    for key, first, last, title in (("MIGRATION", "Data", "Migration User", "Integration - Data Migration"), ("INTEGRATION", "ERP", "Integration User", "Integration - ERP Sync"),
                                    ("HOLDING", "Sales Ops", "Holding Queue", "Unassigned Accounts Holding User")):
        p = dict(id=sfid("005"), emp_no=f"SYS{len(SPECIAL) + 1:03d}", first=first, last=last, hire=dt.date(2020, 11, 1), term=None, region="HQ",
                 persona="by_the_book", stints=[], rehire_of=None, email=f"{slug(first + last)}@orvane.com", title_override=title)
        W.PEOPLE.append(p)
        SPECIAL[key] = p


def fmt_phone(p):
    digits = "".join(ch for ch in p if ch.isdigit())
    if len(digits) != 10:
        return p
    r = R.random()
    if r < .55:
        return p
    if r < .7:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    if r < .8:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
    if r < .9:
        return f"+1 {digits[:3]} {digits[3:6]} {digits[6:]}"
    return digits


def messy_name(n):
    r = R.random()
    if r < .03:
        return n.upper()
    if r < .05:
        return n + " "
    if r < .07:
        return n.replace(" & ", " and ")
    if r < .09:
        for s in ("Inc.", "LLC", "Corp.", "Co.", "Ltd.", "Corporation", "Holdings", "Group, Inc."):
            if n.endswith(" " + s):
                return n[: -len(s) - 1]
    if r < .105:
        w = n.split()
        i = R.randrange(len(w))
        if len(w[i]) > 5:
            j = R.randint(1, len(w[i]) - 3)
            w[i] = w[i][:j] + w[i][j + 1] + w[i][j] + w[i][j + 2:]
        return " ".join(w)
    return n


# ------------------------------------------------------------------ before commerce
def prep(a):
    a["assets"] = a.get("assets", [])
    a["industry_rec"] = R.choice(IND_LEGACY[a["industry"]]) if a["industry"] in IND_LEGACY and chance(.22) else a["industry"]
    if chance(.04) and a["first_buy"]:
        a["erp_dupe"] = str(seq("erp", 1_000_000, 7, 6))
    a["dupe_crm"] = chance(.04) or (a.get("quillon") and not a.get("quillon_only") and chance(.7))
    a["prov"] = {}
    last = None
    for f in W.FYS:
        if last and chance(.3):
            a["prov"][f] = last
            continue
        e = a["emp"].get(f - 1, a["emp"][f])
        v = dict(emp=human_round(e * R.uniform(.85, 1.18)), rev=human_round(a["rev"].get(f - 1, a["rev"][f]) * R.uniform(.8, 1.25)))
        a["prov"][f] = v
        last = v


# ------------------------------------------------------------------ account + history
def account(a, orders):
    V = a["view"]
    created = MIGRATION_LOAD if (a["first_buy"] and a["first_buy"] < WIN_START) or (a["status_end"] == "never" and chance(.5)) else \
        max(WIN_START, (a["purchases"][0] if a["purchases"] else WIN_START) - D(R.randint(10, 120)))
    src = "Salesforce"
    created_by = SPECIAL["MIGRATION"]["id"] if created == MIGRATION_LOAD else None
    if a.get("quillon") and a.get("quillon_only"):
        created, src, created_by = QUILLON_MIGRATION, "Quillon CRM Migration", SPECIAL["MIGRATION"]["id"]
    own = W.owner_on(a, SNAP)
    owner_id = own["person"]["id"] if own else None
    if own is None:
        prev = next((st for s, e, st in reversed(a["cov"]["OWNER"]) if st), None)
        if prev and chance(.5):
            owner_id = prev["person"]["id"]
            O.issue("owner_inactive_user", "Account", a["id"], "OwnerId", owner_id, "(reassign to active rep)", a["id"],
                    "OwnerId points to inactive User", "Rep left; account never reassigned.", "Medium")
        else:
            owner_id = SPECIAL["HOLDING"]["id"]
            O.issue("owner_holding_queue", "Account", a["id"], "OwnerId", owner_id, "(assign coverage)", a["id"],
                    "Owner = Sales Ops Holding Queue", "Account sitting in holding queue between reps.", "Low")
        a["vacant_label"] = pname(prev["person"]) + " (inactive)" if prev else "Sales Ops Holding Queue"
    par = a["parent"]
    parent_id = par["id"] if par else None
    if a.get("unlinked") and not a.get("linked_on"):
        parent_id = None
        O.issue("subsidiary_not_linked_to_parent", "Account", a["id"], "ParentId", None, par["id"], a["id"],
                "Name/domain/address similarity to parent family; ERP bill-to", f"Subsidiary of {par['legal']} not linked in CRM; covered and priced as standalone.", "High")
    elif par and chance(.03):
        wrong = R.choice([x for x in W.ACCOUNTS if x["role"] == "parent" and x is not par["ultimate"]] or [par])
        parent_id = wrong["id"]
        O.issue("wrong_parent_account", "Account", a["id"], "ParentId", wrong["id"], par["id"], a["id"], "Parent industry/geo mismatch",
                "Linked to the wrong parent account.", "High")
    name = V.crm_name(SNAP)
    true_now = V.true_name(SNAP)
    if name != true_now:
        O.issue("account_name_outdated", "Account", a["id"], "Name", name, true_now, a["id"], "News/website shows new company name",
                "Company rebranded; CRM still has the old name.", "Medium")
    shown = messy_name(name)
    if shown != name:
        O.issue("account_name_formatting", "Account", a["id"], "Name", shown, name, a["id"], "Casing/whitespace/suffix/typo", "Name entered inconsistently.", "Low")
    seg_rec, seg_true = V.seg[26], a["seg"][26]
    if seg_rec != seg_true:
        O.issue("segment_outdated", "Account", a["id"], "Segment__c", seg_rec, seg_true, a["id"], "Employees/spend imply different segment",
                "Segment not updated at FY26 realignment.", "Medium")
    st_rec, st_true = V.status[26], V.true_status(SNAP)
    if st_rec != st_true:
        O.issue("coverage_status_stale", "Account", a["id"], "Coverage_Status__c", st_rec, st_true, a["id"], "Recompute from last purchase date",
                "Retention/Development/Acquisition flag set at Feb-2025 realignment and not refreshed.", "Medium")
    if a.get("stuck_region"):
        O.issue("legacy_region_value", "Account", a["id"], "Region__c", V.region[26], W.region_scope(a, 26), a["id"], "Region not in West/Central/East",
                "Pre-FY24 region label never updated after restructure.", "Low")
    lp_true = V.last_purchase(SNAP)
    lp_rec = lp_true
    if lp_true and chance(.15):
        older = [x for x in a["purchases"] if x < lp_true - D(60)]
        if older:
            lp_rec = R.choice(older)
            O.issue("last_purchase_rollup_wrong", "Account", a["id"], "Last_Purchase_Date__c", ds(lp_rec), ds(lp_true), a["id"],
                    "Compare to max(Sales_Order.Order_Date)", "Roll-up broke when orders came through partner / portal.", "Medium")
    fy25 = sum(o["sub"] for o in orders if o["fy"] == 25 and o.get("opp") and o["status"] != "Cancelled")
    emp_rec = a["prov"][22]["emp"] if chance(.6) else a["prov"][R.choice([23, 24, 25])]["emp"]
    if abs(emp_rec - a["emp"][26]) / max(1, a["emp"][26]) > .35:
        O.issue("employee_count_stale", "Account", a["id"], "NumberOfEmployees", emp_rec, a["emp"][26], a["id"], "Compare to latest firmographics",
                "Employee count never refreshed; company changed size.", "Low")
    cust_since = a["first_buy"] if a["first_buy"] else None
    if a.get("quillon") and a.get("quillon_only") and cust_since:
        O.issue("customer_since_reset_by_migration", "Account", a["id"], "Customer_Since__c", ds(QUILLON_MIGRATION), ds(cust_since), a["id"],
                "Quillon legacy orders predate this", "Migration overwrote original customer-since date.", "Low")
        cust_since = QUILLON_MIGRATION
    typ = {"retention": "Customer", "development": "Customer", "lapsed": "Former Customer", "never": "Prospect"}[a["status_end"]]
    if a.get("flags") and "bankrupt" in a["flags"]:
        typ = "Former Customer"
    partner = W.partner_on(a, SNAP)
    ag = a.get("agreement")
    row = dict(Id=a["id"], Name=shown, Legal_Name__c=a["legal"] if chance(.7) else None, DBA_Name__c=a["dba"], Type=typ, ParentId=parent_id,
               Segment__c=seg_rec, Coverage_Status__c=st_rec, Coverage_Status_As_Of__c="2025-02-01", Region__c=V.region[26],
               Territory__c=f"{V.region[26]}-{seg_rec.split()[0][:3].upper()}-{R.randint(1, 40):02d}", OwnerId=owner_id,
               Partner_Of_Record__c=partner["id"] if partner else None, Industry=a["industry_rec"], Sub_Industry__c=a["sub_industry"] if chance(.7) else None,
               NAICS__c=a["naics"] if chance(.6) else None, Ownership=a["ownership"], TickerSymbol=a.get("ticker"), NumberOfEmployees=emp_rec,
               AnnualRevenue=a["prov"][R.choice([22, 23, 24, 25])]["rev"] if chance(.8) else None, Fiscal_Year_End_Month__c=a["fye_month"] if chance(.5) else None,
               BillingStreet=a["street"], BillingCity=a["city"][2], BillingState=a["state"] if chance(.8) else RD.STATE_NAMES.get(a["state"], a["state"]),
               BillingPostalCode=a["zip"], BillingCountry=R.choice(COUNTRY_VARIANTS[a["country"]]), Phone=fmt_phone(a["phone"]),
               Website=R.choice([f"www.{a['domain']}", a["domain"], f"https://{a['domain']}", f"http://www.{a['domain']}/"]),
               ERP_Customer_Number__c=a["erp"] if chance(.82) else None, BizGraph_Id__c=f"BG{R.randint(10**8, 10**9 - 1)}" if chance(.75) else None,
               Customer_Since__c=ds(cust_since), Last_Purchase_Date__c=ds(lp_rec), Total_Spend_Last_FY__c=round(fy25, 2) if fy25 else None,
               Primary_Competitor__c=a["env"]["primary_competitor"] if chance(.5) else None, Hypervisor__c=a["env"]["hypervisor"] if chance(.4) else None,
               Public_Cloud__c=a["env"]["cloud"] if chance(.4) else None, Contract_Pricing_Agreement__c=ag["id"] if ag else None,
               Credit_Limit__c=a["credit_limit"], Payment_Terms__c=a["terms"], Tax_Exempt__c=tf(a["tax_exempt"]),
               AccountSource=R.choice(["Legacy Load", "Rep Created", "Lead Conversion", "ERP Sync", None]),
               Description=None, Source_System__c=src, Legacy_Quillon_Id__c=a.get("quillon_erp") if a.get("quillon") else None, IsDeleted="false",
               MasterRecordId=None, CreatedDate=ts(created), CreatedById=created_by or (W.owner_on(a, created) or {"person": SPECIAL["MIGRATION"]})["person"]["id"],
               LastModifiedDate=ts(SNAP - D(R.randint(0, 200))), LastActivityDate=None)
    if a.get("showcase"):
        row["Description"] = R.choice([None, "Key account", "see account plan", None])
    O.add("Account", row)
    history(a, V, created)
    team(a)
    firmo(a)
    contacts(a)
    if a["dupe_crm"]:
        duplicate(a, row)
    for p, s, e in a["partner_hist"]:
        O.add("Account_Partner__c", dict(Id=sfid("a0D"), Account__c=a["id"], Partner_Account__c=p["id"], Role__c="Partner of Record",
                                          Start_Date__c=ds(max(s, WIN_START)), End_Date__c=ds(e), Is_Primary__c=tf(e is None)))
    if a.get("acquired_by"):
        b, d = a["acquired_by"]
        O.issue("acquired_company_not_reparented", "Account", a["id"], "ParentId", parent_id, b["id"], a["id"], "News: acquired by another customer",
                f"Acquired by {b['legal']} on {d}; CRM still shows it as independent.", "Medium")


MIGRATION_LOAD = dt.date(2021, 1, 29)


def history(a, V, created):
    def h(field, old, new, d, who=None):
        if d < created or old == new:
            return
        O.add("AccountHistory", dict(Id=sfid("017"), AccountId=a["id"], Field=field, OldValue=old, NewValue=new, CreatedDate=ts(min(d, SNAP)),
                                     CreatedById=who or SPECIAL["INTEGRATION"]["id"]))
    prev = None
    for s, e, st in a["cov"]["OWNER"]:
        cur = st["person"] if st else None
        if prev is not None and cur is not None and cur is not prev:
            h("Owner", pname(prev), pname(cur), s + D(R.randint(0, 25)))
        if cur is not None:
            prev = cur
    for f in W.FYS[1:]:
        h("Segment__c", V.seg[f - 1], V.seg[f], fy_start(f) + D(R.randint(0, 20)))
        h("Coverage_Status__c", V.status[f - 1], V.status[f], fy_start(f) + D(R.randint(0, 20)))
        h("Region__c", V.region[f - 1], V.region[f], fy_start(f) + D(R.randint(0, 30)))
    for d, nb in V.name_changes:
        upd = V.crm_name_lag.get(d)
        if upd:
            h("Name", a["legal"], nb, upd, None)
    if a.get("linked_on"):
        h("Parent", None, a["parent"]["legal"], a["linked_on"])
    for p, s, e in a["partner_hist"][1:]:
        h("Partner_Of_Record__c", a["partner_hist"][0][0]["base_name"], p["base_name"], s)
    for f in W.FYS:
        own = W.owner_on(a, fy_start(f) + D(10))
        O.add("Account_Segment_History__c", dict(Id=sfid("a04"), Account__c=a["id"], Fiscal_Year__c=f"FY{f}", Segment__c=V.seg[f],
                                                  Coverage_Status__c=V.status[f], Region__c=V.region[f],
                                                  Territory__c=f"{V.region[f]}-{V.seg[f].split()[0][:3].upper()}",
                                                  Assigned_Owner__c=own["person"]["id"] if own else None, Realignment_Date__c=ds(fy_start(f)),
                                                  Notes__c="FY24 restructure: two US regions + Canada split into West / Central / East" if f == 24 and V.region[23] != V.region[24] else None))
        if f > 22 and V.seg[f] != V.seg[f - 1]:
            V.event(a, fy_start(f), "CRM", "Segment Change", f"{V.seg[f - 1]} -> {V.seg[f]}", record_table="Account_Segment_History__c",
                    subject=f"Realignment FY{f}: {V.seg[f - 1]} -> {V.seg[f]}")


def team(a):
    for lab, iv in a["cov"].items():
        for s, e, st in iv:
            if st is None:
                continue
            O.add("AccountTeamMember", dict(Id=sfid("01M"), AccountId=a["id"], UserId=st["person"]["id"],
                                            TeamMemberRole=ROLE_LABEL.get(lab if lab != "OWNER" else "OWNER", lab) if lab != "OWNER" else
                                            ("Account Owner" if st["role"] != "SEL_RAM" else "Regional Account Manager - Select"),
                                            Start_Date__c=ds(s), End_Date__c=ds(e - D(1)) if e <= SNAP else None, Is_Current__c=tf(e > SNAP),
                                            CreatedDate=ts(s)))


def firmo(a):
    for f in W.FYS:
        pv = a["prov"][f]
        O.add("Account_Firmographics__c", dict(Id=sfid("a03"), Account__c=a["id"], Fiscal_Year__c=f"FY{f}", Source__c="BizGraph Data (3rd party)",
                                                Employees__c=pv["emp"], Annual_Revenue__c=pv["rev"], Est_IT_Budget__c=human_round(a["itb"][f] * R.uniform(.7, 1.3)),
                                                Number_Of_Sites__c=len([s for s in a["sites"] if not s["opened"] or s["opened"] <= fy_end(f)]),
                                                Employee_Growth_Pct__c=round(100 * (a["emp"][f] / max(1, a["emp"][f - 1]) - 1), 1) if chance(.8) else None,
                                                Credit_Rating__c=R.choice(["A1", "A2", "A3", "B1", "B2", "B3", "C1"]) if chance(.7) else None,
                                                As_Of_Date__c=ds(fy_start(f) + D(R.randint(0, 200)))))
        if chance(.18):
            O.add("Account_Firmographics__c", dict(Id=sfid("a03"), Account__c=a["id"], Fiscal_Year__c=f"FY{f}", Source__c="Rep Entered",
                                                    Employees__c=human_round(a["emp"][f] * R.uniform(.6, 1.5)), Annual_Revenue__c=None, Est_IT_Budget__c=None,
                                                    Number_Of_Sites__c=None, As_Of_Date__c=ds(fy_start(f) + D(R.randint(0, 300)))))
        env = a["env"]
        w11 = 0 if f < 23 else min(100, (f - 22) * R.randint(10, 30))
        if a.get("showcase") == "headcount_jump_flat_pc_spend":
            w11 = min(w11, 25)
        O.add("Account_Environment__c", dict(Id=sfid("a0E"), Account__c=a["id"], Fiscal_Year__c=f"FY{f}",
                                              Client_OS__c="Windows 10" if w11 == 0 else f"Windows 11 ~{w11}% / Windows 10 remainder" if w11 < 100 else "Windows 11",
                                              Hypervisor__c=env["hypervisor"] if not (f >= 25 and "VMware exit / hypervisor change" in sum((a["inits"][x] for x in a["inits"] if x <= f), [])) else "Migrating to Converge HCI / Hyper-V",
                                              Public_Cloud__c=env["cloud"], ITSM_Tool__c=env["itsm"], Backup_Approach__c=env["backup"],
                                              Est_Endpoints__c=human_round(a["emp"][f] * R.uniform(1.0, 1.4)), Est_Servers__c=human_round(max(1, a["emp"][f] / R.uniform(25, 80))),
                                              Est_Storage_TB__c=human_round(max(1, a["emp"][f] * R.uniform(.05, .6))), Primary_Competitor__c=env["primary_competitor"],
                                              Competitor_Install_Pct__c=round(env["competitor_share"] * 100), Strategic_Initiatives__c="; ".join(a["inits"].get(f, [])) or None,
                                              Source__c=R.choice(["Rep discovery", "BizGraph technographics", "QBR", "Rep discovery"])))


BUYING_ROLES = {"C-Level": ["Economic Buyer", "Executive Sponsor", "Decision Maker"], "VP": ["Decision Maker", "Economic Buyer", "Champion"],
                "Director": ["Champion", "Technical Evaluator", "Decision Maker", "Influencer"], "Manager": ["Technical Evaluator", "Influencer", "Procurement", "Champion"],
                "Individual Contributor": ["Technical Evaluator", "End User", "Influencer", "Procurement"], "Shared Mailbox": ["Procurement", "Accounts Payable"]}


def contacts(a):
    own = W.owner_on(a, SNAP)
    owner_id = own["person"]["id"] if own else SPECIAL["HOLDING"]["id"]
    for c in a["contacts"]:
        left = c["end"] is not None and c["end"] <= SNAP
        status, left_d, bounced = "Active", None, "false"
        if left:
            if chance(.42) and not c.get("champion"):
                status, left_d = "Left Company", ds(c["end"] + D(R.randint(5, 200)))
            else:
                bounced = tf(chance(.55))
                O.issue("contact_left_company_still_active", "Contact", c["id"], "Status__c", "Active", "Left Company", a["id"],
                        "Bounced email / no activity / LinkedIn-style job change", f"Left the company around {c['end']}." +
                        (f" Now at another customer (contact {c['moved_to']['id']})." if c.get("moved_to") else ""), "Medium")
        title = c["title"]
        for d, old, new in c["title_hist"]:
            if chance(.5):
                O.add("ContactHistory", dict(Id=sfid("01b"), ContactId=c["id"], Field="Title", OldValue=old, NewValue=new, CreatedDate=ts(d)))
                title = new
            else:
                O.issue("contact_title_outdated", "Contact", c["id"], "Title", old, new, a["id"], "Email signatures / meeting notes show new title",
                        "Promotion never updated in CRM.", "Low")
        rp = c["reports_to"]
        O.add("Contact", dict(Id=c["id"], AccountId=a["id"], FirstName=c["first"], LastName=c["last"], Title=title if chance(.93) else None, Department=c["dept"],
                              Level__c=c["level"], Email=c["email"], Phone=fmt_phone(c["phone"]) if chance(.85) else None, MobilePhone=c["mobile"],
                              ReportsToId=rp["id"] if rp and chance(.6) else None, Buying_Role__c=R.choice(BUYING_ROLES.get(c["level"], ["Influencer"])) if chance(.7) else None,
                              Status__c=status, HasOptedOutOfEmail=tf(chance(.05)), Email_Bounced__c=bounced, MailingCity=a["city"][2], MailingState=a["state"],
                              MailingCountry=a["country"], OwnerId=owner_id, LeadSource=R.choice(["Legacy Load", "Rep Created", "Event", "Web", "Lead Conversion", None]),
                              Start_Date__c=ds(c["start"]) if chance(.3) else None, Left_Company_Date__c=left_d, IsDeleted="false", MasterRecordId=None,
                              CreatedDate=ts(max(c["start"], MIGRATION_LOAD)), LastModifiedDate=ts(SNAP - D(R.randint(0, 400))), LastActivityDate=None))
        if c.get("moved_from"):
            O.issue("same_person_new_company", "Contact", c["id"], "Id", c["id"], c["moved_from"]["id"], a["id"], "Same name, new email domain",
                    "This contact previously worked at another customer account (job move) - relationship carries over.", "Info")
        if chance(.03) and not c["shared"]:
            did = sfid("003")
            nick = {"Robert": "Bob", "William": "Bill", "Richard": "Rick", "Michael": "Mike", "Jennifer": "Jen", "Christopher": "Chris",
                    "Katherine": "Kate", "Elizabeth": "Liz", "Daniel": "Dan", "Matthew": "Matt", "Joshua": "Josh", "Anthony": "Tony"}.get(c["first"], c["first"])
            O.add("Contact", dict(Id=did, AccountId=a["id"], FirstName=nick, LastName=c["last"], Title=title, Email=c["email"].upper() if chance(.4) else c["email"],
                                  Status__c="Active", OwnerId=owner_id, LeadSource="Event", CreatedDate=ts(rand_bday(max(c["start"], WIN_START), SNAP)),
                                  IsDeleted="false", Email_Bounced__c="false"))
            O.issue("duplicate_contact", "Contact", did, "Id", did, c["id"], a["id"], "Same last name + email", "Duplicate contact created from event badge scan.", "Low")


def duplicate(a, master):
    """A second CRM account for the same company (Quillon migration or rep-created), often owned by a different rep."""
    did = sfid("001")
    q = a.get("quillon") and not a.get("quillon_only")
    nm = a.get("quillon_name") if q else R.choice([a["base_name"], a["legal"].upper(), a["base_name"] + " - " + a["city"][2], a["legal"].replace(",", ""),
                                                   a["base_name"] + " (old)", a["domain"].split(".")[0].title()])
    alt = [s for s in W.STINTS if s["role"] in ("MB_IAE", "LE_FAE", "SB_REP", "LE_IAE") and stint_active(s, SNAP)]
    owner = R.choice(alt)["person"]["id"] if alt and chance(.7) else SPECIAL["MIGRATION"]["id"]
    merged = chance(.2)
    O.add("Account", dict(Id=did, Name=nm, Type="Customer" if a["first_buy"] else "Prospect", Segment__c=R.choice(W.SEGS[:3]), Region__c=W.region_scope(a, 23),
                          OwnerId=owner, Industry=a["industry_rec"], BillingCity=a["city"][2], BillingState=a["state"], BillingCountry=R.choice(COUNTRY_VARIANTS[a["country"]]),
                          Phone=fmt_phone(a["phone"]), Website=a["domain"] if chance(.6) else None, ERP_Customer_Number__c=a.get("erp_dupe") or (a.get("quillon_erp") if q else None),
                          Source_System__c="Quillon CRM Migration" if q else "Salesforce", Legacy_Quillon_Id__c=a.get("quillon_erp") if q else None,
                          IsDeleted=tf(merged), MasterRecordId=a["id"] if merged else None,
                          CreatedDate=ts(QUILLON_MIGRATION if q else rand_bday(WIN_START, SNAP - D(30))), CreatedById=SPECIAL["MIGRATION"]["id"] if q else owner,
                          Coverage_Status__c=R.choice(["Retention", "Development", "Acquisition", None]), Description="Migrated from Quillon" if q else None))
    if not merged:
        O.issue("duplicate_account", "Account", did, "Id", did, a["id"], a["id"], "Name/domain/phone match", ("Quillon migration created a second record; " if q else "") +
                "duplicate owned by a different rep.", "High")
    a["dupe_id"] = did
    for c in R.sample(a["contacts"], min(len(a["contacts"]), R.randint(0, 3))):
        cid = sfid("003")
        O.add("Contact", dict(Id=cid, AccountId=did, FirstName=c["first"], LastName=c["last"], Title=c["title"], Email=c["email"], Status__c="Active",
                              OwnerId=owner, CreatedDate=ts(QUILLON_MIGRATION if q else rand_bday(WIN_START, SNAP)), IsDeleted="false", Email_Bounced__c="false"))
        O.issue("duplicate_contact", "Contact", cid, "AccountId", did, c["id"], a["id"], "Contact exists on master account", "Contact copied onto duplicate account.", "Low")


# ------------------------------------------------------------------ globals
def users(leaders):
    rvp = {k[-1]: v for k, v in leaders.items() if k.startswith("RVP")}
    for p in W.PEOPLE:
        st = p["stints"][-1] if p["stints"] else None
        title = p.get("title_override") or (W.ROLES.get(st["role"], (st["role"],))[0] if st else "User")
        region = st["region"] if st else p["region"]
        mgr = rvp.get((region or "W")[0]) or leaders.get("CRO")
        if p.get("title_override", "").startswith(("Chief Exec",)):
            mgr = None
        act = p["term"] is None
        O.add("User", dict(Id=p["id"], EmployeeNumber=p["emp_no"], FirstName=p["first"], LastName=p["last"], Name=pname(p), Email=p["email"], Title=title,
                           Department="Sales" if st and st["role"] not in ("SUPPORT", "COLL", "CREDIT", "ORDERS", "MKT") else "Operations",
                           Sales_Role__c=ROLE_LABEL.get(st["role"], st["role"]) if st else None, Region__c=region,
                           ManagerId=mgr["id"] if mgr and mgr is not p else None, IsActive=tf(act), Hire_Date__c=ds(p["hire"]),
                           Termination_Date__c=ds(p["term"]), Rehire_Of__c=p["rehire_of"]["id"] if p["rehire_of"] and chance(.5) else None,
                           CreatedDate=ts(max(p["hire"], dt.date(2020, 12, 15)))))
        if p["rehire_of"]:
            O.issue("boomerang_duplicate_user", "User", p["id"], "Rehire_Of__c", None, p["rehire_of"]["id"], None, "Same name, new user record",
                    "Rep left and was rehired; history split across two user records.", "Low")
        for s in p["stints"]:
            O.add("User_Role_History__c", dict(Id=sfid("a0C"), User__c=p["id"], Sales_Role__c=s["role"], Role_Title__c=W.ROLES.get(s["role"], (s["role"],))[0],
                                                Region__c=s["region"], Start_Date__c=ds(s["start"]), End_Date__c=ds(s["end"]),
                                                Change_Reason__c="Promotion" if s.get("promoted") else "Termination" if s.get("left") else
                                                "FY24 Restructure" if s["end"] == dt.date(2023, 2, 1) else None))


def partners():
    for p in W.PARTNERS:
        O.add("Account", dict(Id=p["id"], Name=p["legal"], Type="Partner", Segment__c="Partner", Region__c=p["region"], Industry="IT Services / Reseller",
                              BillingCity=p["city"][2], BillingState=p["state"], BillingCountry=p["country"], Phone=p["phone"], Website=p["domain"],
                              ERP_Customer_Number__c=p["erp"], Description=f"{p['type']} - {p['tier']} partner. Focus: {p['focus']}", Source_System__c="Salesforce",
                              Customer_Since__c=ds(p["joined"]), CreatedDate=ts(MIGRATION_LOAD), IsDeleted="false", Credit_Limit__c=5_000_000, Payment_Terms__c="Net 45"))
        O.add("ERP_Customer", dict(Customer_Number=p["erp"], Customer_Name=p["legal"].upper(), Customer_Type="Reseller", Bill_To_Address=p["street"], City=p["city"][2],
                                   State_Province=p["state"], Postal_Code=p["zip"], Country_Code="CA" if p["country"] == "Canada" else "US",
                                   Currency="CAD" if p["country"] == "Canada" else "USD", Payment_Terms="Net 45", Credit_Limit=5_000_000, Tax_Exempt="Y",
                                   Status="Active", Source_System="ORV_ERP", Created_Date=ds(p["joined"])))


def erp_master(a):
    cc = "CA" if a["country"] == "Canada" else "US"
    nm = a["legal"].upper() if chance(.5) else a["legal"]
    pnum = a["ultimate"]["erp"] if a["parent"] and not a.get("unlinked") and chance(.6) else None
    rows = [dict(Customer_Number=a["erp"], Customer_Name=nm, Customer_Type="Direct", Parent_Customer_Number=pnum, Bill_To_Address=a["street"], City=a["city"][2],
                 State_Province=a["state"], Postal_Code=a["zip"], Country_Code=cc, Currency=a["currency"], Payment_Terms=a["terms"], Credit_Limit=a["credit_limit"],
                 Tax_Exempt="Y" if a["tax_exempt"] else "N", Tax_Cert_Expiration=ds(a["tax_cert_exp"]), Status="Active" if a["first_buy"] else "Prospect - No Orders",
                 Source_System="ORV_ERP", Created_Date=ds(a["first_buy"] if a["first_buy"] and a["first_buy"] > dt.date(2010, 1, 1) else dt.date(2010, 1, 1)))]
    if a.get("erp_dupe"):
        rows.append(dict(rows[0], Customer_Number=a["erp_dupe"], Customer_Name=messy_name(a["base_name"]).upper(), Parent_Customer_Number=None,
                         Created_Date=ds(rand_bday(WIN_START, SNAP - D(200)))))
        O.issue("duplicate_erp_customer", "ERP_Customer", a["erp_dupe"], "Customer_Number", a["erp_dupe"], a["erp"], a["id"], "Same name/address in ERP",
                "Second ERP sold-to created for the same customer; orders split across both.", "High")
    if a.get("quillon"):
        rows.append(dict(rows[0], Customer_Number=a["quillon_erp"], Customer_Name=a["quillon_name"], Parent_Customer_Number=None, Source_System="QUILLON_ERP",
                         Status="Inactive - Migrated", Created_Date=ds(a["first_buy"] if a["first_buy"] > dt.date(2010, 1, 1) else dt.date(2012, 3, 1))))
    for r in rows:
        if a["first_buy"] or chance(.3):
            O.add("ERP_Customer", r)
    for s in a["sites"]:
        O.add("ERP_Ship_To", dict(Ship_To_Number=s["id"], Customer_Number=a["erp"], Site_Type=s["type"], Address=s["street"], City=s["city"][2] if isinstance(s["city"], tuple) else s["city"],
                                  State_Province=s["state"], Postal_Code=s["zip"], Country_Code="CA" if s["country"] == "Canada" else "US",
                                  Active="N" if a.get("hq_move") and s["type"] == "Headquarters" and chance(.4) else "Y", Created_Date=ds(s["opened"]) if s["opened"] else None))
    # crosswalk (incomplete / partly wrong)
    if a["first_buy"]:
        r = R.random()
        if r < .86:
            O.add("CRM_ERP_Crosswalk", dict(CRM_Account_Id=a["id"], ERP_Customer_Number=a["erp"], Match_Method=R.choice(["Integration", "Integration", "Manual"]),
                                            Match_Confidence=R.choice(["High", "High", "Medium"]), Last_Verified_Date=ds(rand_bday(WIN_START, SNAP))))
        elif r < .89:
            wrong = R.choice(W.ACCOUNTS)["erp"]
            O.add("CRM_ERP_Crosswalk", dict(CRM_Account_Id=a["id"], ERP_Customer_Number=wrong, Match_Method="Fuzzy Name Match", Match_Confidence="Low",
                                            Last_Verified_Date=None))
            O.issue("crosswalk_wrong_mapping", "CRM_ERP_Crosswalk", a["id"], "ERP_Customer_Number", wrong, a["erp"], a["id"], "Address/name mismatch",
                    "Fuzzy match linked CRM account to the wrong ERP customer.", "High")
        else:
            O.issue("crosswalk_missing", "CRM_ERP_Crosswalk", a["id"], "ERP_Customer_Number", None, a["erp"], a["id"], "No crosswalk row",
                    "CRM account not mapped to its ERP customer.", "Medium")
        if a.get("quillon") and chance(.6):
            O.add("CRM_ERP_Crosswalk", dict(CRM_Account_Id=a["id"], ERP_Customer_Number=a["quillon_erp"], Match_Method="Quillon Migration Map",
                                            Match_Confidence="Medium", Last_Verified_Date=ds(QUILLON_MIGRATION)))
    if a.get("agreement"):
        ag = a["agreement"]
        for cat, dsc in ag["disc"].items():
            O.add("Contract_Pricing_Agreement", dict(Agreement_Number=ag["id"], Customer_Number=a["erp"], CRM_Account_Id=a["id"], Agreement_Name=f"{a['base_name']} Master Purchase Agreement",
                                                     Start_Date=ds(ag["start"]), End_Date=ds(add_months(ag["start"], 60)), Category=cat.replace("_", " ").title(),
                                                     Discount_Pct=round(dsc * 100, 1), Applies_To_Subsidiaries="Y", Status="Active",
                                                     Signed_By=f"{a['contacts'][0]['first']} {a['contacts'][0]['last']}" if a["contacts"] else None))


def products():
    for p in CAT.PRODUCTS:
        O.add("Product2", dict(Id=p["Id"], ProductCode=p["sku"], Name=p["name"], Family=p["family"], Product_Line__c=p["line"], Business_Unit__c=p["bu"],
                               Category__c=p["category"], Generation__c=p["gen"], List_Price__c=p["list"], Standard_Cost_Pct__c=p["cost_pct"],
                               Launch_Date__c=ds(p["launch"]), End_Of_Life_Date__c=ds(p["eol"]), IsActive=tf(p["eol"] is None or p["eol"] > SNAP),
                               QuantityUnitOfMeasure=p["unit"], Is_Recurring__c=tf(p["recurring"]), Term_Months__c=p["term"], Serialized__c=tf(p["serialized"]),
                               Specs__c=p["specs"]))
        last = None
        for d in [p["launch"], dt.date(2021, 7, 1), dt.date(2022, 2, 1), dt.date(2023, 2, 1), dt.date(2024, 8, 1), dt.date(2025, 2, 1), dt.date(2025, 4, 1)] + \
                ([p["eol"] - D(239)] if p["eol"] else []):
            if d < p["launch"] or d > SNAP:
                continue
            lp = CAT.list_price(p, d)
            if lp != last:
                O.add("Price_History", dict(SKU=p["sku"], Effective_Date=ds(d), List_Price=lp,
                                            Change_Reason="Launch" if d == p["launch"] else "Prior-generation markdown" if p["eol"] and d >= p["eol"] - D(240) else
                                            "Component cost increase" if lp > (last or 0) else "Market price adjustment"))
                last = lp


# ------------------------------------------------------------------ golden truth (answer key)
def golden(root):
    k = os.path.join(root, "answer_key")
    with open(os.path.join(k, "golden_account_master.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["account_id", "true_legal_name_at_snapshot", "original_legal_name", "role", "true_parent_account_id", "true_ultimate_parent_account_id",
                    "unlinked_in_crm", "duplicate_crm_account_id", "duplicate_erp_customer", "quillon_legacy_customer", "true_segment_FY22", "true_segment_FY23",
                    "true_segment_FY24", "true_segment_FY25", "true_segment_FY26", "true_status_at_snapshot", "true_last_purchase_date", "first_purchase_date",
                    "true_region_FY26", "employees_FY22", "employees_FY26", "growth_pattern", "partner_of_record_at_snapshot", "acquired_by_account_id",
                    "renamed", "bankrupt", "showcase_storyline"])
        for a in W.ACCOUNTS:
            V = a["view"]
            par = a["parent"]
            w.writerow([a["id"], V.true_name(SNAP), a["legal"], a["role"], par["id"] if par else None, a["ultimate"]["id"] if par else None,
                        bool(a.get("unlinked") and not a.get("linked_on")), a.get("dupe_id"), a.get("erp_dupe"), a.get("quillon_erp"),
                        *[a["seg"][f] for f in W.FYS], V.true_status(SNAP), ds(V.last_purchase(SNAP)), ds(a["first_buy"]), W.region_scope(a, 26),
                        a["emp"][22], a["emp"][26], a["growth"], (W.partner_on(a, SNAP) or {}).get("base_name"),
                        a["acquired_by"][0]["id"] if a.get("acquired_by") else None, "renamed" in a["flags"], "bankrupt" in a["flags"], a.get("showcase")])
    with open(os.path.join(k, "golden_coverage_history.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["account_id", "coverage_role", "start_date", "end_date", "user_id", "user_name", "vacant"])
        for a in W.ACCOUNTS:
            for lab, iv in a["cov"].items():
                for s, e, st in iv:
                    w.writerow([a["id"], ROLE_LABEL.get(lab, lab) if lab != "OWNER" else "Account Owner", ds(s), ds(min(e, SNAP)),
                                st["person"]["id"] if st else None, stint_name(st) if st else None, st is None])
    with open(os.path.join(k, "golden_contacts.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["contact_id", "account_id", "true_status", "left_date", "moved_to_contact_id", "moved_from_contact_id", "true_current_title"])
        for c in W.CONTACTS:
            w.writerow([c["id"], c["acct"]["id"], "Left Company" if c["end"] and c["end"] <= SNAP else "Active", ds(c["end"]),
                        c["moved_to"]["id"] if c.get("moved_to") else None, c["moved_from"]["id"] if c.get("moved_from") else None,
                        c["title_hist"][-1][2] if c["title_hist"] else c["title"]])
