#!/usr/bin/env python3
"""Orvane Technologies synthetic CRM + ERP dataset (V2).

    python3 main.py --accounts 500  --out "../sample_500"
    python3 main.py --accounts 20000 --out "../full_20000"
"""
import argparse
import json
import os
import shutil
import sys
import time
from collections import Counter, defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("--accounts", type=int, default=500)
ap.add_argument("--out", default=None)
ap.add_argument("--seed", type=int, default=2026)
ap.add_argument("--base-accounts", type=int, default=0, help="rebuild this many base accounts exactly (V2 sample) then grow to --accounts")
args = ap.parse_args()

import core
core.reseed(args.seed)
from core import *
import catalog as CAT
import world as W
import out as OUT
import view as VW
import sim_commerce as SC
import sim_crm as CRM
import render as RN

HERE = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(args.out or os.path.join(HERE, "..", f"sample_{args.accounts}"))
if os.path.exists(root):
    shutil.rmtree(root)
os.makedirs(root)
t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


log(f"building world for {args.accounts:,} accounts")
if args.base_accounts:
    leaders = W.build(args.base_accounts)
    W.extend(args.accounts)
else:
    leaders = W.build(args.accounts)
log(f"world: {len(W.ACCOUNTS):,} accounts, {len(W.CONTACTS):,} contacts, {len(W.PEOPLE):,} employees")
for p in CAT.PRODUCTS:
    p["Id"] = sfid("01t")
O = OUT.Out(root)
for m in (SC, CRM, RN, VW):
    m.O = O
RN.special_users()
SC.init_fx()
CRM.build_campaigns()
CRM.build_advisories()
SC.ADVISORIES = CRM.ADVISORIES


def rep_for(a, d, cat):
    for lab in SC.CAT_ROLE[cat]:
        st = W.owner_on(a, d) if lab == "OWNER" else W.owner_on(a, d, lab)
        if st:
            return st, lab
    return W.owner_on(a, d), "OWNER"


