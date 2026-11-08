"""Append hand-written showcase notes (<key>.notes.json) into Task/Event/Note/FeedItem + the unified timeline."""
import csv
import datetime as dt
import glob
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from core import sfid, ts, jdump
from out import SCHEMA, TL_FIELDS

root, notes_dir = sys.argv[1], sys.argv[2]
core.reseed(777)
R = random.Random(777)
T = os.path.join(root, "aible_load", "tables")
K = os.path.join(root, "answer_key")
S = json.load(open(os.path.join(K, "generation_summary.json")))["showcase"]


def rows(n):
    return csv.DictReader(open(os.path.join(T, n + ".csv"), encoding="utf-8"))


users = {r["Name"]: r for r in rows("User")}
acc = {r["Id"]: r for r in rows("Account")}
contacts = defaultdict(dict)
for r in rows("Contact"):
    contacts[r["AccountId"]][f"{r['FirstName']} {r['LastName']}"] = r
seg = {(r["Account__c"], r["Fiscal_Year__c"]): r for r in rows("Account_Segment_History__c")}
firmo = {(r["Account__c"], r["Fiscal_Year__c"]): r for r in rows("Account_Firmographics__c") if r["Source__c"].startswith("BizGraph")}
cov = defaultdict(list)
for r in csv.DictReader(open(os.path.join(K, "golden_coverage_history.csv"))):
    if r["coverage_role"] == "Account Owner":
        cov[r["account_id"]].append(r)
roles = defaultdict(list)
for r in csv.DictReader(open(os.path.join(K, "golden_coverage_history.csv"))):
    roles[(r["account_id"], r["user_name"])].append(r)


def appender(name, fields):
    f = open(os.path.join(T if name != "timeline" else os.path.join(root, "aible_load"), (name if name != "timeline" else "orvane_unified_timeline") + ".csv"),
             "a", newline="", encoding="utf-8")
    return f, csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")


W = {n: appender(n, SCHEMA[n]) for n in ("Task", "Event", "Note", "FeedItem")}
TLf, TL = appender("timeline", TL_FIELDS)
n_in, ev = 0, 0
for path in sorted(glob.glob(os.path.join(notes_dir, "*.notes.json"))):
    key = os.path.basename(path).split(".")[0]
    aid = S[key]["account_id"]
    a = acc[aid]
    for e in json.load(open(path)):
        d = dt.date.fromisoformat(e["date"])
        f = f"FY{core.fy(d)}"
        cv = [r for r in roles[(aid, e["author"])] if r["start_date"] <= e["date"] <= r["end_date"]] or roles[(aid, e["author"])]
        u = {"Id": cv[0]["user_id"]} if cv and cv[0]["user_id"] else users.get(e["author"])
        c = contacts[aid].get(e["contact"]) if e.get("contact") else None
        kind = e["kind"]
        uid = u["Id"] if u else None
        stamp = ts(d)
        rid = None
        if kind in ("call", "email_out", "email_in"):
            rid = sfid("00T")
            W["Task"][1].writerow(dict(Id=rid, WhoId=c["Id"] if c else None, WhatId=e.get("opportunity_id") or aid, AccountId=aid, OwnerId=uid,
                                       Subject=e["subject"][:255], Description=e["body"], TaskSubtype="Call" if kind == "call" else "Email",
                                       Type="Call" if kind == "call" else "Email", CallDurationInSeconds=R.randint(300, 2700) if kind == "call" else None,
                                       CallDisposition="Connected" if kind == "call" else None,
                                       Call_Direction__c="Inbound" if kind == "email_in" else "Outbound", ActivityDate=e["date"], Status="Completed",
                                       Priority="Normal", Topic__c=None, CreatedDate=stamp))
            tbl, etype, sub = "Task", "Call" if kind == "call" else "Email", "Connected" if kind == "call" else ("Inbound" if kind == "email_in" else "Outbound")
        elif kind == "meeting":
            rid = sfid("00U")
            st = dt.datetime(d.year, d.month, d.day, R.randint(14, 21), R.choice([0, 30]))
            W["Event"][1].writerow(dict(Id=rid, WhoId=c["Id"] if c else None, WhatId=e.get("opportunity_id") or aid, AccountId=aid, OwnerId=uid,
                                        Subject=e["subject"][:255], Type="Meeting", StartDateTime=core.ts_dt(st), EndDateTime=core.ts_dt(st + dt.timedelta(minutes=60)),
                                        DurationInMinutes=60, Location=R.choice(["Zoom", "Microsoft Teams", "Customer HQ", "Onsite"]), Description=e["body"],
                                        CreatedDate=ts(d - dt.timedelta(days=R.randint(1, 10)))))
            tbl, etype, sub = "Event", "Meeting", e["subject"][:60]
        elif kind == "note":
            rid = sfid("002")
            W["Note"][1].writerow(dict(Id=rid, ParentId=e.get("opportunity_id") or aid, AccountId=aid, OwnerId=uid, Title=e["subject"][:255], Body=e["body"],
                                       Note_Type__c="Account Note", CreatedDate=stamp))
            tbl, etype, sub = "Note", "Note", "Account Note"
        else:
            rid = sfid("0D5")
            W["FeedItem"][1].writerow(dict(Id=rid, ParentId=aid, CreatedById=uid, Body=e["body"], Type="TextPost", CreatedDate=stamp))
            tbl, etype, sub = "FeedItem", "Chatter Post", "post"
        sg = seg.get((aid, f), {})
        fm = firmo.get((aid, f), {})
        owner = next((r["user_name"] for r in cov[aid] if r["start_date"] <= e["date"] <= r["end_date"]), None) or "Unassigned"
        role = next((r["coverage_role"] for r in roles[(aid, e["author"])] if r["start_date"] <= e["date"] <= r["end_date"]), None)
        par = acc.get(a["ParentId"]) if a["ParentId"] else None
        ev += 1
        TL.writerow(dict(event_id=f"EVN{ev:08d}", event_timestamp=stamp, event_date=e["date"], fiscal_year=f, fiscal_quarter=f"{f} Q{core.fq(d)}",
                         source_system="CRM", event_type=etype, event_subtype=sub, account_id=aid, account_name=a["Name"],
                         erp_customer_number=a["ERP_Customer_Number__c"], parent_account_id=a["ParentId"] or None, parent_account_name=par["Name"] if par else None,
                         ultimate_parent_name=par["Name"] if par else None, segment=sg.get("Segment__c"), coverage_status=sg.get("Coverage_Status__c"),
                         sales_region=sg.get("Region__c"), industry=a["Industry"], employees=fm.get("Employees__c"), annual_revenue=fm.get("Annual_Revenue__c"),
                         account_owner=owner, rep_name=e["author"], rep_role=role, contact_name=e.get("contact") or None,
                         contact_title=c["Title"] if c else None, contact_email=c["Email"] if c else None, opportunity_id=e.get("opportunity_id") or None,
                         subject=e["subject"], text=e["body"], record_table=tbl, record_id=rid))
        n_in += 1
for f, _ in list(W.values()) + [(TLf, None)]:
    f.close()
print(f"ingested {n_in} hand-written notes")
