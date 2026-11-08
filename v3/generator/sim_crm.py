"""Pass 2b (per account): CRM pipeline, quotes, deal regs, approvals, activities & notes, cases & surveys,
telemetry & advisories, campaigns, leads, intent, news. Context-driven topics so text matches the facts."""
import math
from collections import defaultdict
from core import *
import refdata as RD
import catalog as CAT
import world as W
import text as TX
import phrasebank as PB
from view import pname, stint_name, ROLE_LABEL
from world import stint_active
import sim_commerce as SC

O = None
CAMPAIGNS = []
ADVISORIES = []
REP_STATS = defaultdict(lambda: defaultdict(float))   # person id -> {(fy,q,'won'/'pipe'): amount}
STAGES = [("Prospecting", 10, "Pipeline"), ("Qualify", 20, "Pipeline"), ("Solution Design", 40, "Pipeline"),
          ("Proposal", 60, "Best Case"), ("Negotiation", 80, "Commit")]
LEGACY_STAGE = {"Qualify": "Qualification", "Solution Design": "Needs Analysis", "Proposal": "Proposal/Price Quote", "Negotiation": "Negotiation/Review"}
TOPIC_OF = {"client": "client_refresh", "workstation": "client_refresh", "server": "server_refresh", "storage": "storage_capacity",
            "data_protection": "data_protection", "networking": "networking_upgrade", "software": "software_licensing", "services": "services_deployment"}


# ------------------------------------------------------------------ global setup objects
def build_campaigns():
    venues = {22: ("Virtual", dt.date(2021, 9, 21)), 23: ("Las Vegas", dt.date(2022, 9, 13)), 24: ("Austin", dt.date(2023, 9, 19)),
              25: ("Las Vegas", dt.date(2024, 9, 17)), 26: ("Orlando", dt.date(2025, 9, 16))}
    for f, (city, d) in venues.items():
        CAMPAIGNS.append(dict(Id=sfid("701"), Name=f"Orvane Tech Summit FY{f} - {city}", Type="Conference", _kind="summit", _d=d,
                              StartDate=ds(d), EndDate=ds(d + D(2)), Region__c="All", BudgetedCost=2_400_000 + f * 150_000,
                              ActualCost=round((2_400_000 + f * 150_000) * R.uniform(.9, 1.1), -3), Status="Completed",
                              Description=f"Annual customer conference, {city}. Keynotes, AI & infrastructure tracks, Select executive forum."))
    for f in W.FYS:
        for reg in ("West", "Central", "East"):
            for q in (1, 3):
                d = rand_bday(fy_start(f) + D(90 * (q - 1) + 20), fy_start(f) + D(90 * q - 10))
                if d > SNAP:
                    continue
                CAMPAIGNS.append(dict(Id=sfid("701"), Name=f"Orvane Infrastructure Roadshow FY{f} Q{q} - {reg if f >= 24 else ('US West' if reg == 'West' else 'US East')}",
                                      Type="Roadshow", _kind="roadshow", _d=d, _reg=reg, StartDate=ds(d), EndDate=ds(d), Region__c=reg,
                                      BudgetedCost=85000, ActualCost=round(R.uniform(70000, 98000), -2), Status="Completed",
                                      Description="Half-day regional event: servers, storage, data protection."))
        topics = ["Windows 11 Readiness", "AI Infrastructure 101", "Ransomware Recovery Playbook", "Leaving VMware: Your Options",
                  "Device-as-a-Service Economics", "Edge Computing for Operations", "Storage Consolidation", "Workstations for AI & Design"]
        for m in range(0, 12, 2):
            d = rand_bday(fy_start(f) + D(30 * m), fy_start(f) + D(30 * m + 25))
            if d > SNAP:
                continue
            t = R.choice([x for x in topics if not (("AI" in x or "VMware" in x) and f < 24)])
            CAMPAIGNS.append(dict(Id=sfid("701"), Name=f"Webinar: {t} ({d.strftime('%b %Y')})", Type="Webinar", _kind="webinar", _d=d, _topic=t,
                                  StartDate=ds(d), EndDate=ds(d), Region__c="All", BudgetedCost=12000, ActualCost=round(R.uniform(8000, 14000), -2),
                                  Status="Completed", Description=t))
        d = rand_bday(fy_start(f) + D(150), fy_start(f) + D(200))
        CAMPAIGNS.append(dict(Id=sfid("701"), Name=f"Select Executive Forum FY{f}", Type="Executive Event", _kind="exec_forum", _d=d,
                              StartDate=ds(d), EndDate=ds(d + D(1)), Region__c="All", BudgetedCost=600000, ActualCost=round(R.uniform(520000, 650000), -3),
                              Status="Completed", Description="Invite-only CIO forum for Select accounts."))
    CAMPAIGNS.append(dict(Id=sfid("701"), Name="Windows 10 End-of-Support Refresh Program", Type="Email / ABM", _kind="win11", _d=dt.date(2024, 6, 3),
                          StartDate="2024-06-03", EndDate="2025-10-14", Region__c="All", BudgetedCost=1_200_000, ActualCost=1_140_000, Status="Completed",
                          Description="ABM + email program targeting Windows 10 fleets ahead of Oct 2025 end of support."))
    for c in CAMPAIGNS:
        O.add("Campaign", c)


ADV_DEFS = [
    ("OSA-2021-031", "BMC remote code execution in Atlas management controller", "Critical", 9.8, dt.date(2021, 10, 12), ("Atlas Rack Servers", "Atlas Tower Servers")),
    ("OSA-2022-007", "Storage controller firmware data corruption under heavy dedupe", "High", 8.1, dt.date(2022, 3, 22), ("Strata Storage",)),
    ("OSA-2022-044", "UEFI SMM privilege escalation", "High", 7.8, dt.date(2022, 9, 6), ("Atlas Rack Servers", "Atlas Modular", "Converge HCI")),
    ("OSA-2023-012", "Switch OS SSH authentication bypass", "Critical", 9.1, dt.date(2023, 2, 28), ("Mesh Networking",)),
    ("OSA-2023-058", "Backup appliance immutability bypass via API", "High", 8.4, dt.date(2023, 8, 15), ("Vault Data Protection",)),
    ("OSA-2024-017", "BMC firmware vulnerability allows unauthenticated session hijack", "Critical", 9.4, dt.date(2024, 4, 9), ("Atlas Rack Servers", "Atlas AI Servers", "Outpost Edge")),
    ("OSA-2024-063", "Drive firmware premature wear-out (7.68TB NVMe)", "High", 7.5, dt.date(2024, 10, 22), ("Strata Storage", "Converge HCI")),
    ("OSA-2025-009", "GPU node thermal throttling firmware defect", "Medium", 6.2, dt.date(2025, 3, 18), ("Atlas AI Servers",)),
    ("OSA-2025-041", "Storage OS NFS export permission flaw", "High", 8.0, dt.date(2025, 7, 29), ("Strata Storage",)),
    ("OSA-2025-077", "BMC Redfish API information disclosure", "Medium", 5.9, dt.date(2025, 11, 4), ("Atlas Rack Servers", "Atlas Modular", "Atlas AI Servers")),
]


def build_advisories():
    for num, title, sev, cvss, d, fams in ADV_DEFS:
        aid = sfid("a0A")
        ADVISORIES.append(dict(id=aid, num=num, d=d, fams=fams, sev=sev, title=title))
        O.add("Security_Advisory__c", dict(Id=aid, Advisory_Number__c=num, Title__c=title, Severity__c=sev, CVSS__c=cvss, Published_Date__c=ds(d),
                                           Affected_Products__c="; ".join(fams), Fixed_Firmware__c="See release notes - fixed in builds released after " + ds(d),
                                           Description__c=f"{title}. Customers should update firmware on affected {', '.join(fams)} systems."))


# ------------------------------------------------------------------ slot helper
import bisect as _bis


def _acache(a):
    n = len(a.get("assets", []))
    c = a.get("_acache")
    if c is None or c[0] != n:
        infra = sorted((x["sd"], i, x) for i, x in enumerate(a.get("assets", [])) if x["p"]["bu"] == "Infrastructure Solutions")
        stor = [t for t in infra if t[2]["p"]["category"] in ("Storage", "Data Protection")]
        srv_cum, k = [], 0
        for t in infra:
            k += t[2]["p"]["category"] in ("Servers", "AI Servers")
            srv_cum.append(k)
        c = (n, [t[0] for t in infra], [t[2] for t in infra], [t[0] for t in stor], [t[2] for t in stor], srv_cum)
        a["_acache"] = c
    return c


TECH_TOPICS = {"client_refresh", "win11_migration", "server_refresh", "storage_capacity", "data_protection", "hci_virtualization", "ai_gpu_initiative",
               "networking_upgrade", "edge_deployment", "support_escalation", "security_advisory", "services_deployment", "software_licensing", "consumption_billing"}
FIN_TOPICS = {"po_followup", "credit_hold_collections", "pricing_negotiation", "contract_pricing", "lease_end"}


