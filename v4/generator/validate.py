"""Integrity + realism checks for a generated V2 output folder."""
import csv
import os
import sys
from collections import Counter, defaultdict

root = sys.argv[1]
T = os.path.join(root, "aible_load", "tables")


def rows(name, cols=None):
    with open(os.path.join(T, name + ".csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            yield {k: r[k] for k in cols} if cols else r


def ids(name, col="Id"):
    return {r[col] for r in rows(name, [col])}


acc = ids("Account")
con = ids("Contact")
opp = ids("Opportunity")
usr = ids("User")
prod = ids("Product2")
camp = ids("Campaign")
case = ids("Case")
asset = ids("Asset")
orders = ids("Sales_Order", "Order_Number")
invs = ids("Invoice", "Invoice_Number")
erp = ids("ERP_Customer", "Customer_Number")
problems = Counter()


def fk(table, col, target, allow_blank=True):
    n = bad = 0
    for r in rows(table, [col]):
        v = r[col]
        if not v:
            continue
        n += 1
        if v not in target:
            bad += 1
    status = "OK " if bad == 0 else "BAD"
    print(f"  {status} {table}.{col} -> {bad:,} orphans of {n:,}")
    problems[status] += 1


print("Foreign keys")
for t, c, tgt in [("Contact", "AccountId", acc), ("Opportunity", "AccountId", acc), ("Opportunity", "OwnerId", usr), ("OpportunityLineItem", "OpportunityId", opp),
                  ("OpportunityLineItem", "Product2Id", prod), ("OpportunityHistory", "OpportunityId", opp), ("OpportunityTeamMember", "UserId", usr),
                  ("Quote", "OpportunityId", opp), ("Task", "AccountId", acc), ("Task", "OwnerId", usr), ("Event", "AccountId", acc), ("Case", "AccountId", acc),
                  ("Case", "AssetId", asset), ("CaseComment", "ParentId", case), ("Asset", "AccountId", acc), ("Asset", "Product2Id", prod),
                  ("CampaignMember", "CampaignId", camp), ("CampaignMember", "ContactId", con), ("AccountTeamMember", "UserId", usr),
                  ("Sales_Order", "CRM_Opportunity_Id", opp), ("Sales_Order_Line", "Order_Number", orders), ("Invoice", "Order_Number", orders),
                  ("Payment", "Invoice_Number", invs), ("Shipment", "Order_Number", orders), ("Account", "OwnerId", usr), ("Account", "ParentId", acc),
                  ("Sales_Order", "Customer_Number", erp), ("Advisory_Exposure__c", "Asset__c", asset), ("Account", "Partner_Of_Record__c", acc)]:
    fk(t, c, tgt)

print("\nUniqueness")
for t, c in [("Account", "Id"), ("Contact", "Id"), ("Opportunity", "Id"), ("Sales_Order", "Order_Number"), ("Invoice", "Invoice_Number"), ("Case", "CaseNumber"),
             ("Asset", "Id"), ("Task", "Id")]:
    vals = [r[c] for r in rows(t, [c])]
    d = len(vals) - len(set(vals))
    print(f"  {'OK ' if d == 0 else 'BAD'} {t}.{c} duplicates: {d}")

print("\nDates (nothing after 2026-01-31 except open opps/future tasks)")
late = Counter()
for t, c in [("Sales_Order", "Order_Date"), ("Invoice", "Invoice_Date"), ("Payment", "Payment_Date"), ("Case", "CreatedDate"), ("Event", "StartDateTime")]:
    for r in rows(t, [c]):
        if r[c] and r[c][:10] > "2026-01-31":
            late[t] += 1
print("  ", dict(late) or "OK")
bad_c = bad_m = 0
for r in rows("Opportunity", ["CreatedDate", "LastModifiedDate"]):
    bad_c += r["CreatedDate"][:10] > "2026-01-31"
    bad_m += r["LastModifiedDate"] < r["CreatedDate"]
print(f"  {'OK ' if not bad_c else 'BAD'} Opportunity created after snapshot: {bad_c:,}")
print(f"  {'OK ' if not bad_m else 'BAD'} Opportunity modified before created: {bad_m:,}")
tl = Counter()
blank_acct = 0
n = 0
for r in csv.DictReader(open(os.path.join(root, "aible_load", "orvane_unified_timeline.csv"), encoding="utf-8")):
    n += 1
    tl[r["source_system"]] += 1
    if not r["account_id"]:
        blank_acct += 1
print(f"\nTimeline: {n:,} rows; by source {dict(tl)}; rows with no account_id (unattributed): {blank_acct:,}")
orders_amt = defaultdict(float)
for r in rows("Sales_Order", ["Order_Number", "Subtotal"]):
    orders_amt[r["Order_Number"]] = float(r["Subtotal"])
line_amt = defaultdict(float)
for r in rows("Sales_Order_Line", ["Order_Number", "Extended_Price"]):
    line_amt[r["Order_Number"]] += float(r["Extended_Price"])
mism = sum(1 for k in orders_amt if abs(orders_amt[k] - line_amt[k]) > 1)
print(f"Order subtotal vs sum(lines) mismatches: {mism}")
print("\nIssue types planted:")
ic = Counter(r["issue_type"] for r in csv.DictReader(open(os.path.join(root, "answer_key", "planted_issues.csv"))))
for k, v in ic.most_common():
    print(f"  {k:45s}{v:>8,}")
