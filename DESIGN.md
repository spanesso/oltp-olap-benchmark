# Design: OLTP vs OLAP Benchmark

## Pipeline

Data flows in one direction so both models derive from a single load:

```
NYC 311 API ──▶ staging.service_request_raw ──▶ oltp.* (PostgreSQL, 3NF) ──▶ star schema (DuckDB)
                (PostgreSQL, text columns)
```

API pages land in a staging table with all values as text and a checkpoint that makes the
load resumable and idempotent. From staging, a normalized OLTP model is built in PostgreSQL.
From the OLTP model, a denormalized star schema is built in DuckDB. Both models hold the
same requests; integration tests prove parity row by row.

## Data models

### OLTP — PostgreSQL, third normal form

Eight tables: `agency`, `complaint_type`, `complaint_descriptor`, `borough`, `location`,
`channel`, `status`, and the central `service_request`. Each descriptive value is stored
once and referenced by foreign key. No derived column is stored: resolution time is computed
in queries as `closed_at - created_at`. B-tree indexes cover every foreign key on
`service_request` and `created_at`, created after the bulk load.

### OLAP — DuckDB, star schema

Six dimensions (`dim_date`, `dim_agency`, `dim_complaint`, `dim_location`, `dim_channel`,
`dim_status`) and one fact table (`fact_service_request`). Dimensions are denormalized:
`dim_complaint` flattens type and descriptor, `dim_location` includes borough. The fact
table carries precomputed measures — `resolution_hours`, `is_closed`, `closed_within_30d`,
`created_hour` — that the OLTP side computes at query time. No indexes: columnar scans are
the idiomatic access path. Surrogate keys match OLTP identifiers so tests can compare the
two models row by row.

## Analytical queries

Six queries, each implemented as two SQL files (`sql/oltp/q*.sql` and `sql/olap/q*.sql`)
that must return equivalent rows:

| Query | Question |
|-------|----------|
| q1 | Volume by complaint type, month and borough |
| q2 | Top 10 complaint types per ZIP code with average resolution time |
| q3 | Share of requests closed within 30 days, by agency and channel |
| q4 | 90th percentile of resolution time by agency and quarter |
| q5 | Noise complaints in Brooklyn by day of week and hour |
| q6 | Channel share by quarter |

## Measurement method

Each query is measured identically on both models: 1 warm-up run (discarded) followed by 10
measured runs. Timing uses `time.perf_counter` around execute plus full fetch, which is what
an application would observe. For each query all runs execute on one model first, then on
the other; nothing else runs concurrently. Reported metrics are the median and the 95th
percentile over the 10 measured runs.

**Significance rule**: OLAP is at least 3× faster on the median in at least two thirds of
the analytical queries. The rule is evaluated only on the full profile (5,000,000 requests).

## Limitations

- **Engine defaults, not tuned.** PostgreSQL ran with the Docker image defaults
  (`shared_buffers` 128 MB, `work_mem` 4 MB, 2 parallel workers per gather) inside the
  Docker Desktop virtual machine. DuckDB ran natively with 10 threads and 12.7 GiB of
  memory. A tuned PostgreSQL would narrow the gap; by how much was not measured.
- **Schema and engine effects are combined.** The benchmark compares a normalized row-store
  model against a star-schema columnar model. It does not separate the contribution of the
  schema design from the contribution of the storage engine.
- **q5 anomaly.** On the OLTP side, q5 grew from 9 ms on 200,000 rows to 1,018 ms on
  5,000,000 rows — far more than the data growth. A query-plan change under the small
  default `work_mem` is the likely cause, but this was not investigated.
- **Single environment.** One machine (Apple M1 Pro, 10 cores, 16 GB), one run of each
  configuration, no concurrent users.