def slots_for(a, d, contact=None, rep=None, o=None, extra=None, topic=None):
    cs = [c for c in a["contacts"] if c["start"] <= d and (c["end"] is None or c["end"] > d) and not c["shared"]] or a["contacts"][:1]
    c = contact or (R.choice(cs) if cs else None)
    if contact is None and topic and cs:
        if topic in TECH_TOPICS:
            pool = [x for x in cs if x["dept"] in ("IT", "Security", "Engineering", "Data & Analytics", "Clinical IT", "Executive")] or cs
        elif topic in FIN_TOPICS:
            pool = [x for x in a["contacts"] if x["start"] <= d and (x["end"] is None or x["end"] > d) and x["dept"] in ("Finance", "Procurement", "Executive")] or cs
        elif topic in ("exec_change", "qbr_review", "budget_planning", "m_and_a_integration"):
            pool = [x for x in cs if x["level"] in ("C-Level", "VP", "Director")] or cs
        else:
            pool = cs
        if c not in pool:
            c = TX.RT.choice(pool)
    c2 = R.choice(cs) if cs else c
    _, idates, iass, sdates, sass, scum = _acache(a)
    ki, ks = _bis.bisect_right(idates, d), _bis.bisect_right(sdates, d)
    infra = iass[:ki] if ki < 50 else [iass[R.randrange(ki)] for _ in range(3)]
    stor = sass[:ks] if ks < 50 else [sass[R.randrange(ks)] for _ in range(3)]
    nserv = scum[ki - 1] if ki else 0
    p = (o["lines"][0]["p"] if o else None)
    se = W.owner_on(a, d, "SA")
    old = a.get("_prev_owner_name")
    f = fy(d)
    sl = TX.make_slots(account=a["view"].crm_name(d) if chance(.7) else a["base_name"], contact_first=c["first"] if c else "", contact_last=c["last"] if c else "",
                       contact_name=f"{c['first']} {c['last']}" if c else "", contact_title=c["title"] if c else "",
                       contact2_name=f"{c2['first']} {c2['last']}" if c2 else "", contact2_title=c2["title"] if c2 else "",
                       rep_first=rep["person"]["first"] if rep else "", rep_name=stint_name(rep) if rep else "",
                       se_name=stint_name(se) if se else R.choice(["the SE", "our SA", "Marco (SA)", "presales"]), old_rep=old or "the previous rep",
                       partner=(W.partner_on(a, d) or {}).get("base_name", "the partner"), competitor=a["env"]["primary_competitor"],
                       product=p["name"] if p else "", product_line=(p["family"] if p else ""),
                       infra_product=(R.choice(infra)["p"]["name"] if infra else "Atlas 240 G4 Base"),
                       storage_product=(R.choice(stor)["p"]["line"] if stor else "Strata 500"),
                       seats=f"{a['emp'][f]:,}", servers=str(nserv or R.randint(4, 40)),
                       amount=money(o["sub"]) if o else money(R.choice([25000, 60000, 140000, 380000])),
                       budget=money(a["itb"][f] * R.uniform(.05, .2)), qty=str(o["lines"][0]["qty"]) if o else str(R.randint(10, 300)),
                       date=TX.nice_date(d + D(R.randint(3, 20))), quarter=f"Q{fq(d)}", fy=f"FY{f}",
                       po_number=(o["po"] if o and o.get("po") else ""), order_number=o["on"] if o else "", quote_number=(o or {}).get("quote_no") or "",
                       site_city=R.choice(a["sites"])["city"][2], hq_city=a["city"][2], os="Windows 11" if f >= 25 else "Windows 10",
                       hypervisor=a["env"]["hypervisor"], cloud=a["env"]["cloud"], initiative=(R.choice(a["inits"][f]) if a["inits"].get(f) else "refresh planning"),
                       discount=str(int(o["disc"] * 100)) if o and o["disc"] < 1 else "")
    if a.get("new_exec"):
        sl["new_exec"] = f"{a['new_exec'][1]['first']} {a['new_exec'][1]['last']}"
        sl["exec_title"] = a["new_exec"][1]["title"]
    if extra:
        sl.update({k: str(v) for k, v in extra.items()})
    return sl, c


# ------------------------------------------------------------------ opportunities
def opp_name(a, cat, o, persona, d):
    short = a["base_name"]
    g = SC.GROUP_NAME[cat]
    if persona in ("sloppy", "non_logger") and chance(.5):
        return R.choice([f"{short} - {g.lower()}", f"{short} Q{fq(d)}", f"{short} deal", f"{short} - refresh?", f"{short.upper()} {g}",
                         f"{short} {o['lines'][0]['p']['line'] if o else g}", "New Opportunity", f"{short} - FY{fy(d)}"])
    if o:
        l0 = o["lines"][0]
        return f"{short} - {l0['p']['line']} x{l0['qty']} - FY{fy(d)} Q{fq(d)}"
    return f"{short} - {g} - FY{fy(d)} Q{fq(d)}"


def cycle_days(amount):
    med = 10 if amount < 10000 else 28 if amount < 50000 else 55 if amount < 250000 else 95 if amount < 1e6 else 150
    return int(clip(lognorm(med, .5), 2, 400))


