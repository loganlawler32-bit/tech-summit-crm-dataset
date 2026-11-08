# Answer key - do NOT load into Aible

- `planted_issues.csv` - every deliberately planted data problem: issue type, table, record id, field, the recorded (wrong) value, the correct value, and a hint about how it can be detected.
- `golden_account_master.csv` - truth per account: real legal name now, true parent/ultimate parent, unlinked flag, duplicate CRM/ERP ids, Quillon legacy id, true segment per FY,
  true status at snapshot, true last purchase, employee trajectory, partner, acquired-by, renamed/bankrupt flags, showcase storyline.
- `golden_coverage_history.csv` - who truly covered each account in each role, with vacancies.
- `golden_contacts.csv` - true employment status of every contact, job moves between customers, true current title.
- `generation_summary.json` - counts and parameters of this generation run.
