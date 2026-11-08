# Orvane Technologies - Synthetic CRM + ERP Dataset (V3, 10,000 accounts - full build)

All companies, people, products, emails and phone numbers are fictional. Orvane Technologies is a made-up North American
hardware + infrastructure + services vendor. Data covers **FY22-FY26** (fiscal year = Feb 1 - Jan 31; Feb 1 2021 - Jan 31 2026),
snapshot taken **2026-01-31**, plus summarized pre-Salesforce history back to FY17.

## What to load into Aible
Everything in `aible_load/`:

| File | Rows | What it is |
|---|---:|---|
| `orvane_unified_timeline.csv` | 12,482,969 | **The single CSV.** One row per event (order, order line, payment, invoice issue, shipment exception, opportunity created/closed, call, email, meeting, note, chatter, support case, survey, telemetry alert, advisory exposure, campaign response, lead, intent surge, news, consumer purchase, owner/segment change), each carrying account context *as recorded at the time* (segment, coverage status, region, owner, employees, revenue). Free text in `text`; type-specific fields in `details_json`. 6,460 MB. |
| `tables/*.csv` | | 57 relational tables (Salesforce objects + ERP + install base) with every field - join on `Id` / `...Id` / `Order_Number` / `Customer_Number`. 8,425 MB. |

**Do NOT load `answer_key/`** - it contains the ground truth and the list of every planted data problem, so you can score
whether the cleanup and the agents actually found them.

## Shape of the data
- **Accounts:** 10,000 customers/prospects + 5 channel partners. Segment at FY26 (true): Select 100, Large Enterprise 3104,
  Medium Business 4347, Small Business 2449. Canada 426 accounts (~5%).
- **Status at snapshot (true, from last purchase):** Retention 5803, Development 2395, Acquisition 1802
  (of which 1095 have never bought). Rules: bought in last 12 months = Retention; 1-3 years = Development; 3+ years or never = Acquisition.
- **Lifecycle movement:** 1547 accounts changed segment during the five years (startups growing SB -> MB -> LE, decliners moving down, Select accounts entering/leaving the top 100).
- **Hierarchies:** 450 parent companies with 2033 subsidiaries; 460 subsidiaries are not linked to their parent in CRM.
- **Sales org:** 2431 Orvane employees over five years with heavy turnover. On average **21.2 different Orvane people** touched each account
  (max 54). Owners per account over 5 years: {'2': 933, '3': 2555, '4': 3177, '5': 2068, '6': 986, '7': 260, '8': 20, '9': 1}.
- **Products:** 500 fictional SKUs (Aster/Bastion/Cadence/Forge/Wisp/Clarity/Tether/Nova client lines; Atlas servers incl. AI; Converge HCI; Strata storage;
  Vault data protection; Mesh networking; Outpost edge; software; ProCare support; deployment/consulting services; Flex and Device-as-a-Service).
- **Revenue by FY (USD M, all channels):** {'22': 13729.4, '23': 13797.9, '24': 13782.4, '25': 17786.7, '26': 19664.8} - a FY23-24 PC slump, then an AI-server and Windows 11 refresh wave.
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
- **select family misrouting** - Magnolia Mesa Products Holdings (`0015f00004TTh8VAAT`)
- **storage capacity crunch** - Meadow Trail Public Works (`0015f00004TWGVZAA5`)
- **champion left mid deal** - Luxium Precision Corporation (`0015f00004TWjCKAA1`)
- **headcount jump flat pc spend** - CPM Precision Co. (`0015f00004TYN6yAAH`)
- **missed po credit hold** - Zenara Co. (`0015f00004TYdWgAAL`)
- **rep carousel partner conflict** - Lake Valley Engineering Inc (`0015f00004Tbf4xAAB`)
- **security advisory exposure** - Falcon College (`0015f00004TXOLpAAP`)
- **ai reacquisition** - Peterson & Kennedy Utilities Group, Inc. (`0015f00004TaVL6AAN`)
- **consumer to mb journey** - Meadow Port Products L.P. (`0015f00004TbCWbAAN`)
- **lease end refresh** - Juniper Crossing Systems Inc. (`0015f00004Tcu17AAB`)

V3 is built on the V2 sample: the same 500 companies (names, IDs, contacts, reps, coverage history, storylines and hand-written notes) plus 9,500 more. Their order/opportunity histories were regenerated inside the larger world.

See `DATA_DICTIONARY.md` for every table and column. Regenerate with `generator/main.py --accounts N --out <folder>`.