def make_opp(a, d_close, cat, amount, rep, outcome, o=None, created=None, comp=None, partner=None, otype=None, stale=False):
    """outcome: won/lost/open."""
    persona = rep["person"]["persona"] if rep else "by_the_book"
    created = created or bday_back(d_close - D(cycle_days(amount)))
    created = max(created, WIN_START - D(R.randint(0, 40))) if created < WIN_START else created
    if created > SNAP:   # deal with a far-out close date: it was still created before the snapshot
        created = bday_back(SNAP - D(1 + (created - SNAP).days % 45))
    oid = sfid("006")
    f = fy(d_close)
    owner_label = ROLE_LABEL.get(rep["role"], rep["role"]) if rep else "House"
    otype = otype or ("New Business" if a.get("_first_in_window") else "Existing Business")
    pushes = poisson({"happy_ears": 1.6, "sloppy": 1.4, "sandbagger": .4}.get(persona, .7))
    orig_close = d_close - D(pushes * R.randint(14, 40)) if pushes else d_close
    cur = a["currency"]
    rate = SC.fx(d_close) if cur == "CAD" else 1
    amt_rec = round(amount * rate, 2)
    if outcome == "won":
        stage, prob, fc, closed, won = "Closed Won", 100, "Closed", True, True
    elif outcome == "lost":
        stage, prob, fc, closed, won = "Closed Lost", 0, "Omitted", True, False
    else:
        k = R.randint(0, 4)
        stage, prob, fc = STAGES[k]
        closed = won = False
    if fy(created) < 24 and stage in LEGACY_STAGE and chance(.5):
        stage_rec = LEGACY_STAGE[stage]        # pre-FY24 picklist values survived the stage redesign
    else:
        stage_rec = stage
    reason = None
    if outcome == "lost":
        reason = wpick({"Lost to Competitor": 34, "No Decision / Status Quo": 22, "Price": 18, "Budget Cut / Freeze": 10, "Timing - Pushed to Next FY": 8,
                        "Moved to Public Cloud": 4, "Lost to Partner (channel conflict)": 2, "Product Gap": 2})
    dr = None
    if partner:
        dr = deal_reg(a, partner, created, amount, cat, oid, outcome)
    row = dict(Id=oid, Name=opp_name(a, cat, o, persona, d_close), AccountId=a.get("_opp_acct_override") or a["id"],
               End_Customer_Account__c=a["id"] if partner else None, OwnerId=rep["person"]["id"] if rep else None, Owner_Role__c=owner_label,
               Type=otype, Product_Group__c=SC.GROUP_NAME[cat], StageName=stage_rec, Amount=amt_rec if not (persona == "sloppy" and chance(.05)) else 0,
               CurrencyIsoCode=cur, Probability=prob, ForecastCategoryName=fc, CloseDate=ds(d_close), IsClosed=tf(closed), IsWon=tf(won),
               LeadSource=R.choice(["Rep Generated", "Rep Generated", "Customer Request", "Partner", "Marketing - Event", "Marketing - Web", "Install Base Renewal"]),
               CampaignId=None, Partner_Account__c=partner["id"] if partner else None, Deal_Registration__c=dr,
               Primary_Competitor__c=comp, Loss_Reason__c=reason, Next_Step__c=None if closed else TX.topic_text(TOPIC_OF[cat], "next_steps", slots_for(a, SNAP)[0], persona)[:250],
               Push_Count__c=pushes, Original_Close_Date__c=ds(orig_close), Sales_Motion__c=(o or {}).get("channel") or ("Partner" if partner else "Direct"),
               Fiscal_Quarter__c=f"FY{f} Q{fq(d_close)}", ERP_Order_Number__c=o["on"] if o and not o.get("opp_missing_link") else None,
               Description=None, CreatedDate=ts(created), CreatedById=rep["person"]["id"] if rep else None,
               LastModifiedDate=ts(max(created, min(SNAP, d_close + D(R.randint(0, 20))))) if closed else ts(max(created, SNAP - D(R.randint(0, 60)))))
    if stale:
        row["Description"] = None
        O.issue("stale_open_opportunity", "Opportunity", oid, "CloseDate", ds(d_close), "(update or close)", a["id"],
                "IsClosed=false and CloseDate < snapshot", "Open opportunity with a close date in the past.", "Low")
    if row["Amount"] == 0 and outcome == "won":
        O.issue("zero_amount_won_opportunity", "Opportunity", oid, "Amount", 0, amt_rec, a["id"], "Closed Won with Amount 0",
                "Rep never updated amount; order exists in ERP.")
    if stage_rec != stage:
        O.issue("legacy_picklist_value", "Opportunity", oid, "StageName", stage_rec, stage, a["id"], "StageName not in current picklist",
                "Pre-FY24 stage name survived the sales-process redesign.", "Low")
    if o is None and outcome == "won" and not a.get("_no_po_logged"):
        O.issue("won_opportunity_without_order", "Opportunity", oid, "ERP_Order_Number__c", None, "(no order booked)", a["id"],
                "Closed Won with no matching Sales_Order", "Customer verbally committed; PO never arrived so nothing was booked.", "High")
    O.add("Opportunity", row)
    # history
    path = STAGES[:R.randint(2, 5)] if outcome == "lost" else STAGES if outcome == "won" else STAGES[:STAGES.index((stage, prob, fc)) + 1]
    span = max(1, ((d_close if closed else min(SNAP, d_close)) - created).days)
    est = amount * (R.uniform(1.1, 1.6) if persona == "happy_ears" else R.uniform(.8, 1.3))
    for i, (sn, pr, fcat) in enumerate(path):
        sd = created + D(int(span * i / (len(path) + 1)))
        if sd > SNAP:
            break
        O.add("OpportunityHistory", dict(Id=sfid("008"), OpportunityId=oid, StageName=sn, Amount=round((est if i < 3 else amount) * rate, 2),
                                         CloseDate=ds(orig_close if i < 2 else d_close), Probability=pr, ForecastCategory=fcat,
                                         CreatedDate=ts(sd), CreatedById=row["CreatedById"]))
    if closed:
        O.add("OpportunityHistory", dict(Id=sfid("008"), OpportunityId=oid, StageName=stage, Amount=amt_rec, CloseDate=ds(d_close), Probability=prob,
                                         ForecastCategory=fc, CreatedDate=ts(d_close), CreatedById=row["CreatedById"]))
    # team + splits
    team = [(rep, owner_label)] if rep else []
    ae = W.owner_on(a, created)
    if ae and rep and ae is not rep:
        team.append((ae, "Account Owner"))
    for lab in ("SA", "LE_IAE", "TAM"):
        s = W.owner_on(a, created, lab)
        if s and s is not rep and (lab != "TAM" or cat in ("server", "storage")) and (lab != "SA" or cat not in ("client", "software")):
            team.append((s, ROLE_LABEL[lab]))
    if partner:
        pam = next((s for s in W.STINTS if s["role"] == "PAM" and stint_active(s, created)), None)
        if pam:
            team.append((pam, "Partner Account Manager"))
    seen = set()
    for s, lab in team:
        if id(s) in seen:
            continue
        seen.add(id(s))
        O.add("OpportunityTeamMember", dict(Id=sfid("00q"), OpportunityId=oid, UserId=s["person"]["id"], TeamMemberRole=lab))
    if rep:
        if ae and ae is not rep:
            O.add("OpportunitySplit", dict(Id=sfid("149"), OpportunityId=oid, SplitOwnerId=ae["person"]["id"], SplitType="Revenue", SplitPercentage=100, SplitAmount=amt_rec))
            O.add("OpportunitySplit", dict(Id=sfid("149"), OpportunityId=oid, SplitOwnerId=rep["person"]["id"], SplitType="Overlay", SplitPercentage=100, SplitAmount=amt_rec))
            if chance(.03):
                O.add("OpportunitySplit", dict(Id=sfid("149"), OpportunityId=oid, SplitOwnerId=rep["person"]["id"], SplitType="Revenue", SplitPercentage=50, SplitAmount=round(amt_rec / 2, 2)))
                O.issue("split_over_allocated", "OpportunitySplit", oid, "SplitPercentage", 150, 100, a["id"], "Revenue splits sum > 100%",
                        "Specialist added a revenue split on top of the AE's 100%.", "Medium")
        else:
            O.add("OpportunitySplit", dict(Id=sfid("149"), OpportunityId=oid, SplitOwnerId=rep["person"]["id"], SplitType="Revenue", SplitPercentage=100, SplitAmount=amt_rec))
        key = rep["person"]["id"]
        if outcome == "won":
            REP_STATS[key][(fy(d_close), fq(d_close), "won")] += amount
        if outcome == "open" or (outcome != "lost" and d_close > SNAP - D(90)):
            REP_STATS[key][(fy(d_close), fq(d_close), "pipe")] += amount
        REP_STATS[key]["persona"] = persona
        REP_STATS[key]["role"] = rep["role"]
    # quotes
    lines = o["lines"] if o else SC.RECIPES[cat](a, amount, min(d_close, SNAP), .15)
    for l in lines:
        O.add("OpportunityLineItem", dict(Id=sfid("00k"), OpportunityId=oid, Product2Id=l["p"]["Id"], ProductCode=l["p"]["sku"], Name=l["p"]["name"],
                                          Quantity=l["qty"], ListPrice=round(l["list"] * rate, 2), UnitPrice=round(l["unit"] * rate, 2),
                                          Discount=l["disc"], TotalPrice=round(l["qty"] * l["unit"] * rate, 2)))
    if amount > 4000:
        quotes(a, row, o, cat, amount, created, d_close, outcome, rep, lines)
    O.view.event(a, created, "CRM", "Opportunity Created", SC.GROUP_NAME[cat], record_table="Opportunity", record_id=oid, rep=rep,
                 opportunity_id=oid, amount=amt_rec, currency=cur, amount_usd=round(amount, 2), stage=path[0][0], subject=row["Name"],
                 partner_name=partner["base_name"] if partner else None, product_category=SC.GROUP_NAME[cat])
    if closed:
        O.view.event(a, d_close, "CRM", "Opportunity Closed", stage, record_table="Opportunity", record_id=oid, rep=rep, opportunity_id=oid,
                     amount=amt_rec, currency=cur, amount_usd=round(amount, 2), stage=stage, status=reason, subject=row["Name"],
                     details=dict(competitor=comp, pushes=pushes, original_close=ds(orig_close), cycle_days=(d_close - created).days, deal_reg=dr))
    return row, created


def deal_reg(a, partner, created, amount, cat, oid, outcome):
    did = sfid("a01")
    sub = created - D(R.randint(0, 25))
    status = "Approved" if chance(.8) else R.choice(["Rejected", "Expired", "Pending"])
    name_sub = R.choice([a["legal"], a["base_name"], a["base_name"].upper(), a["base_name"] + " Corp", a["legal"].replace(".", "")])
    O.add("Deal_Registration__c", dict(Id=did, Name=f"DR-{seq('dr', 200000, 3)}", Partner_Account__c=partner["id"], End_Customer_Account__c=a["id"] if chance(.7) else None,
                                       End_Customer_Name_As_Submitted__c=name_sub, Opportunity__c=oid, Product_Group__c=SC.GROUP_NAME[cat],
                                       Est_Value__c=human_round(amount * R.uniform(.8, 1.5)), Submitted_Date__c=ds(sub), Status__c=status,
                                       Decision_Date__c=ds(sub + D(R.randint(1, 10))) if status != "Pending" else None,
                                       Expiration_Date__c=ds(sub + D(90)), Rejection_Reason__c="Direct opportunity already open" if status == "Rejected" else None,
                                       Partner_Rep_Name__c=" ".join(W.person())))
    if chance(.06):   # a second partner registers the same deal -> conflict
        other = R.choice([p for p in W.PARTNERS if p is not partner])
        d2 = sfid("a01")
        O.add("Deal_Registration__c", dict(Id=d2, Name=f"DR-{seq('dr', 200000, 3)}", Partner_Account__c=other["id"], End_Customer_Account__c=None,
                                           End_Customer_Name_As_Submitted__c=a["base_name"], Opportunity__c=None, Product_Group__c=SC.GROUP_NAME[cat],
                                           Est_Value__c=human_round(amount), Submitted_Date__c=ds(sub + D(R.randint(1, 20))), Status__c="Rejected",
                                           Decision_Date__c=ds(sub + D(25)), Expiration_Date__c=ds(sub + D(110)),
                                           Rejection_Reason__c="Duplicate registration - another partner registered first", Partner_Rep_Name__c=" ".join(W.person())))
        O.issue("channel_conflict_duplicate_registration", "Deal_Registration__c", d2, "End_Customer_Account__c", None, a["id"], a["id"],
                "Two partners registered the same end customer/project", f"{other['base_name']} and {partner['base_name']} both registered this deal.")
    return did


