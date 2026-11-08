"""Write README.md + DATA_DICTIONARY.md into an output folder; sort the unified timeline chronologically."""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from out import SCHEMA, TL_FIELDS

root = sys.argv[1]
K = os.path.join(root, "answer_key")
L = os.path.join(root, "aible_load")
S = json.load(open(os.path.join(K, "generation_summary.json")))


def count(path):
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in csv.reader(f)) - 1


# chronological sort of the unified timeline, chunked by fiscal quarter so multi-GB files never sit in memory at once
import tempfile
tl = os.path.join(L, "orvane_unified_timeline.csv")
tmpd = tempfile.mkdtemp(dir=L)
chunks = {}
n_rows = 0
with open(tl, encoding="utf-8", newline="") as f:
    rd = csv.reader(f)
    head = next(rd)
    i_ts, i_acct = head.index("event_timestamp"), head.index("account_id")
    for r in rd:
        k = (r[i_ts] or "0000-00")[:7]
        if k not in chunks:
            chunks[k] = open(os.path.join(tmpd, k + ".csv"), "w", encoding="utf-8", newline="")
        csv.writer(chunks[k]).writerow(r)
        n_rows += 1
for fh in chunks.values():
    fh.close()
with open(tl, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(head)
    for k in sorted(chunks):
        p_ = os.path.join(tmpd, k + ".csv")
        with open(p_, encoding="utf-8", newline="") as g:
            part = list(csv.reader(g))
        part.sort(key=lambda r: (r[i_ts] or "", r[i_acct] or ""))
        w.writerows(part)
        os.remove(p_)
os.rmdir(tmpd)
rows = range(n_rows)

DESC = {
    "Account": "Customer, prospect, partner and duplicate account records exactly as they sit in Salesforce at 2026-01-31 (stale segment/status fields, broken parent links, duplicate records, inconsistent formats).",
    "AccountHistory": "Field-change history: owner, segment, coverage status, region, name, parent, partner of record.",
    "AccountTeamMember": "Every Orvane person who covered the account and when (owner, inside AE, specialists, SA, TAM, RAM, SDM) with start/end dates.",
    "Account_Partner__c": "Channel partner of record over time.",
    "Account_Firmographics__c": "Yearly employees / revenue / IT budget / sites from a 3rd-party provider (lagged, sometimes stale) plus occasional rep-entered values that disagree.",
    "Account_Segment_History__c": "Segment, coverage status (Retention/Development/Acquisition), region, territory and assigned owner at each February realignment.",
    "Account_Environment__c": "Yearly technology environment: client OS / Windows 11 progress, hypervisor, cloud, ITSM, backup approach, estimated endpoints/servers/storage, competitor footprint, strategic initiatives.",
    "Contact": "Customer people incl. shared mailboxes (AP, purchasing, help desk); leavers often still marked Active; duplicates; reports-to chains; buying roles.",
    "ContactHistory": "Recorded title changes (many promotions were never recorded).",
    "Lead": "Inbound/marketing leads; many duplicate existing contacts or use inconsistent company names.",
    "User": "Orvane employees (sales, specialists, support, finance, marketing) with hire/termination dates; boomerang rehires create second user records.",
    "User_Role_History__c": "Every role/region stint per person: promotions (SB -> MB -> LE -> Select), FY24 restructure moves, terminations.",
    "Opportunity": "Won, lost, open and stale deals; owners vary by product group (AE vs specialist); legacy stage values from before FY24; pushes and original close dates.",
    "OpportunityHistory": "Stage/amount/close-date progression for each opportunity.",
    "OpportunityLineItem": "Products on each opportunity.",
    "OpportunityTeamMember": "Who worked each deal (owner, account owner, SA, inside AE, TAM, partner manager).",
    "OpportunitySplit": "Revenue and overlay credit splits (some over-allocated).",
    "Quote": "Quote versions per opportunity (discount tightening over versions, configuration errors).",
    "QuoteLineItem": "Lines on the final quote.",
    "Deal_Registration__c": "Partner deal registrations, approvals/rejections and conflicting registrations.",
    "Discount_Approval__c": "Discount approvals vs policy threshold (policy tightened in FY25); missing approvals are planted issues.",
    "Forecast_Submission__c": "Weekly commit/best-case/pipeline calls per rep per quarter (sandbaggers and happy-ears visible vs actuals).",
    "Quota__c": "Quarterly quota per quota-carrying rep with new-hire ramp.",
    "Task": "Calls (duration, disposition, direction) and emails (subject + body) written in each rep's own style; topics follow what is actually happening on the account.",
    "Event": "Meetings (discovery, demos, deep dives, architecture workshops, QBRs, exec briefings, negotiations) with attendees and meeting notes.",
    "Note": "Long-form notes: annual account plans, win reviews, hand-written showcase account notes.",
    "FeedItem": "Internal chatter posts about accounts (handoffs, champion changes, escalations, partner conflicts).",
    "Case": "Support cases tied to installed assets: priority, SLA, dispatch, escalation, resolution time.",
    "CaseComment": "Support engineer / customer case comments with log snippets and part numbers.",
    "Survey_Response__c": "Post-case NPS/CSAT with verbatims.",
    "Campaign": "Orvane Tech Summit (5 years), regional roadshows, webinars, Select Executive Forum, Windows 10 end-of-support program.",
    "CampaignMember": "Contact invitations/attendance with session interests.",
    "Web_Intent_Signal__c": "Monthly web/3rd-party intent by topic (leading indicator before purchases).",
    "News_Item__c": "News about customer companies (funding, layoffs, acquisitions, exec hires, HQ moves, rebrands, cyber incidents, bankruptcies).",
    "ERP_Customer": "ERP customer master (sold-to numbers; duplicates; Quillon legacy customers; names that differ from CRM).",
    "ERP_Ship_To": "Ship-to sites per customer (incl. stale HQ after relocations).",
    "CRM_ERP_Crosswalk": "Mapping between CRM accounts and ERP customer numbers - incomplete and partly wrong on purpose.",
    "Sales_Order": "Every order: channel (field/inside/online/portal/partner), PO numbers (messy), holds (missing PO, credit), payment method, currency, contract pricing applied or not.",
    "Sales_Order_Line": "Order lines with list, net price, discount, cost and margin, promised vs ship dates.",
    "Shipment": "Shipments with carriers, delays, damage, address exceptions, backorders after the snapshot.",
    "Invoice": "Invoices with tax, balances, past-due/disputed/written-off status, dunning level, days to pay.",
    "Payment": "Payments: ACH, wire, check, card, partner remittance, lease funding; short-pays and unapplied cash.",
    "Credit_Memo": "Returns and price-adjustment credits.",
    "RMA": "Return authorizations with reasons and disposition.",
    "Credit_Hold_Event": "Credit holds with open AR at hold and release info.",
    "Contract_Pricing_Agreement": "Parent-level master agreements by category (should apply to subsidiaries - often doesn't).",
    "Lease_Contract": "Orvane Financial Services leases with term end dates and end-of-term options.",
    "Flex_Usage_Monthly": "Pay-per-use (Orvane Flex) and Device-as-a-Service monthly committed vs used vs overage.",
    "Legacy_Order_Summary": "Pre-Salesforce order history FY17-FY21 by category (Orvane legacy ERP and Quillon ERP).",
    "Consumer_Order": "Consumer web store and employee purchase program orders by people tied to business accounts (mostly not linked).",
    "Asset": "Installed base: serialized infrastructure (one row per system) and client device lots (serial ranges), install site, status, firmware, warranty end, end of support.",
    "ServiceContract": "Warranty / ProCare contracts per asset with start/end and status.",
    "Asset_Telemetry_Monthly__c": "Monthly phone-home telemetry for storage/backup/HCI arrays: capacity, used %, growth, alerts, firmware.",
    "Security_Advisory__c": "Product security advisories (BMC, firmware, storage OS).",
    "Advisory_Exposure__c": "Which installed systems were exposed to which advisory, and whether they were remediated.",
    "Product2": "500 Orvane SKUs: generations, launch/end-of-life, list price, cost %, specs.",
    "Price_History": "List price changes over time (shortage increases, PC-slump cuts, prior-generation markdowns).",
}
counts = S["row_counts"]
for n in list(counts):
    p = os.path.join(L, "tables", n + ".csv")
    if os.path.exists(p) and n in ("Task", "Event", "Note", "FeedItem"):
        counts[n] = count(p)
counts["orvane_unified_timeline"] = len(rows)
tot_mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(L) for f in fs) / 1e6
tl_mb = os.path.getsize(tl) / 1e6
seg = S["segment_true_FY26"]
st = S["status_true_at_snapshot"]
VER = "V3" if S["accounts"] >= 5000 else "V2"
KIND = "full build" if S["accounts"] >= 5000 else "sample"
readme = f"""# Orvane Technologies - Synthetic CRM + ERP Dataset ({VER}, {S['accounts']:,} accounts - {KIND})

All companies, people, products, emails and phone numbers are fictional. Orvane Technologies is a made-up North American
hardware + infrastructure + services vendor. Data covers **FY22-FY26** (fiscal year = Feb 1 - Jan 31; Feb 1 2021 - Jan 31 2026),
snapshot taken **2026-01-31**, plus summarized pre-Salesforce history back to FY17.

## What to load into Aible
Everything in `aible_load/`:

| File | Rows | What it is |
|---|---:|---|
| `orvane_unified_timeline.csv` | {counts['orvane_unified_timeline']:,} | **The single CSV.** One row per event (order, order line, payment, invoice issue, shipment exception, opportunity created/closed, call, email, meeting, note, chatter, support case, survey, telemetry alert, advisory exposure, campaign response, lead, intent surge, news, consumer purchase, owner/segment change), each carrying account context *as recorded at the time* (segment, coverage status, region, owner, employees, revenue). Free text in `text`; type-specific fields in `details_json`. {tl_mb:,.0f} MB. |
| `tables/*.csv` | | {len(SCHEMA)} relational tables (Salesforce objects + ERP + install base) with every field - join on `Id` / `...Id` / `Order_Number` / `Customer_Number`. {tot_mb - tl_mb:,.0f} MB. |

**Do NOT load `answer_key/`** - it contains the ground truth and the list of every planted data problem, so you can score
whether the cleanup and the agents actually found them.

## Shape of the data
- **Accounts:** {S['accounts']:,} customers/prospects + {S['partners']} channel partners. Segment at FY26 (true): Select {seg.get('Select', 0)}, Large Enterprise {seg.get('Large Enterprise', 0)},
  Medium Business {seg.get('Medium Business', 0)}, Small Business {seg.get('Small Business', 0)}. Canada {S['canada_accounts']} accounts (~5%).
- **Status at snapshot (true, from last purchase):** Retention {st.get('Retention', 0)}, Development {st.get('Development', 0)}, Acquisition {st.get('Acquisition', 0)}
  (of which {S['never_purchased']} have never bought). Rules: bought in last 12 months = Retention; 1-3 years = Development; 3+ years or never = Acquisition.
- **Lifecycle movement:** {S['accounts_changed_segment']} accounts changed segment during the five years (startups growing SB -> MB -> LE, decliners moving down, Select accounts entering/leaving the top 100).
- **Hierarchies:** {S['families']} parent companies with {S['subsidiaries']} subsidiaries; {S['unlinked_subsidiaries']} subsidiaries are not linked to their parent in CRM.
- **Sales org:** {S['employees_in_org']} Orvane employees over five years with heavy turnover. On average **{S['avg_people_touching_account']} different Orvane people** touched each account
  (max {S['max_people_touching_account']}). Owners per account over 5 years: {S['owners_per_account_5yr']}.
- **Products:** {S['products']} fictional SKUs (Aster/Bastion/Cadence/Forge/Wisp/Clarity/Tether/Nova client lines; Atlas servers incl. AI; Converge HCI; Strata storage;
  Vault data protection; Mesh networking; Outpost edge; software; ProCare support; deployment/consulting services; Flex and Device-as-a-Service).
- **Revenue by FY (USD M, all channels):** {S['revenue_usd_millions_by_FY']} - a FY23-24 PC slump, then an AI-server and Windows 11 refresh wave.
- **Channel partners:** Summit Point Solutions, Crestline Technology Group, BlueHarbor IT, Ironclad Data Partners, Maplegrid Systems (Canada) - partners of record on ~25% of SB/MB
  accounts, sell into those accounts, register deals (sometimes the same deal twice), and buy for their own use.

## Built-in realism & mess (all on purpose)
- Segment/status/region fields are set once a year at February realignment and lag reality; FY24 restructure (US West / US East / Canada -> West / Central / East) left some old values behind.
- Reps leave mid-year; accounts sit vacant, with inactive owners, or in a holding queue; boomerang rehires get second user records; inside reps get promoted to field roles.
- Subsidiaries sold to as standalone accounts by the wrong team, without parent contract pricing (price leakage).
- Duplicate accounts and ERP customers (incl. a FY24 Q3 migration of an acquired rival's CRM/ERP, "Quillon"), an incomplete and partly wrong CRM<->ERP crosswalk.
- Missing / late / placeholder POs, PO-amount mismatches, blanket POs, credit holds, P-card style card payments, partner remittances, short-pays disputing discounts, unapplied cash, write-offs after bankruptcies.
- Contacts who left still marked Active, the same person reappearing at another customer, duplicate contacts, unrecorded promotions, shared mailboxes.
- Discounts above policy without approvals, over-allocated splits, stale open opportunities, $0 won deals, won deals with no order, orders not linked to opportunities.
- Rep-specific writing habits (shorthand, typos, late bulk logging, non-loggers), each rep's forecasting bias (sandbaggers vs. happy ears).
- Supply shortage FY22-23 (long lead times, partial shipments), firmware drift and unpatched security advisories, storage arrays filling up, leases and warranties expiring.

## Showcase accounts (deliberate storylines for demos)
{chr(10).join(f"- **{k.replace('_', ' ')}** - {v['name']} (`{v['account_id']}`)" for k, v in S['showcase'].items())}

{"V3 is built on the V2 sample: the same 500 companies (names, IDs, contacts, reps, coverage history, storylines and hand-written notes) plus 9,500 more. Their order/opportunity histories were regenerated inside the larger world." if VER == "V3" else ""}

See `DATA_DICTIONARY.md` for every table and column. Regenerate with `generator/main.py --accounts N --out <folder>`.
"""
open(os.path.join(root, "README.md"), "w").write(readme)

