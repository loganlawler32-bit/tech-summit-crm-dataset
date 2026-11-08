# Tech Summit synthetic CRM + ERP datasets (V1-V4)

Fake but realistic sales data built for the Tech Summit demo: load it into Aible, have it cleanse the data, and build agents and
workforce automations for highly technical salespeople. **Everything is fictional** - companies, people, emails, phone numbers and
products. No real customer data is included.

| Version | What it is | Accounts | Rows | Uncompressed |
|---|---|---:|---:|---:|
| **V1** | First, simpler version: Salesforce CRM only, for "Altura Cloud Systems" (B2B software), CY2021-2025 | 12,000 | 1.2M | 0.6 GB |
| **V2** | Messy CRM + ERP + install base for "Orvane Technologies" (fictional PC + infrastructure vendor), FY22-FY26 (Feb-Jan), 500-account sample | 500 | 2.7M | 0.6 GB |
| **V3** | V2's 500 companies grown to 10,000 | 10,000 | 63.3M | 14 GB |
| **V4** | V3's 10,000 companies grown to 20,000 | 20,000 | 108.3M | 25 GB |

V2-V4 are deliberately messy: rep churn, vacancies and misrouted coverage, segment moves (SB -> MB -> LE -> Select), parent/subsidiary
hierarchies with unlinked subsidiaries, account renames, duplicate accounts and contacts, missing/placeholder POs, credit holds, short
pays, discounts without approval, a botched merge of an acquired rival ("Quillon"), 5 channel partners, ~5% Canada, ~500 SKUs,
call logs, emails, meeting notes, support cases, telemetry and security advisories. Every planted problem is listed in that version's
answer key. 10 showcase accounts carry hand-written storylines (same companies in V2, V3 and V4).

## What's in this repo
- `v1/` - README, data summary and the generator script.
- `v2/`, `v3/`, `v4/` - README, full `DATA_DICTIONARY.md`, `answer_key/README.md` + `generation_summary.json`, and the `generator/`
  (pure Python 3 standard library) including the hand-written showcase notes.

The data files themselves are too big for git (GitHub caps files at 100 MB), so they are attached to **GitHub Releases**:

| Release | Contents | Files | Compressed |
|---|---|---|---:|
| [v1-data](https://github.com/loganlawler32-bit/tech-summit-crm-dataset/releases/tag/v1-data) | V1 - all 17 CSVs + SQLite database | `v1-salesforce-crm.tar.gz` | 0.13 GB |
| [v2-data](https://github.com/loganlawler32-bit/tech-summit-crm-dataset/releases/tag/v2-data) | V2 - 500-account sample: unified timeline + 57 tables | `v2-sample500-aible_load.tar.gz` | 0.14 GB |
| [v2-data](https://github.com/loganlawler32-bit/tech-summit-crm-dataset/releases/tag/v2-data) | V2 - answer key (do not load into Aible) | `v2-sample500-answer_key.tar.gz` | 0.00 GB |
| [v3-data](https://github.com/loganlawler32-bit/tech-summit-crm-dataset/releases/tag/v3-data) | V3 - 10,000 accounts: unified timeline + 57 tables | `v3-aible_load.tar.gz.001` … `.002` (2 parts) | 3.28 GB |
| [v3-data](https://github.com/loganlawler32-bit/tech-summit-crm-dataset/releases/tag/v3-data) | V3 - answer key (do not load into Aible) | `v3-answer_key.tar.gz` | 0.01 GB |
| [v4-data](https://github.com/loganlawler32-bit/tech-summit-crm-dataset/releases/tag/v4-data) | V4 - 20,000 accounts: unified timeline + 57 tables | `v4-aible_load.tar.gz.001` … `.003` (3 parts) | 5.81 GB |
| [v4-data](https://github.com/loganlawler32-bit/tech-summit-crm-dataset/releases/tag/v4-data) | V4 - answer key (do not load into Aible) | `v4-answer_key.tar.gz` | 0.03 GB |

Each release has a `SHA256SUMS-vN.txt` checksum file.

## Downloading and unpacking
Single files are ordinary `.tar.gz` archives. Large ones are split into numbered parts - download **all** parts of an archive into one folder, then:

```bash
cat v4-aible_load.tar.gz.* | tar -xzf -
```

On Windows, open the `.001` file with 7-Zip (it reads the other parts automatically), then extract the `.tar` inside.
With the GitHub CLI you can fetch a whole release at once: `gh release download v4-data -R loganlawler32-bit/tech-summit-crm-dataset`.

## What to load into Aible
For V2-V4, load `aible_load/` only: `orvane_unified_timeline.csv` (the single CSV - one row per event with account context as recorded
at the time) plus `tables/` (57 relational tables). **Keep `answer_key/` out of Aible** - it holds the ground truth and the list of every
planted data problem, so you can score whether the cleanup and agents found them.

## Regenerating
```bash
cd v4/generator
python3 main.py --accounts 20000 --base-accounts 500 --grow-through 10000 --out ../out_v4   # ~55 min
python3 ingest_notes.py ../out_v4 showcase_notes_v4 && python3 docs.py ../out_v4
```
(V3: `--accounts 10000 --base-accounts 500`; V2: `--accounts 500`.) A rebuild produces an equivalent dataset; the published files also
include a few small post-build date corrections, so they are not byte-identical to a fresh run.