def quotes(a, opp, o, cat, amount, created, close, outcome, rep, lines):
    nv = 1 if amount < 20000 else R.randint(1, 4)
    cur = a["currency"]
    rate = SC.fx(close) if cur == "CAD" else 1
    persona = rep["person"]["persona"] if rep else "by_the_book"
    final_q = None
    for v in range(1, nv + 1):
        qd = created + D(int((close - created).days * v / (nv + 1)))
        if qd > SNAP:
            break
        qn = f"Q-{seq('q', 2_000_000, 3, 2)}"
        last = v == nv
        extra = (nv - v) * R.uniform(.02, .05)
        sub = sum(l["qty"] * l["list"] for l in lines)
        tot = sum(l["qty"] * l["unit"] for l in lines) * (1 + extra)
        cfg_err = None
        if cat in ("server", "storage") and chance(.06):
            cfg_err = R.choice(["PSU capacity insufficient for accelerator config", "Rail kit missing for 2U chassis", "Drive count exceeds backplane",
                                "Mixed DIMM speeds", "Warranty term mismatch vs. hardware", "NIC not supported on this riser"])
        status = ("Accepted" if outcome == "won" else "Rejected" if outcome == "lost" else "Presented") if last else "Superseded"
        if last and outcome == "lost" and chance(.4):
            status = "Expired"
        qid = sfid("0Q0")
        O.add("Quote", dict(Id=qid, QuoteNumber=qn, OpportunityId=opp["Id"], AccountId=a["id"], Version__c=v, Status=status, ExpirationDate=ds(qd + D(30)),
                            Subtotal=round(sub * rate, 2), Discount=round((1 - tot / sub) * 100, 1) if sub else 0, TotalPrice=round(tot * rate, 2),
                            CurrencyIsoCode=cur, Configuration_Validated__c=tf(cfg_err is None), Config_Error__c=cfg_err, CreatedDate=ts(qd),
                            CreatedById=rep["person"]["id"] if rep else None))
        if last and (outcome != "lost" or chance(.5)):
            for l in lines:
                up = round(l["unit"] * (1 + extra), 2)
                O.add("QuoteLineItem", dict(Id=sfid("0QL"), QuoteId=qid, Product2Id=l["p"]["Id"], ProductCode=l["p"]["sku"], Quantity=l["qty"],
                                            ListPrice=round(l["list"] * rate, 2), UnitPrice=round(up * rate, 2),
                                            Discount=round((1 - up / l["list"]) * 100, 1) if l["list"] else 0, TotalPrice=round(up * l["qty"] * rate, 2)))
        final_q = (qid, qn, tot)
        maxd = max((l["disc"] for l in lines), default=0)
        thr = (15 if fy(qd) < 25 else 12) if rep and rep["role"] in ("SB_REP", "MB_IAE", "LE_IAE") else (25 if fy(qd) < 25 else 20)
        if last and maxd > thr:
            missing = chance(.35 if persona == "discounter" else .08)
            if missing:
                O.issue("discount_without_approval", "Quote", qid, "Discount", maxd, f"<= {thr}% without approval", a["id"],
                        "Quote discount above policy threshold and no Discount_Approval__c", "Discount exceeded policy without a recorded approval.", "High")
            else:
                lvl = "Manager" if maxd <= thr + 10 else "Deal Desk" if maxd <= thr + 20 else "VP Sales"
                O.add("Discount_Approval__c", dict(Id=sfid("a02"), Opportunity__c=opp["Id"], Quote__c=qid, Requested_By__c=rep["person"]["id"] if rep else None,
                                                   Approver__c=lvl, Approval_Level__c=lvl, Requested_Discount_Pct__c=maxd, Policy_Threshold_Pct__c=thr,
                                                   Status__c="Approved" if chance(.88) else "Rejected",
                                                   Justification__c=R.choice(["Competitive - " + a["env"]["primary_competitor"] + " quote in hand", "Quarter-end volume", "Strategic logo",
                                                                              "Match contract pricing", "Multi-year commitment", "Customer budget cap", "Displace incumbent",
                                                                              "pls approve, need this by EOQ"]),
                                                   Requested_Date__c=ds(qd), Decision_Date__c=ds(qd + D(R.randint(0, 4)))))
    if o and final_q:
        o["quote_no"] = final_q[1]


def pipeline(a, orders):
    """Opportunities for orders (won), lost deals, open pipeline, stale and no-PO wins."""
    seg_end = a["seg_end"]
    first_win = True
    for o in orders:
        d = o["d"]
        if o["channel"] == "Online Store" and not chance(.08):
            continue
        if o["sub"] < 3000 and a["seg"][o["fy"]] == "Small Business" and not chance(.3):
            continue
        if o["channel"] == "Premier Portal" and chance(.7):
            continue
        if chance(.07):
            o["opp_missing_link"] = True
        a["_first_in_window"] = first_win and not a.get("legacy")
        otype = "New Business" if a["_first_in_window"] else ("Existing Business - Warranty Renewal" if o["lines"][0]["p"]["category"] == "Support Services" else
                                                             R.choice(["Existing Business - Expansion", "Existing Business - Refresh", "Existing Business - Run Rate"]))
        comp = a["env"]["primary_competitor"] if o["competitive"] else None
        row, created = make_opp(a, d if o["status"] != "Cancelled" else d, o["cat"], o["sub"], o["rep"], "won", o, comp=comp,
                                partner=o["partner"], otype=otype)
        o["opp"] = row
        o["opp_created"] = created
        if o.get("opp_missing_link"):
            O.issue("order_not_linked_to_opportunity", "Sales_Order", o["on"], "CRM_Opportunity_Id", None, row["Id"], a["id"],
                    "Match on account, amount and date", "ERP order is missing the CRM opportunity reference.", "Low")
        first_win = False
        # lost deals around the same need
        lost_rate = {"client": .45, "workstation": .4, "server": .9, "storage": 1.0, "data_protection": .8, "networking": .6, "software": .2, "services": .3}[o["cat"]]
        for _ in range(poisson(lost_rate * (.6 if seg_end == "Small Business" else 1))):
            ld = rand_bday(max(WIN_START, d - D(300)), min(SNAP, d + D(300)))
            make_opp(a, ld, o["cat"], o["sub"] * R.uniform(.5, 1.8), o["rep"] or W.owner_on(a, ld), "lost",
                     comp=wpick(RD.COMPETITORS) if chance(.6) else None, partner=W.partner_on(a, ld) if chance(.3) else None)
    # never-bought / lapsed accounts still get pipeline that goes nowhere
    if a["status_end"] in ("never", "lapsed", "development"):
        n = {"never": R.randint(0, 4), "lapsed": R.randint(0, 2), "development": R.randint(0, 3)}[a["status_end"]]
        for _ in range(n):
            ld = rand_bday(WIN_START + D(30), SNAP + D(120))
            cat = wpick(a["mix"])
            amt = SC.AVG_ORDER[cat][a["seg"][fy(min(ld, SNAP))]] * lognorm(1, .6)
            rep = W.owner_on(a, min(ld, SNAP))
            outcome = "open" if ld > SNAP else "lost"
            if outcome == "open" and a.get("showcase") == "ai_reacquisition":
                cat, amt = "server", 640000
            make_opp(a, ld, cat, amt, rep, outcome, comp=wpick(RD.COMPETITORS) if chance(.6) else None)
    # open pipeline for active buyers (next two quarters) + stale + won-without-PO
    if a.get("showcase") == "ai_reacquisition":
        own = W.owner_on(a, dt.date(2025, 11, 3))
        make_opp(a, dt.date(2026, 4, 24), "server", 640_000, own, "open", created=dt.date(2025, 11, 3), comp="Public cloud")
    if a.get("champion"):
        ch, new, dest, repl = a["champion"]
        own = W.owner_on(a, dt.date(2025, 5, 1))
        row, _ = make_opp(a, dt.date(2026, 3, 27), "server", 1_240_000, own, "open", created=dt.date(2025, 4, 22))
        a["champion_opp"] = row["Id"]
        sl, _ = slots_for(a, dt.date(2025, 7, 30), rep=own)
        for d, body in ((dt.date(2025, 7, 30), f"heads up - {ch['first']} {ch['last']} ({ch['title']}) resigned, last day was 7/18. they were our sponsor on the $1.2M data center refresh. nobody has told procurement who owns the decision now. @{sl['se_name']} can you check if the infra mgr is still engaged?"),
                        (dt.date(2025, 9, 9), f"FYI {ch['first']} {ch['last']} just showed up as CIO at {dest['base_name']}. could be a door opener there. meanwhile our deal here is stalled until they backfill."),
                        (dt.date(2025, 10, 20), f"new {repl['title']} {repl['first']} {repl['last']} started 10/6. first intro call booked. they want to 're-baseline all vendor commitments' - expect the refresh to slip to next FY")):
            fid = sfid("0D5")
            O.add("FeedItem", dict(Id=fid, ParentId=a["id"], CreatedById=own["person"]["id"] if own else None, Body=body, Type="TextPost", CreatedDate=ts(d)))
            O.view.event(a, d, "CRM", "Chatter Post", "champion_change", record_table="FeedItem", record_id=fid, rep=own, text=body)
    if a["status_end"] == "retention":
        recent = [o for o in orders if o["d"] > SNAP - D(180)]
        k = min(40, max(1, int(len(recent) * R.uniform(.25, .6))))
        for o in R.sample(recent, min(k, len(recent))):
            cd = rand_bday(SNAP + D(5), SNAP + D(180))
            rep = W.owner_on(a, SNAP) if o["cat"] == "client" else (o["rep"] if o["rep"] and stint_active(o["rep"], SNAP) else W.owner_on(a, SNAP))
            make_opp(a, cd, o["cat"], o["sub"] * R.uniform(.6, 1.6), rep, "open", created=rand_bday(SNAP - D(120), SNAP - D(1)),
                     partner=W.partner_on(a, SNAP) if chance(.2) else None)
        if chance(.18) and recent:
            o = R.choice(recent)
            make_opp(a, rand_bday(SNAP - D(160), SNAP - D(5)), o["cat"], o["sub"], W.owner_on(a, SNAP - D(10)), "open",
                     created=SNAP - D(R.randint(150, 300)), stale=True)
        if chance(.03) or a.get("showcase") == "missed_po_credit_hold":
            o = R.choice(recent) if recent else None
            if o:
                make_opp(a, rand_bday(SNAP - D(120), SNAP - D(20)), o["cat"], o["sub"] * 1.4, W.owner_on(a, SNAP - D(20)), "won")