dd = ["# Data dictionary\n", "## `orvane_unified_timeline.csv` (the single CSV)\n",
      "| Column | Meaning |", "|---|---|"]
TLD = {"event_id": "Unique event id", "event_timestamp": "UTC timestamp", "event_date": "Date", "fiscal_year": "Orvane FY (Feb-Jan)", "fiscal_quarter": "Orvane fiscal quarter",
       "source_system": "CRM / ERP / Support / Telemetry / Product Security / Marketing / Survey / News / Consumer Store", "event_type": "Kind of event", "event_subtype": "Detail (disposition, status, category...)",
       "account_id": "CRM account (blank when the source system could not attribute it)", "account_name": "Name as recorded in that system at that time",
       "erp_customer_number": "Primary ERP customer number", "parent_account_id": "Parent as linked in CRM at the time (blank if not linked)",
       "parent_account_name": "", "ultimate_parent_name": "", "segment": "Segment as recorded for that fiscal year", "coverage_status": "Retention/Development/Acquisition as recorded at that FY's realignment",
       "sales_region": "Region label as recorded (old labels before FY24)", "industry": "Industry picklist value as recorded", "employees": "3rd-party employee count for that FY",
       "annual_revenue": "3rd-party revenue for that FY", "account_owner": "Who owned the account on that date (or vacancy label)", "rep_name": "Orvane person who did/owned the event",
       "rep_role": "Their role on the account", "partner_name": "Channel partner involved", "contact_name": "Customer person", "contact_title": "", "contact_email": "",
       "opportunity_id": "", "quote_number": "", "order_number": "", "invoice_number": "", "case_number": "", "asset_serial": "", "product_sku": "", "product_name": "",
       "product_family": "", "product_category": "", "quantity": "", "list_price": "", "unit_price": "Net price", "discount_pct": "", "amount": "Amount in record currency",
       "currency": "USD or CAD", "amount_usd": "", "po_number": "As typed (messy)", "payment_method": "", "status": "", "stage": "", "channel": "Direct - Field / Direct - Inside / Online Store / Premier Portal / Partner",
       "subject": "", "text": "Free text: notes, call summaries, email bodies, case comments, verbatims, news", "details_json": "Event-specific extra fields (JSON)",
       "record_table": "Source table in tables/", "record_id": "Source record id"}