order_total = 0
accts = sorted(W.ACCOUNTS, key=lambda a: a["depth"])
for i, a in enumerate(accts):
    RN.prep(a)
    plans = SC.plan_orders(a)
    sk = a.get("showcase")
    if sk == "missed_po_credit_hold":
        a["pay_style"] = "disputer"
        plans += [dict(date=bday(SNAP - D(k)), cat=c, target=t, fy=26) for k, c, t in ((41, "client", 182000), (26, "server", 238000), (12, "client", 96000))]
    if sk == "lease_end_refresh":
        plans.append(dict(date=dt.date(2023, 4, 28), cat="client", target=1_650_000, fy=24, force_lease=True))
    plans.sort(key=lambda p: p["date"])
    orders, ar = [], []
    for p in plans:
        o = SC.make_order(a, p, None, rep_for)
        if not o:
            continue
        ar = [(d, v) for d, v in ar if (p["date"] - d).days < 75]
        SC.finance_order(a, o, a["sites"][0], sum(v for _, v in ar))
        ar.append((p["date"], o["sub"]))
        orders.append(o)
    V = VW.View(a, orders)
    O.view = V
    SC.legacy(a, V)
    CRM.pipeline(a, orders)
    SC.write_commerce(a, orders, V)
    SC.flex(a)
    SC.consumer(a)
    CRM.telemetry(a)
    CRM.advisories(a)
    CRM.support(a)
    CRM.activities(a, orders)
    CRM.marketing(a)
    RN.account(a, orders)
    RN.erp_master(a)
    order_total += len(orders)
    a["_orders_n"] = len(orders)
    a["_rev"] = {f: sum(o["sub"] for o in orders if o["fy"] == f and o["status"] != "Cancelled") for f in W.FYS}
    if (i + 1) % max(1, len(accts) // 20) == 0:
        log(f"  {i + 1:,}/{len(accts):,} accounts, {order_total:,} orders, {O.tl.n:,} timeline events")

log("globals: users, partners, products, quotas, forecasts")
RN.users(leaders)
RN.partners()
RN.products()
# quotas + weekly forecast submissions per quota-carrying rep
QBASE = {"SB_REP": 450_000, "MB_IAE": 1_300_000, "LE_FAE": 3_200_000, "SEL_GAD": 14_000_000, "SEL_RAM": 2_400_000, "LE_IAE": 2_000_000,
         "OV_SERVER": 2_600_000, "OV_STORAGE": 2_400_000, "OV_DP": 1_500_000, "OV_NET": 1_100_000, "OV_WKS": 1_200_000, "OV_SW": 900_000,
         "OV_SVC": 1_000_000, "MB_SPEC_CLIENT": 1_100_000, "MB_SPEC_INFRA": 1_300_000, "MB_SPEC_SW": 500_000, "MB_SPEC_SVC": 500_000}
BIAS = {"sandbagger": .72, "happy_ears": 1.45, "star": 1.02, "discounter": 1.08, "sloppy": 1.25}
for s in W.STINTS:
    if s["role"] not in QBASE:
        continue
    pid = s["person"]["id"]
    st = CRM.REP_STATS.get(pid, {})
    for f in W.FYS:
        for q in range(1, 5):
            qs = add_months(fy_start(f), 3 * (q - 1))
            qe = add_months(qs, 3) - D(1)
            if not (s["start"] <= qe and (s["end"] is None or s["end"] > qs)) or qs > SNAP:
                continue
            tenure_q = max(0, months_between(s["person"]["hire"], qs) // 3)
            ramp = [25, 50, 75][tenure_q] if tenure_q < 3 else 100
            quota = human_round(QBASE[s["role"]] / 4 * (1.08 ** (f - 22)) * ramp / 100 * (1.25 if q == 4 else .9 if q == 1 else 1))
            O.add("Quota__c", dict(Id=sfid("a0Q"), User__c=pid, Sales_Role__c=s["role"], Fiscal_Year__c=f"FY{f}", Fiscal_Quarter__c=f"Q{q}",
                                   Quota_Amount__c=quota, Ramp_Pct__c=ramp))
            won = st.get((f, q, "won"), 0)
            pipe = st.get((f, q, "pipe"), 0) + won * R.uniform(.3, .9)
            bias = BIAS.get(st.get("persona") or s["person"]["persona"], 1)
            wk = qs
            k = 0
            while wk <= min(qe, SNAP) and k < 13:
                frac = (k + 1) / 13
                closed_td = won * min(1, frac ** 1.6)
                commit = human_round(max(closed_td, won * bias * R.uniform(.88, 1.08)))
                O.add("Forecast_Submission__c", dict(Id=sfid("a0F"), User__c=pid, Fiscal_Quarter__c=f"FY{f} Q{q}", Week_Of__c=ds(wk),
                                                     Commit_Amount__c=commit, Best_Case_Amount__c=human_round(commit * R.uniform(1.1, 1.5)),
                                                     Pipeline_Amount__c=human_round(pipe * R.uniform(.9, 1.2)), Quota__c=quota, Closed_To_Date__c=round(closed_td, 2)))
                wk += D(7)
                k += 1
for camp in CRM.CAMPAIGNS:
    pass
RN.golden(root)
counts = O.counts()
issues = dict(O.ic)
O.close()

# ------------------------------------------------------------------ summary
A = W.ACCOUNTS
seg26 = Counter(a["view"].seg[26] for a in A)
true_seg = Counter(a["seg"][26] for a in A)
status = Counter(a["view"].true_status(SNAP) for a in A)
never = sum(1 for a in A if not a["purchases"])
rev = {f: round(sum(a["_rev"][f] for a in A) / 1e6, 1) for f in W.FYS}
moved = sum(1 for a in A if len(set(a["seg"][f] for f in W.FYS)) > 1)
owners = Counter(min(10, len({id(st) for s, e, st in a["cov"]["OWNER"] if st})) for a in A)
people_touch = [len({id(st) for lab, iv in a["cov"].items() for s, e, st in iv if st}) for a in A]
summary = dict(accounts=len(A), partners=len(W.PARTNERS), products=len(CAT.PRODUCTS), employees_in_org=len(W.PEOPLE),
               segment_true_FY26=dict(true_seg), segment_recorded_FY26=dict(seg26), status_true_at_snapshot=dict(status), never_purchased=never,
               canada_accounts=sum(1 for a in A if a["country"] == "Canada"), accounts_changed_segment=moved,
               owners_per_account_5yr=dict(sorted(owners.items())), avg_people_touching_account=round(sum(people_touch) / len(A), 1),
               max_people_touching_account=max(people_touch), revenue_usd_millions_by_FY=rev, families=sum(1 for a in A if a["role"] == "parent"),
               subsidiaries=sum(1 for a in A if a["role"] == "subsidiary"), unlinked_subsidiaries=sum(1 for a in A if a.get("unlinked") and not a.get("linked_on")),
               showcase={k: dict(account_id=v["id"], name=v["legal"]) for k, v in W.SHOWCASE.items()}, row_counts=counts, planted_issues=issues,
               runtime_sec=round(time.time() - t0))
with open(os.path.join(root, "answer_key", "generation_summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)
tot_bytes = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(root) for fn in fns)
log(f"done: {sum(counts.values()):,} rows across {len(counts)} files, {tot_bytes / 1e6:,.0f} MB")
print(json.dumps({k: summary[k] for k in ("segment_true_FY26", "status_true_at_snapshot", "never_purchased", "revenue_usd_millions_by_FY",
                                           "accounts_changed_segment", "owners_per_account_5yr", "avg_people_touching_account")}, indent=1))