# ------------------------------------------------------------------ activities
DISP = {"connected": 38, "left_voicemail": 32, "no_answer": 14, "gatekeeper": 5, "meeting_booked": 4, "callback_requested": 4,
        "not_interested": 1.5, "wrong_number": 1, "bad_number": .5}
RATE = {"Small Business": .45, "Medium Business": 1.6, "Large Enterprise": 4.2, "Select": 11}
PERSONA_RATE = {"non_logger": .12, "sloppy": .55, "star": 1.45, "happy_ears": 1.1, "bulk_logger": .9}


def context_topics(a, d, orders_by_month):
    t = []
    m = (d.year, d.month)
    for o in orders_by_month.get(m, []):
        t.append((TOPIC_OF[o["cat"]], o))
        if o.get("hold") and o["hold"] == "Awaiting PO":
            t += [("po_followup", o)] * 3
        if o.get("credit_hold"):
            t += [("credit_hold_collections", o)] * 2
        if o["channel"] == "Partner" and chance(.2):
            t.append(("partner_conflict", o))
        if o["cat"] == "server" and any(l["p"]["category"] == "AI Servers" for l in o["lines"]):
            t += [("ai_gpu_initiative", o)] * 2
        if o["cat"] == "server" and any(l["p"]["category"] == "HCI" for l in o["lines"]):
            t.append(("hci_virtualization", o))
        if SC.SHORTAGE[0] <= o["d"] <= SC.SHORTAGE[1] and o["cat"] in ("server", "storage", "client"):
            t.append(("order_status_delay", o))
    f = fy(d)
    for x in a["inits"].get(f, []):
        k = {"Windows 11 migration": "win11_migration", "AI pilot": "ai_gpu_initiative", "AI production rollout": "ai_gpu_initiative",
             "VMware exit / hypervisor change": "hci_virtualization", "Ransomware resilience": "data_protection", "Storage consolidation": "storage_capacity",
             "Edge / IoT rollout": "edge_deployment", "Network modernization": "networking_upgrade", "Cost reduction program": "layoffs_cost_cutting",
             "M&A integration": "m_and_a_integration", "New site build-out": "expansion_new_site"}.get(x)
        if k:
            t.append((k, None))
    for nd, nt in a["news"]:
        if 0 <= (d - nd).days <= 75:
            k = {"exec_hire": "exec_change", "acquisition": "m_and_a_integration", "acquired": "m_and_a_integration", "layoffs": "layoffs_cost_cutting",
                 "expansion": "expansion_new_site", "funding": "budget_planning"}.get(nt)
            if k:
                t += [(k, None)] * 3
    if a.get("_handoff") and 0 <= (d - a["_handoff"]).days <= 45:
        t += [("rep_handoff", None)] * 4
    if d.month == ((a["fye_month"]) % 12) + 1 or d.month == a["fye_month"]:
        t.append(("budget_planning", None))
    for ln, s, e, units, fin in a.get("leases", []):
        if 0 <= (e - d).days <= 200:
            t += [("lease_end", None)] * 3
    if a.get("_exp_warranty", {}).get(m):
        t += [("warranty_renewal", None)] * 2
    if a.get("_adv_month", {}).get(m):
        t += [("security_advisory", None)] * 3
    if a.get("flex_contract") and chance(.15):
        t.append(("consumption_billing", None))
    if chance(.08):
        t.append(("competitor_threat", None))
    if a["seg"][f] == "Small Business":
        t.append(("small_business_purchase", None))
    if not t:
        t = [("relationship_check_in", None), ("qbr_review", None) if a["seg"][f] in ("Large Enterprise", "Select") else ("relationship_check_in", None)]
    return t


def activities(a, orders):
    obm = defaultdict(list)
    for o in orders:
        obm[(o["d"].year, o["d"].month)].append(o)
        if o.get("opp_created"):
            obm[(o["opp_created"].year, o["opp_created"].month)].append(o)
    # warranty expirations by month (signals)
    ew = defaultdict(int)
    for x in a.get("assets", []):
        if x["wend"] and WIN_START <= x["wend"] <= SNAP + D(120):
            ew[((x["wend"] - D(90)).year, (x["wend"] - D(90)).month)] += x["qty"]
    a["_exp_warranty"] = ew
    if a["first_buy"] is None and a["status_end"] == "never":
        start = WIN_START + D(R.randint(0, 900))
    else:
        start = WIN_START
    m = month_start(start)
    prev_owner = None
    while m <= SNAP:
        f = fy(m)
        seg = a["seg"][f]
        own = W.owner_on(a, m + D(14))
        if own is not prev_owner and prev_owner is not None and own is not None:
            a["_handoff"] = m + D(R.randint(0, 20))
            a["_prev_owner_name"] = stint_name(prev_owner)
            handoff_chatter(a, m, own, prev_owner)
        prev_owner = own or prev_owner
        engaged = W.buying(a, m) or W.buying(a, m + D(200)) or a["status_end"] == "never" or chance(.3)
        reps = [(own, "OWNER")] if own else []
        for lab in ("LE_IAE", "SA", "TAM", "OV_SERVER", "OV_STORAGE", "MB_SPEC_CLIENT", "MB_SPEC_INFRA", "OV_SVC", "SDM"):
            s = W.owner_on(a, m + D(14), lab)
            if s:
                reps.append((s, lab))
        for rep, lab in reps:
            base = RATE[seg] * (1 if lab == "OWNER" else .35) * (1 if engaged else .25)
            n = poisson(base * PERSONA_RATE.get(rep["person"]["persona"], 1))
            topics = context_topics(a, m + D(14), obm)
            for _ in range(n):
                d = rand_bday(m, min(SNAP, add_months(m, 1) - D(1)))
                topic, o = R.choice(topics)
                if lab in ("SA", "OV_SERVER", "OV_STORAGE", "MB_SPEC_INFRA", "TAM") and topic in ("client_refresh", "win11_migration", "small_business_purchase"):
                    topic = R.choice(["server_refresh", "storage_capacity", "data_protection", "hci_virtualization"])
                one_activity(a, d, rep, topic, o)
        # meetings
        if seg in ("Large Enterprise", "Select") and own and W.buying(a, m) and m.month in ((a["fye_month"] + 2) % 12 + 1, (a["fye_month"] + 5) % 12 + 1,
                                                                                              (a["fye_month"] + 8) % 12 + 1, (a["fye_month"] + 11) % 12 + 1):
            if seg == "Select" or chance(.45):
                meeting(a, rand_bday(m, min(SNAP, m + D(27))), own, "qbr", None)
        if own and m.month == 2 and seg in ("Large Enterprise", "Select") and (W.buying(a, m) or chance(.3)):
            account_plan(a, rand_bday(m, m + D(40)), own)
        m = add_months(m, 1)
    # opportunity meetings + win/loss notes
    for o in orders:
        if o.get("opp") and o["sub"] > 100000 and o.get("opp_created"):
            span = (o["d"] - o["opp_created"]).days
            types = ["discovery", "product_demo", "technical_deep_dive", "proposal_review", "negotiation"]
            R.shuffle(types)
            types = sorted(types[:R.randint(1, 3)], key=["discovery", "product_demo", "technical_deep_dive", "proposal_review", "negotiation"].index)
            if o["cat"] in ("server", "storage", "data_protection"):
                types.insert(3, "architecture_workshop")
            if o["sub"] > 500000:
                types.insert(1, "executive_briefing")
            for i, t in enumerate(types[: R.randint(1, len(types))]):
                d = bday(o["opp_created"] + D(int(span * (i + .5) / len(types))))
                if d <= SNAP:
                    meeting(a, d, o["rep"] or W.owner_on(a, d), t, o)
            if o["sub"] > 150000 and chance(.4) and o["rep"]:
                sl, c = slots_for(a, o["d"], rep=o["rep"], o=o)
                body = TX.pick(PB.WIN_NOTES, sl, o["cat"])
                note(a, o["opp"]["Id"], o["d"] + D(R.randint(1, 20)), o["rep"], f"Win review - {o['opp']['Name']}", body, "Win/Loss Review")