for c in TL_FIELDS:
    dd.append(f"| `{c}` | {TLD.get(c, '')} |")
dd.append("\n## Relational tables (`tables/`)\n")
for n, cols in SCHEMA.items():
    dd.append(f"### `{n}` - {counts.get(n, 0):,} rows\n{DESC.get(n, '')}\n\nColumns: " + ", ".join(f"`{c}`" for c in cols) + "\n")
open(os.path.join(root, "DATA_DICTIONARY.md"), "w").write("\n".join(dd))
akr = """# Answer key - do NOT load into Aible

- `planted_issues.csv` - every deliberately planted data problem: issue type, table, record id, field, the recorded (wrong) value, the correct value, and a hint about how it can be detected.
- `golden_account_master.csv` - truth per account: real legal name now, true parent/ultimate parent, unlinked flag, duplicate CRM/ERP ids, Quillon legacy id, true segment per FY,
  true status at snapshot, true last purchase, employee trajectory, partner, acquired-by, renamed/bankrupt flags, showcase storyline.
- `golden_coverage_history.csv` - who truly covered each account in each role, with vacancies.
- `golden_contacts.csv` - true employment status of every contact, job moves between customers, true current title.
- `generation_summary.json` - counts and parameters of this generation run.
"""
open(os.path.join(K, "README.md"), "w").write(akr)
print("docs written;", f"timeline sorted ({len(rows):,} rows)")
