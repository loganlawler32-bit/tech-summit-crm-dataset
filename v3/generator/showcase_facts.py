"""Write a markdown fact sheet per showcase account (input for hand-written notes)."""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

root, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
T = os.path.join(root, "aible_load", "tables")
K = os.path.join(root, "answer_key")
S = json.load(open(os.path.join(K, "generation_summary.json")))["showcase"]


def rows(n):
    return csv.DictReader(open(os.path.join(T, n + ".csv"), encoding="utf-8"))


ids = {v["account_id"]: k for k, v in S.items()}
gold = {r["account_id"]: r for r in csv.DictReader(open(os.path.join(K, "golden_account_master.csv")))}
users = {r["Id"]: r for r in rows("User")}
acc = {r["Id"]: r for r in rows("Account")}
fam = defaultdict(list)
for a, g in gold.items():
    if g["true_ultimate_parent_account_id"] in ids:
        fam[g["true_ultimate_parent_account_id"]].append(a)
want = set(ids) | {x for v in fam.values() for x in v}
F = defaultdict(lambda: defaultdict(list))
for r in rows("Contact"):
    if r["AccountId"] in ids:
        F[r["AccountId"]]["contacts"].append(r)
gc = {r["contact_id"]: r for r in csv.DictReader(open(os.path.join(K, "golden_contacts.csv"))) if r["account_id"] in ids}
for r in csv.DictReader(open(os.path.join(K, "golden_coverage_history.csv"))):
    if r["account_id"] in ids:
        F[r["account_id"]]["coverage"].append(r)
for r in rows("Sales_Order"):
    if r["End_User_Account_Id"] in want or r["Customer_Number"] in {acc[x]["ERP_Customer_Number__c"] for x in ids if x in acc}:
        F[r["End_User_Account_Id"]]["orders"].append(r)
for r in rows("Opportunity"):
    if r["AccountId"] in ids and (r["IsClosed"] == "false" or float(r["Amount"] or 0) > 150000):
        F[r["AccountId"]]["opps"].append(r)
for r in rows("News_Item__c"):
    if r["Account__c"] in ids:
        F[r["Account__c"]]["news"].append(r)
for r in rows("Account_Environment__c"):
    if r["Account__c"] in ids:
        F[r["Account__c"]]["env"].append(r)
for r in rows("Account_Firmographics__c"):
    if r["Account__c"] in ids and r["Source__c"].startswith("BizGraph"):
        F[r["Account__c"]]["firmo"].append(r)
for r in rows("Lease_Contract"):
    if r["CRM_Account_Id"] in ids:
        F[r["CRM_Account_Id"]]["leases"].append(r)
tel = defaultdict(dict)
for r in rows("Asset_Telemetry_Monthly__c"):
    if r["Account__c"] in ids:
        tel[r["Account__c"]][r["Asset__c"]] = r
assets = {}
for r in rows("Asset"):
    if r["AccountId"] in ids:
        assets[r["Id"]] = r
        F[r["AccountId"]]["assets"].append(r)
adv = defaultdict(Counter)
for r in rows("Advisory_Exposure__c"):
    if r["Account__c"] in ids:
        adv[r["Account__c"]][r["Status__c"]] += 1
iss = defaultdict(Counter)
for r in csv.DictReader(open(os.path.join(K, "planted_issues.csv"))):
    if r["account_id"] in want:
        iss[ids.get(r["account_id"]) or ("sub of " + str([k for k, v in fam.items() if r["account_id"] in v][:1]))][r["issue_type"]] += 1