def one_activity(a, d, rep, topic, o):
    persona = rep["person"]["persona"]
    if persona == "bulk_logger" and chance(.7):
        d2 = d + D((4 - d.weekday()) % 7)
        logged = d2 if d2 <= SNAP else d
    else:
        logged = d
    sl, c = slots_for(a, d, rep=rep, o=o, topic=topic)
    who = c["id"] if c and not (c["end"] and c["end"] < d) else (c["id"] if c else None)
    if c and c["end"] and c["end"] < d:
        a["_left_contact_touch"] = a.get("_left_contact_touch", 0) + 1
    if chance(.55):
        disp = wpick(DISP)
        body = TX.call_log(topic, sl, persona, disp)
        dur = R.randint(25, 70) if disp in ("left_voicemail", "no_answer", "gatekeeper", "wrong_number", "bad_number") else R.randint(180, 3300)
        subj = TX.topic_text(topic, "subjects", sl, persona) if disp == "connected" else R.choice(["Call", "Outbound call", "Call - VM", f"Call {sl['contact_first']}", "Phone call"])
        direction = "Outbound" if chance(.82) else "Inbound"
        tid = sfid("00T")
        O.add("Task", dict(Id=tid, WhoId=who, WhatId=(o or {}).get("opp", {}).get("Id") if o and o.get("opp") else a["id"], AccountId=a["id"],
                           OwnerId=rep["person"]["id"], Subject=subj[:255], Description=body if persona != "non_logger" or chance(.3) else None,
                           TaskSubtype="Call", Type="Call", CallDurationInSeconds=dur, CallDisposition=disp.replace("_", " ").title(),
                           Call_Direction__c=direction, ActivityDate=ds(d), Status="Completed", Priority="Normal", Topic__c=topic,
                           CreatedDate=ts(logged)))
        O.view.event(a, d, "CRM", "Call", disp.replace("_", " ").title(), record_table="Task", record_id=tid, rep=rep, contact=c, subject=subj[:255],
                     text=body, details=dict(duration_sec=dur, direction=direction, topic=topic, logged_date=ds(logged) if logged != d else None),
                     opportunity_id=(o or {}).get("opp", {}).get("Id") if o and o.get("opp") else None, order_number=o["on"] if o else None)
    else:
        inbound = chance(.3)
        subj, body = TX.topic_text(topic, "emails_in" if inbound else "emails_out", sl, persona)
        tid = sfid("00T")
        O.add("Task", dict(Id=tid, WhoId=who, WhatId=a["id"], AccountId=a["id"], OwnerId=rep["person"]["id"], Subject=("RE: " if inbound and chance(.5) else "Email: ") + subj[:240],
                           Description=body, TaskSubtype="Email", Type="Email", Call_Direction__c="Inbound" if inbound else "Outbound",
                           ActivityDate=ds(d), Status="Completed", Priority="Normal", Topic__c=topic, CreatedDate=ts(logged)))
        O.view.event(a, d, "CRM", "Email", "Inbound" if inbound else "Outbound", record_table="Task", record_id=tid, rep=rep, contact=c,
                     subject=subj, text=body, details=dict(topic=topic))
    if chance(.04 if persona != "star" else .08):
        sl2, _ = slots_for(a, d, rep=rep, o=o)
        post = TX.topic_text(topic, "chatter", sl2, persona)
        fid = sfid("0D5")
        O.add("FeedItem", dict(Id=fid, ParentId=a["id"], CreatedById=rep["person"]["id"], Body=post, Type="TextPost", CreatedDate=ts(d)))
        O.view.event(a, d, "CRM", "Chatter Post", topic, record_table="FeedItem", record_id=fid, rep=rep, text=post)


def handoff_chatter(a, d, new, old):
    sl, _ = slots_for(a, d, rep=new)
    sl["old_rep"] = stint_name(old)
    post = TX.topic_text("rep_handoff", "chatter", sl, new["person"]["persona"])
    fid = sfid("0D5")
    O.add("FeedItem", dict(Id=fid, ParentId=a["id"], CreatedById=new["person"]["id"], Body=post, Type="TextPost", CreatedDate=ts(d)))
    O.view.event(a, d, "CRM", "Owner Change", "Rep handoff", record_table="FeedItem", record_id=fid, rep=new, text=post,
                 details=dict(previous_owner=stint_name(old), new_owner=stint_name(new)))


def meeting(a, d, rep, mtype, o):
    if rep is None or d > SNAP:
        return
    sl, c = slots_for(a, d, rep=rep, o=o)
    cs = [x for x in a["contacts"] if x["start"] <= d and (x["end"] is None or x["end"] > d) and not x["shared"]]
    att = [f"{x['first']} {x['last']} ({x['title']})" for x in R.sample(cs, min(len(cs), R.randint(1, 4)))]
    att += [f"{stint_name(rep)} (Orvane)"]
    se = W.owner_on(a, d, "SA")
    if se and mtype in ("technical_deep_dive", "architecture_workshop", "product_demo", "qbr"):
        att.append(f"{stint_name(se)} (Orvane SA)")
    title = {"discovery": "Discovery", "product_demo": "Demo", "technical_deep_dive": "Technical Deep Dive", "architecture_workshop": "Architecture Workshop",
             "executive_briefing": "Executive Briefing", "qbr": "Quarterly Business Review", "proposal_review": "Proposal Review",
             "negotiation": "Commercial Negotiation", "account_planning": "Account Planning"}[mtype]
    eid = sfid("00U")
    dur = R.choice([30, 45, 60, 60, 90, 120]) if mtype != "qbr" else R.choice([60, 90, 120])
    st = dt.datetime(d.year, d.month, d.day, R.randint(14, 21), R.choice([0, 0, 30]))
    loc = R.choice(["Zoom", "Microsoft Teams", "Teams", "Customer HQ - " + a["city"][2], "Orvane Executive Briefing Center", "Zoom", "Onsite"])
    body = TX.meeting_note(mtype, sl, att, rep["person"]["persona"], (o or {}).get("cat")) if (rep["person"]["persona"] != "non_logger" or chance(.25)) else None
    O.add("Event", dict(Id=eid, WhoId=c["id"] if c else None, WhatId=o["opp"]["Id"] if o and o.get("opp") else a["id"], AccountId=a["id"],
                        OwnerId=rep["person"]["id"], Subject=f"{title} - {a['base_name']}", Type="Meeting", StartDateTime=ts_dt(st),
                        EndDateTime=ts_dt(st + dt.timedelta(minutes=dur)), DurationInMinutes=dur, Location=loc, Attendees__c="; ".join(att),
                        Description=body, CreatedDate=ts(d - D(R.randint(1, 15)))))
    O.view.event(a, d, "CRM", "Meeting", title, record_table="Event", record_id=eid, rep=rep, contact=c, subject=f"{title} - {a['base_name']}",
                 text=body, details=dict(duration_min=dur, location=loc, attendees=att), opportunity_id=o["opp"]["Id"] if o and o.get("opp") else None)


def note(a, parent, d, rep, title, body, ntype):
    if d > SNAP:
        return
    nid = sfid("002")
    O.add("Note", dict(Id=nid, ParentId=parent, AccountId=a["id"], OwnerId=rep["person"]["id"] if rep else None, Title=title, Body=body,
                       Note_Type__c=ntype, CreatedDate=ts(d)))
    O.view.event(a, d, "CRM", "Note", ntype, record_table="Note", record_id=nid, rep=rep, subject=title, text=body)


def account_plan(a, d, rep):
    if d > SNAP:
        return
    sl, _ = slots_for(a, d, rep=rep)
    body = TX.account_plan(sl)
    note(a, a["id"], d, rep, f"FY{fy(d)} Account Plan - {a['base_name']}", body, "Account Plan")


# ------------------------------------------------------------------ support, telemetry, advisories
CASE_CATS = {"Notebooks": {"hardware_failure": 30, "battery_swelling": 15, "display_issue": 20, "doa": 5, "shipping_damage": 5, "warranty_question": 10, "config_help": 15},
             "Desktops": {"hardware_failure": 45, "doa": 8, "display_issue": 10, "config_help": 25, "warranty_question": 12},
             "Servers": {"hardware_failure": 35, "drive_failure": 25, "firmware_bug": 15, "performance": 15, "config_help": 10},
             "Storage": {"drive_failure": 35, "performance": 25, "firmware_bug": 20, "data_recovery": 10, "config_help": 10},
             "Networking": {"network_connectivity": 50, "firmware_bug": 30, "config_help": 20}}
CATMAP = {"Notebooks": "Notebooks", "Rugged": "Notebooks", "Consumer Notebooks": "Notebooks", "Desktops": "Desktops", "Thin Clients": "Desktops",
          "Workstations": "Desktops", "Servers": "Servers", "AI Servers": "Servers", "Modular": "Servers", "HCI": "Servers", "Edge": "Servers",
          "Storage": "Storage", "Data Protection": "Storage", "Networking": "Networking"}
CASE_CAP = {"Small Business": 3, "Medium Business": 8, "Large Enterprise": 24, "Select": 110}


def support(a):
    cases_per_fy = defaultdict(int)
    out = []
    for x in a.get("assets", []):
        cm = CATMAP.get(x["p"]["category"])
        if not cm:
            continue
        s = max(x["sd"], WIN_START)
        e = SNAP
        yrs = max(0, (e - s).days / 365)
        rate = (.03 * x["qty"]) if cm in ("Notebooks", "Desktops") else .18
        n = poisson(min(rate * yrs, 30))
        for _ in range(n):
            out.append((between(s, e), x, wpick(CASE_CATS[cm])))
    for f in W.FYS:
        if W.buying(a, fy_start(f) + D(100)) or chance(.2):
            for _ in range(poisson({"Small Business": .5, "Medium Business": 1.2, "Large Enterprise": 3, "Select": 10}[a["seg"][f]])):
                out.append((rand_bday(fy_start(f), min(SNAP, fy_end(f))), None, wpick({"billing_issue": 40, "software_licensing": 30, "warranty_question": 30})))
    out.sort(key=lambda z: z[0])
    for d, x, cat in out:
        f = fy(d)
        if cases_per_fy[f] >= CASE_CAP[a["seg"][f]] * R.uniform(.7, 1.3):
            continue
        cases_per_fy[f] += 1
        one_case(a, d, x, cat)


