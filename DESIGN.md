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

## Dashboard

A React SPA (Clean Architecture) reads `results/benchmark_full.json` and renders the
speedup chart, per-query table, execution plans, and environment card. An optional
stdlib-only API server (`dashboard/api_server.py`, port 8788) runs `benchmark.py run`
as a subprocess, copies the updated JSON to `dashboard/public/`, and returns the fresh
data to the browser in a single POST — no page reload. The static JSON is the
authoritative source; the dashboard degrades gracefully when the server is not running.

## Alternatives considered

**Data source.** Fifteen public APIs were evaluated in two research rounds. Chicago Crimes
(8.6 M rows) was a strong candidate but offered less volume; openFDA (20 M reports) imposed
strict rate limits (240/min); USGS earthquakes had only 712 K rows; GitHub events provided
no historical backfill. NYC 311 won on volume (22.7 M rows), API quality (pages of 50,000,
no throttling with an app token), and natural analytical dimensions (agency, complaint type,
borough, channel, time).

**OLAP engine.** DuckDB was chosen over ClickHouse (requires a running server and adds
operational complexity) and PostgreSQL materialized views (same row-oriented engine, so the
columnar advantage would not be visible). DuckDB is embedded, columnar, and needs no
infrastructure beyond a single file.

## Scaling to 10x

With 50,000,000 rows the main changes would be:

- **Ingestion.** Parallel page fetching (currently sequential to respect the API) and chunked
  staging inserts. The current 27-minute load would grow to roughly 4–5 hours without
  parallelism.
- **PostgreSQL.** Tuning becomes mandatory: `shared_buffers` to 4+ GB, `work_mem` to 256 MB+,
  `effective_cache_size` sized to available RAM. Table partitioning on `created_at` (monthly
  ranges) would keep index sizes manageable. The q5 anomaly (9 ms → 1,018 ms at 5 M)
  suggests query plans degrade under default settings at scale.
- **DuckDB.** Likely still fast — columnar engines handle analytical scans well at this
  scale — but `memory_limit` may need to grow beyond 12.7 GiB.
- **Pipeline.** Add a data-validation step and consider Parquet as an intermediate format for
  portability between engines.
- **Benchmark.** Add concurrent-user simulation to test contention, and include the
  transactional operations (US4) to show the side of the trade-off where OLTP wins.

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