STORY = {
    "select_family_misrouting": "Select parent with many subsidiaries. Several subsidiaries are NOT linked to the parent in CRM, are owned by ordinary LE/MB reps, and are buying at standard discount instead of the parent's master agreement pricing (leakage). The GAD doesn't know; reps from different teams step on each other.",
    "storage_capacity_crunch": "Large Enterprise account whose main Strata array is ~88% full and growing ~4%/month; competitor Lumora is pitching. Storage expansion/refresh is overdue; warranty renewal decisions coming.",
    "champion_left_mid_deal": "LE account. Executive sponsor/champion resigned 2025-07-18 in the middle of a $1.24M Servers & HCI refresh opportunity (open, close 2026-03-27). They later became CIO at another customer. A new exec started 2025-10-06 and wants to re-baseline vendors. The CRM contact record still shows the champion as Active.",
    "headcount_jump_flat_pc_spend": "Company acquired another business in early FY26 (March 2025) and headcount jumped ~65%, but PC/client spend stayed flat; Windows 11 migration is behind; large legacy fleet coming off warranty.",
    "missed_po_credit_hold": "LE account where three recent deals (Dec 2025-Jan 2026) were won/committed verbally but orders sit On Hold awaiting PO, and the account is on credit hold because of past-due invoices and short-pays disputing discounts.",
    "rep_carousel_partner_conflict": "Medium Business account that has had 5+ different owners in 5 years with vacancy gaps, notes lost between handoffs; a channel partner holds the account and also sells into it, causing conflict with direct reps.",
    "security_advisory_exposure": "LE account with a large Atlas server fleet running old BMC firmware; hundreds of systems exposed to critical advisories (OSA-2024-017 and OSA-2025-077) and still unpatched.",
    "ai_reacquisition": "Development account (no purchases in 12+ months) now running an AI pilot; surging web intent on AI servers & GPUs; a $640K Atlas AI opportunity was opened Nov 2025 and they are also evaluating public cloud GPUs. CRM still shows Coverage Status 'Retention' (stale).",
    "consumer_to_mb_journey": "Founder bought laptops on the consumer web store in 2021, company opened a Small Business account, grew quickly and became Medium Business in FY26; consumer purchases were never linked to the business.",
    "lease_end_refresh": "Account with a 2,380-device Orvane Financial Services lease ending 2026-04-28; refresh vs extend vs buyout decision; Windows 11 and ITAD/data sanitization matter.",
}
for aid, key in ids.items():
    a = acc[aid]
    g = gold[aid]
    L = [f"# Showcase: {key}", "", f"**Storyline to bring to life:** {STORY.get(key, '')}", "",
         f"## Account\n- CRM Name: {a['Name']}  (true legal name: {g['true_legal_name_at_snapshot']})\n- Account Id: {aid}\n- Industry: {a['Industry']} / {a['Sub_Industry__c']}\n"
         f"- HQ: {a['BillingCity']}, {a['BillingState']} {a['BillingCountry']}\n- Website: {a['Website']}\n- Segment by FY (true): FY22 {g['true_segment_FY22']}, FY23 {g['true_segment_FY23']}, "
         f"FY24 {g['true_segment_FY24']}, FY25 {g['true_segment_FY25']}, FY26 {g['true_segment_FY26']}\n- Employees FY22 {g['employees_FY22']} -> FY26 {g['employees_FY26']} ({g['growth_pattern']})\n"
         f"- Coverage status in CRM: {a['Coverage_Status__c']} (true at 2026-01-31: {g['true_status_at_snapshot']}); last purchase {g['true_last_purchase_date']}\n"
         f"- Partner of record: {g['partner_of_record_at_snapshot'] or 'none'}; Primary competitor: {a['Primary_Competitor__c'] or 'unknown'}"]
    L.append("\n## Orvane people on the account (who covered it when) - use these exact names as authors")
    for r in sorted(F[aid]["coverage"], key=lambda r: (r["start_date"], r["coverage_role"])):
        L.append(f"- {r['start_date']} to {r['end_date']}: {r['coverage_role']}: {r['user_name'] or '(VACANT - no one assigned)'}")
    L.append("\n## Customer contacts (use these exact names)")
    for c in F[aid]["contacts"][:45]:
        t = gc.get(c["Id"], {})
        L.append(f"- {c['FirstName']} {c['LastName']} - {c['Title']} ({c['Level__c']}) email {c['Email']}; true status {t.get('true_status')}"
                 + (f", left {t.get('left_date')}" if t.get("left_date") else "") + (f"; CRM status {c['Status__c']}"))
    L.append("\n## Firmographics by FY (3rd party)")
    for r in sorted(F[aid]["firmo"], key=lambda r: r["Fiscal_Year__c"]):
        L.append(f"- {r['Fiscal_Year__c']}: employees {r['Employees__c']}, revenue ${float(r['Annual_Revenue__c'] or 0):,.0f}, est IT budget ${float(r['Est_IT_Budget__c'] or 0):,.0f}")
    L.append("\n## Environment & initiatives by FY")
    for r in sorted(F[aid]["env"], key=lambda r: r["Fiscal_Year__c"]):
        L.append(f"- {r['Fiscal_Year__c']}: OS {r['Client_OS__c']}; hypervisor {r['Hypervisor__c']}; cloud {r['Public_Cloud__c']}; backup {r['Backup_Approach__c']}; initiatives: {r['Strategic_Initiatives__c']}")
    od = F[aid]["orders"]
    byfy = Counter()
    for o in od:
        byfy[o["Order_Date"][:7]] += float(o["Order_Total_USD"])
    L.append(f"\n## Orders: {len(od)} total. Largest 15:")
    for o in sorted(od, key=lambda o: -float(o["Order_Total_USD"]))[:15]:
        L.append(f"- {o['Order_Date']} {o['Order_Number']} ${float(o['Order_Total_USD']):,.0f} channel {o['Channel']} rep {o['Sales_Rep_Name']} PO {o['PO_Number']} status {o['Status']} hold {o['Hold_Reason']}")
    L.append("\n## Most recent 12 orders:")
    for o in sorted(od, key=lambda o: o["Order_Date"])[-12:]:
        L.append(f"- {o['Order_Date']} {o['Order_Number']} ${float(o['Order_Total_USD']):,.0f} {o['Channel']} rep {o['Sales_Rep_Name']} PO {o['PO_Number']} status {o['Status']} hold {o['Hold_Reason']} {o['Notes'] or ''}")
    L.append("\n## Open / large opportunities")
    for r in sorted(F[aid]["opps"], key=lambda r: r["CloseDate"])[-14:]:
        L.append(f"- {r['Id']} {r['Name']} | {r['Product_Group__c']} | {r['StageName']} | ${float(r['Amount'] or 0):,.0f} | close {r['CloseDate']} | owner {users.get(r['OwnerId'], {}).get('Name')} | won={r['IsWon']} closed={r['IsClosed']}")
    L.append("\n## Install base highlights")
    cats = Counter()
    for x in F[aid]["assets"]:
        cats[(x["Configuration__c"] or x["Name"])[:60] if x["Quantity"] == "1" else x["Name"][:60]] += int(x["Quantity"] or 1)
    for k2, v in cats.most_common(12):
        L.append(f"- {v} x {k2}")
    for asid, t in list(tel[aid].items())[:6]:
        x = assets.get(asid, {})
        L.append(f"- Telemetry {x.get('Name')} serial {x.get('SerialNumber')}: {t['Used_Pct__c']}% of {t['Capacity_TB__c']}TB (as of {t['Month__c']}), growth {t['Growth_TB_Per_Month__c']} TB/mo, firmware {t['Firmware_Version__c']}")
    if adv[aid]:
        L.append(f"- Security advisory exposures: {dict(adv[aid])}")
    for r in F[aid]["leases"]:
        L.append(f"- Lease {r['Lease_Number']} {r['Lease_Type']} {r['Start_Date']} to {r['End_Date']} units {r['Units']} financed ${float(r['Financed_Amount']):,.0f} status {r['Status']}")
    L.append("\n## News")
    for r in F[aid]["news"]:
        L.append(f"- {r['Published_Date__c']} [{r['News_Type__c']}] {r['Headline__c']}")
    if aid in fam:
        L.append("\n## Subsidiaries (true family)")
        for s in fam[aid][:20]:
            sa, sg = acc.get(s, {}), gold[s]
            L.append(f"- {sa.get('Name')} (id {s}) segment {sa.get('Segment__c')} owner {users.get(sa.get('OwnerId'), {}).get('Name')} | linked in CRM: {sa.get('ParentId') == aid} | unlinked flag: {sg['unlinked_in_crm']}")
    L.append("\n## Planted data problems on this account")
    for k2, v in iss.get(key, {}).items():
        L.append(f"- {k2}: {v}")
    for k2, c in iss.items():
        if isinstance(k2, str) and k2.startswith("sub of") and aid in k2:
            L.append(f"- subsidiaries: {dict(c)}")
    open(os.path.join(outdir, f"{key}.md"), "w").write("\n".join(L) + "\n")
print("wrote", len(ids), "fact sheets to", outdir)