def one_case(a, d, x, cat):
    tier = (x["w"]["line"] if x and x.get("w") else "Base Warranty")
    sla = 4 if "Mission Critical" in tier else 24 if "ProCare" in tier else 72
    pri = wpick({"P1 - Critical": 6, "P2 - High": 22, "P3 - Medium": 50, "P4 - Low": 22}) if x and x["p"]["bu"] == "Infrastructure Solutions" else \
        wpick({"P2 - High": 10, "P3 - Medium": 60, "P4 - Low": 30})
    sev = {"P1 - Critical": "Severity 1", "P2 - High": "Severity 2", "P3 - Medium": "Severity 3", "P4 - Low": "Severity 4"}[pri]
    res = lognorm({"P1 - Critical": 9, "P2 - High": 26, "P3 - Medium": 70, "P4 - Low": 120}[pri], .8) * (1.3 if SC.SHORTAGE[0] <= d <= SC.SHORTAGE[1] else 1)
    closed = d + D(int(res // 24) + 1)
    status = "Closed" if closed <= SNAP else wpick({"Working": 40, "Waiting on Customer": 25, "Awaiting Parts": 20, "Escalated": 15})
    esc = pri.startswith("P1") and chance(.4) or chance(.06)
    cs = [c for c in a["contacts"] if c["start"] <= d and (c["end"] is None or c["end"] > d)] or a["contacts"][:1]
    c = R.choice(cs) if cs else None
    if c and c["shared"] and c["dept"] != "IT":
        tech = [z for z in cs if not z["shared"] and z["dept"] in ("IT", "Security", "Engineering", "Data & Analytics", "Operations", "Executive")]
        c = TX.RT.choice(tech) if tech else c
    sl, _ = slots_for(a, d, contact=c, extra=dict(model=x["p"]["name"] if x else "", firmware=x["fw"] or "" if x else "",
                                                 case_number=""))
    if x:
        sl["product"] = sl["infra_product"] = x["p"]["name"]
    n_com = R.randint(2, 6) if pri.startswith(("P1", "P2")) else R.randint(1, 3)
    subj, comments = TX.case_text(cat, sl, n_com, TX.CASE_AREA.get(CATMAP.get(x["p"]["category"])) if x else None)
    cid = sfid("500")
    cnum = f"C-{seq('case', 7_000_000, 13, 9):08d}"
    disp = "Onsite Technician" if cat in ("hardware_failure", "drive_failure") and "NBD" in tier or "Mission" in tier and cat in ("hardware_failure", "drive_failure") else \
        "Parts Only" if cat in ("hardware_failure", "drive_failure", "battery_swelling", "display_issue") else "Remote" if cat in ("firmware_bug", "performance", "config_help", "network_connectivity") else None
    sup = next((s for s in R.sample(W.STINTS, min(60, len(W.STINTS))) if s["role"] == "SUPPORT" and stint_active(s, d)), None) or \
        next((s for s in W.STINTS if s["role"] == "SUPPORT"), None)
    O.add("Case", dict(Id=cid, CaseNumber=cnum, AccountId=a["id"], ContactId=c["id"] if c else None, AssetId=x["id"] if x else None,
                       Asset_Serial__c=x["sn"] if x else None, Product__c=x["p"]["name"] if x else None, OwnerId=sup["person"]["id"] if sup else None,
                       Subject=subj[:255], Description=comments[0] if comments else subj, Category__c=cat.replace("_", " ").title(), Priority=pri, Severity__c=sev,
                       Origin=wpick({"Phone": 35, "Web": 25, "Email": 20, "Chat": 12, "Proactive (Telemetry)": 8 if x and x["p"]["serialized"] else 0}),
                       Status=status, IsEscalated=tf(esc), Dispatch_Type__c=disp, Parts_Dispatched__c=f"PN {R.choice('0123456789ABCDEFGHJKMNPRTVWXY')}{R.randint(1, 9)}{R.choice('ABCDEFGHJKMNPRTVWXY')}{R.randint(10, 99)}" if disp in ("Onsite Technician", "Parts Only") else None,
                       SLA_Hours__c=sla, Resolution_Hours__c=round(res, 1) if status == "Closed" else None, SLA_Met__c=tf(res <= sla * 1.5) if status == "Closed" else None,
                       CreatedDate=ts(d, 0, 23), ClosedDate=ts(closed) if status == "Closed" else None))
    for i, cm in enumerate(comments):
        cd = d + D(int(i * max(1, (min(closed, SNAP) - d).days) / max(1, len(comments))))
        O.add("CaseComment", dict(Id=sfid("00a"), ParentId=cid, CommentBody=cm, IsPublished=tf(chance(.6)), CreatedById=sup["person"]["id"] if sup else None,
                                  Author_Type__c="Support Engineer" if i % 2 == 0 or chance(.3) else "Customer", CreatedDate=ts(cd)))
    O.view.event(a, d, "Support", "Support Case", cat.replace("_", " ").title(), record_table="Case", record_id=cid, case_number=cnum, contact=c,
                 product=x["p"] if x else None, asset_serial=x["sn"] if x else None, status=status, subject=subj, text="\n---\n".join(comments),
                 details=dict(priority=pri, sla_hours=sla, resolution_hours=round(res, 1) if status == "Closed" else None, escalated=esc, warranty_tier=tier))
    if status == "Closed" and chance(.3):
        good = res <= sla * 1.5 and not esc
        nps = R.randint(8, 10) if good and chance(.7) else R.randint(5, 8) if good else R.randint(0, 6)
        band = "promoter" if nps >= 9 else "passive" if nps >= 7 else "detractor"
        verb = TX.pick(PB.SURVEY_VERBATIMS[band], sl) if chance(.6) else None
        sid = sfid("a05")
        O.add("Survey_Response__c", dict(Id=sid, Account__c=a["id"], Contact__c=c["id"] if c else None, Case__c=cid, Survey_Type__c="Post-Case CSAT",
                                          NPS_Score__c=nps, CSAT_Score__c=clip(round(nps / 2), 1, 5), Verbatim__c=verb, Response_Date__c=ds(min(SNAP, closed + D(R.randint(1, 10))))))
        if verb:
            O.view.event(a, min(SNAP, closed + D(3)), "Survey", "Survey Response", band.title(), record_table="Survey_Response__c", record_id=sid,
                         contact=c, text=verb, case_number=cnum, details=dict(nps=nps))


def telemetry(a):
    sc = a.get("showcase") == "storage_capacity_crunch"
    arrays = [x for x in a.get("assets", []) if x["p"]["category"] in ("Storage", "Data Protection", "HCI") and x["p"]["serialized"]
              and ("Shelf" not in x["p"]["name"])]
    if sc and not arrays:
        p = next(p for p in CAT.PRODUCTS if p["name"].startswith("Strata 500 Unified Array G3"))
        SC.add_asset(a, None, p, dt.date(2022, 4, 18), a["sites"][0], 1, "".join(R.choice("BCDFGHJKLMNPQRSTVWXYZ0123456789") for _ in range(7)), None, source="Order")
        arrays = [a["assets"][-1]]
    for i, x in enumerate(arrays[:25]):
        import re
        mtb = re.search(r"(\d+)TB raw", x["p"]["specs"] or "")
        cap = float(mtb.group(1)) if mtb else 120.0
        used = cap * R.uniform(.22, .5)
        g = cap * R.uniform(.006, .03)
        forced = sc and i == 0
        if forced:
            months = months_between(x["sd"], SNAP)
            used = cap * .30
            g = (cap * .88 - used) / max(1, months)
        m = month_start(max(x["sd"], WIN_START))
        while m <= SNAP:
            used += g * R.uniform(.6, 1.4)
            if used > cap * .93 and not forced:
                used = cap * R.uniform(.55, .75) if chance(.5) else cap * .93
            alerts = poisson(.25 + (2 if used / cap > .85 else 0))
            O.add("Asset_Telemetry_Monthly__c", dict(Id=sfid("a09"), Asset__c=x["id"], Account__c=a["id"], Month__c=ds(m), Capacity_TB__c=cap,
                                                      Used_TB__c=round(used, 1), Used_Pct__c=round(100 * used / cap, 1), Growth_TB_Per_Month__c=round(g, 2),
                                                      Health_Alerts__c=alerts, Predictive_Failures__c=poisson(.04), Firmware_Version__c=x["fw"],
                                                      Phone_Home__c=tf(chance(.92))))
            if used / cap > .85 and not x.get("_cap_ev"):
                x["_cap_ev"] = True
                O.view.event(a, m, "Telemetry", "Capacity Alert", ">85% used", record_table="Asset_Telemetry_Monthly__c", record_id=x["id"],
                             product=x["p"], asset_serial=x["sn"], subject=f"{x['p']['name']} {x['sn']} at {100 * used / cap:.0f}% capacity",
                             details=dict(capacity_tb=cap, used_tb=round(used, 1), growth_tb_month=round(g, 2)))
            m = add_months(m, 1)


def advisories(a):
    adv_month = defaultdict(int)
    for x in a.get("assets", []):
        if not x["p"]["serialized"] or x["fw"] is None:
            continue
        for adv in ADVISORIES:
            if x["p"]["family"] in adv["fams"] and x["sd"] < adv["d"] and x["status"] == "Installed":
                remediated = x["fwd"] and x["fwd"] > adv["d"]
                st = "Remediated" if remediated else ("Risk Accepted" if chance(.08) else "Open - Not Patched")
                if a.get("showcase") == "security_advisory_exposure" and adv["num"] in ("OSA-2024-017", "OSA-2025-077"):
                    st = "Open - Not Patched"
                O.add("Advisory_Exposure__c", dict(Id=sfid("a0B"), Advisory__c=adv["id"], Asset__c=x["id"], Account__c=a["id"],
                                                    Firmware_At_Publish__c=SC.fw_version(x["p"], min(x["fwd"] or x["sd"], adv["d"])), Status__c=st,
                                                    Remediated_Date__c=ds(x["fwd"]) if st == "Remediated" else None,
                                                    Notified_Date__c=ds(adv["d"] + D(R.randint(1, 14))) if chance(.85) else None))
                adv_month[(adv["d"].year, adv["d"].month)] += 1
    a["_adv_month"] = adv_month
    for (y, mth), n in adv_month.items():
        adv = next(x for x in ADVISORIES if (x["d"].year, x["d"].month) == (y, mth))
        O.view.event(a, adv["d"], "Product Security", "Security Advisory Exposure", adv["sev"], record_table="Security_Advisory__c", record_id=adv["id"],
                     subject=f"{adv['num']}: {n} installed systems affected", text=adv["title"], details=dict(affected_assets=n))


# ------------------------------------------------------------------ marketing: campaigns, leads, intent, news
def marketing(a):
    for camp in CAMPAIGNS:
        d = camp["_d"]
        if d > SNAP:
            continue
        k = camp["_kind"]
        seg = a["seg"][fy(d)]
        p = {"summit": {"Small Business": .01, "Medium Business": .05, "Large Enterprise": .18, "Select": .9},
             "roadshow": {"Small Business": .01, "Medium Business": .04, "Large Enterprise": .1, "Select": .2},
             "webinar": {"Small Business": .01, "Medium Business": .02, "Large Enterprise": .04, "Select": .1},
             "exec_forum": {"Small Business": 0, "Medium Business": 0, "Large Enterprise": .01, "Select": .7},
             "win11": {"Small Business": .25, "Medium Business": .35, "Large Enterprise": .4, "Select": .5}}[k][seg]
        if k == "roadshow" and W.region_scope(a, fy(d)).replace("US ", "") != camp.get("_reg"):
            continue
        if not chance(p):
            continue
        cs = [c for c in a["contacts"] if c["start"] <= d and (c["end"] is None or c["end"] > d) and not c["shared"]]
        if not cs:
            continue
        for c in R.sample(cs, min(len(cs), R.randint(1, 3 if k != "win11" else 6))):
            st = wpick({"Attended": 55, "Registered": 15, "No Show": 20, "Sent": 10}) if k != "win11" else wpick({"Sent": 60, "Opened": 25, "Clicked": 12, "Responded": 3})
            interest = R.choice(["AI infrastructure", "Data protection & cyber recovery", "Client fleet management", "HCI / VMware alternatives",
                                 "Storage", "Edge", "Sustainability & ITAD", "Workstations"]) if k == "summit" else None
            mid = sfid("00v")
            O.add("CampaignMember", dict(Id=mid, CampaignId=camp["Id"], ContactId=c["id"], Status=st, HasResponded=tf(st in ("Attended", "Clicked", "Responded")),
                                         Session_Interest__c=interest, CreatedDate=ts(d - D(R.randint(5, 40)))))
            if st in ("Attended", "Clicked", "Responded"):
                O.view.event(a, d, "Marketing", "Campaign Response", camp["Type"], record_table="CampaignMember", record_id=mid, contact=c,
                             subject=camp["Name"], status=st, details=dict(session_interest=interest))
                if k == "summit" and chance(.5):
                    own = W.owner_on(a, d + D(5))
                    if own:
                        one_activity(a, rand_bday(d + D(2), min(SNAP, d + D(14))), own, "event_followup", None)
    # leads
    n = {"never": R.randint(1, 6), "lapsed": R.randint(0, 3), "development": R.randint(0, 3), "retention": R.randint(0, 2)}[a["status_end"]]
    for _ in range(n):
        d = rand_bday(WIN_START, SNAP)
        cs = [c for c in a["contacts"] if c["start"] <= d and not c["shared"]]
        dup = cs and chance(.35)
        if dup:
            c = R.choice(cs)
            f_, l_ = c["first"], c["last"]
            email = c["email"] if chance(.6) else c["email"].upper() if chance(.3) else c["email"].replace(".", "", 1)
        else:
            f_, l_ = W.person()
            email = f"{slug(f_)}.{slug(l_)}@{a['domain']}"
        lid = sfid("00Q")
        company = R.choice([a["base_name"], a["legal"], a["base_name"].upper(), a["base_name"].lower(), a["base_name"] + " Inc", a["domain"].split(".")[0]])
        conv = (not dup) and chance(.2)
        cid = None
        if conv:
            nc = W._mk_contact(a, d, R.choice(["mgr", "ic", "dir"]))
            nc["first"], nc["last"], nc["email"] = f_, l_, email
            cid = nc["id"]
        O.add("Lead", dict(Id=lid, FirstName=f_, LastName=l_, Company=company, Title=R.choice(["IT Manager", "Director IT", "sys admin", "CIO", "IT", "Procurement", None]),
                           Email=email, Phone=W.phone(a["city"][4]) if chance(.6) else None,
                           LeadSource=R.choice(["Web Form", "Content Download", "Tech Summit Badge Scan", "Webinar", "Chat", "Purchased List", "Partner Referral"]),
                           Status="Converted" if conv else wpick({"Open": 25, "Working": 20, "Nurture": 30, "Disqualified": 25}),
                           Rating=R.choice(["Hot", "Warm", "Cold", None]), Industry=a["industry"] if chance(.6) else None,
                           NumberOfEmployees=a["emp"][fy(d)] if chance(.4) else None, City=a["city"][2], State=a["state"], Country=a["country"],
                           OwnerId=next((s["person"]["id"] for s in W.STINTS if s["role"] == "SDR" and stint_active(s, d)), None),
                           Campaign__c=R.choice(CAMPAIGNS)["Id"] if chance(.4) else None,
                           Interest__c=R.choice(["Laptops", "Servers", "Storage", "AI", "Backup", "Windows 11", "Monitors", "Pricing"]),
                           IsConverted=tf(conv), ConvertedDate=ds(d + D(R.randint(1, 30))) if conv else None,
                           ConvertedAccountId=a["id"] if conv else None, ConvertedContactId=cid, Matched_Account_Hint__c=None, CreatedDate=ts(d)))
        if dup:
            O.issue("lead_duplicates_existing_contact", "Lead", lid, "Email", email, c["id"], a["id"], "Lead name/email matches an existing Contact",
                    "Marketing created a new lead for someone already in CRM as a contact.", "Low")
        O.view.event(a, d, "Marketing", "Lead", "Converted" if conv else "Created", record_table="Lead", record_id=lid,
                     subject=f"Lead: {f_} {l_} ({company})", details=dict(email=email, company_as_entered=company), account_known=conv or chance(.3))
    # intent signals
    if chance({"Small Business": .1, "Medium Business": .35, "Large Enterprise": .6, "Select": .9}[a["seg_end"]]):
        topics = ["AI servers & GPUs", "Hyperconverged infrastructure", "Storage arrays", "Backup & cyber recovery", "Windows 11 laptops",
                  "Workstations", "Network switches", "Device-as-a-Service", "Edge computing", "Server refresh"]
        m = month_start(WIN_START)
        while m <= SNAP:
            f = fy(m)
            hot = [t for t in topics if any(k in " ".join(a["inits"].get(f, [])) for k in t.split()[:1])]
            for t in topics:
                p = .5 if t in hot else .06
                if a.get("showcase") == "ai_reacquisition" and t == "AI servers & GPUs" and m > SNAP - D(240):
                    p = 1
                if chance(p):
                    sc = int(clip(R.gauss(70 if t in hot else 40, 15), 5, 99))
                    O.add("Web_Intent_Signal__c", dict(Id=sfid("a06"), Account__c=a["id"], Week_Of__c=ds(m + D(R.randint(0, 3) * 7)), Topic__c=t,
                                                        Intent_Score__c=sc, Page_Views__c=R.randint(1, 60), Content_Downloads__c=poisson(.6),
                                                        Source__c=R.choice(["orvane.com", "Third-party intent (BizGraph)", "orvane.com"])))
                    if sc >= 80:
                        O.view.event(a, m, "Marketing", "Intent Surge", t, record_table="Web_Intent_Signal__c", subject=f"Intent surge: {t}", details=dict(score=sc))
            m = add_months(m, 1)
    # news
    for d, t in a["news"]:
        if d < WIN_START or d > SNAP:
            continue
        nm = a["view"].true_name(d)
        sl, _ = slots_for(a, d, extra=dict(account=nm, site_city=R.choice(a["sites"])["city"][2],
                                           hq_city=a["hq_move"][1][2] if a.get("hq_move") else a["city"][2], pct=R.randint(5, 25)))
        if t == "acquired" and a.get("acquired_by"):
            sl["contact2_name"] = a["acquired_by"][0]["base_name"]
        h, s = TX.news(t, sl)
        nid = sfid("a07")
        O.add("News_Item__c", dict(Id=nid, Account__c=a["id"] if chance(.85) else None, Company_Name_In_Article__c=nm, Published_Date__c=ds(d),
                                   News_Type__c=t.replace("_", " ").title(), Headline__c=h, Summary__c=s,
                                   Source__c=R.choice(["BizWire", "Regional Business Journal", "TechTarget-style trade press", "Press Release", "Local News"]),
                                   URL__c=f"https://news.example.com/{slug(nm)[:30]}-{d.isoformat()}"))
        O.view.event(a, d, "News", "News", t.replace("_", " ").title(), record_table="News_Item__c", record_id=nid, subject=h, text=s)
