# Test fixtures

## `sample_311.json`

A **synthetic** sample of 2,004 rows shaped like the NYC 311 API response: every value is a
string and keys with no value are omitted. No row is real data. The repository commits no
real rows because the terms for redistributing the source data could not be verified (see
`specs/001-nyc311-oltp-olap-benchmark/research.md`, R8).

The file is produced by `generate_sample.py` with a fixed seed, so it can be regenerated
byte for byte:

```bash
python tests/fixtures/generate_sample.py
```

Rows are sorted by `(created_date, unique_key)`, the order the API is read in.

### Edge cases included

| Case | Rows | Expected handling |
|---|---|---|
| No `closed_date` (still open) | 120 | loaded; excluded from resolution measures |
| `closed_date` before `created_date` | 33 | loaded; flagged as invalid resolution |
| Missing `borough` | 31 | mapped to `Unknown` in both models |
| Missing `incident_zip` | 55 | mapped to `Unknown` in both models |
| Missing `open_data_channel_type` | 37 | mapped to `Unknown` in both models |
| Missing `descriptor` | 18 | mapped to `Unknown` in both models |
| One agency code with two names | several | two rows in the agency table |
| Missing `unique_key` | 1 | rejected |
| Non-numeric `unique_key` | 1 | rejected |
| Missing `created_date` | 1 | rejected |
| Unparseable `created_date` | 1 | rejected |

2,000 rows are valid and 4 must be rejected. Creation dates span January 2024 to June 2025
so that period aggregations have several groups, and 62 rows are noise complaints in
Brooklyn so that the filtered query returns data.
