"""Print the key facts for each showcase account (used for review + as fact sheets for written notes)."""
import csv, json, os, sys
from collections import Counter, defaultdict
root = sys.argv[1]
T = os.path.join(root, "aible_load", "tables")
S = json.load(open(os.path.join(root, "answer_key", "generation_summary.json")))["showcase"]
ids = {v["account_id"]: k for k, v in S.items()}
def rows(n):
    return csv.DictReader(open(os.path.join(T, n + ".csv"), encoding="utf-8"))
acc = {r["Id"]: r for r in rows("Account")}
users = {r["Id"]: r["Name"] for r in rows("User")}
erp_of = {r["Id"]: r["ERP_Customer_Number__c"] for r in acc.values()}
facts = defaultdict(lambda: defaultdict(Counter))
for r in rows("Sales_Order"):
    a = r["End_User_Account_Id"]
    if a in ids:
        f = facts[a]
        f["orders"]["n"] += 1
        f["orders"][r["Status"]] += 1
        if r["Hold_Reason"]: f["holds"][r["Hold_Reason"]] += 1
        f["fy_rev"][r["Order_Date"][:4]] += float(r["Order_Total_USD"])
for r in rows("Opportunity"):
    if r["AccountId"] in ids and r["IsClosed"] == "false":
        facts[r["AccountId"]]["open_opps"][f"{r['Product_Group__c']} {r['StageName']} close {r['CloseDate']} ${float(r['Amount'] or 0):,.0f}"] += 1
for r in rows("Asset_Telemetry_Monthly__c"):
    if r["Account__c"] in ids and r["Month__c"] >= "2025-12-01":
        facts[r["Account__c"]]["telemetry"][f"{r['Asset__c'][-6:]} {r['Used_Pct__c']}% of {r['Capacity_TB__c']}TB"] += 1
for r in rows("Advisory_Exposure__c"):
    if r["Account__c"] in ids:
        facts[r["Account__c"]]["advisory"][r["Status__c"]] += 1
for r in rows("Account_Segment_History__c"):
    if r["Account__c"] in ids:
        facts[r["Account__c"]]["segments"][f"{r['Fiscal_Year__c']} {r['Segment__c']} {r['Coverage_Status__c']} {r['Region__c']} owner={users.get(r['Assigned_Owner__c'])}"] += 1
for r in rows("Lease_Contract"):
    if r["CRM_Account_Id"] in ids:
        facts[r["CRM_Account_Id"]]["leases"][f"{r['Lease_Number']} ends {r['End_Date']} units={r['Units']} {r['Status']}"] += 1
for r in rows("Consumer_Order"):
    pass
iss = Counter()
for r in csv.DictReader(open(os.path.join(root, "answer_key", "planted_issues.csv"))):
    if r["account_id"] in ids:
        facts[r["account_id"]]["issues"][r["issue_type"]] += 1
for aid, k in ids.items():
    a = acc[aid]
    print(f"\n### {k}: {a['Name']} ({a['Segment__c']}, {a['Coverage_Status__c']}, owner {users.get(a['OwnerId'])})")
    for key, c in facts[aid].items():
        print(f"  {key}: " + "; ".join(f"{x}" + (f" x{n}" if n > 1 else "") for x, n in sorted(c.items())[:14]))
