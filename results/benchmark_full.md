# Benchmark results: full profile

5,000,000 requests from NYC 311 Service Requests (erm2-nwe9), created 2024-01-01T00:00:00 to 2025-06-10T09:03:00. Generated 2026-10-13T01:17:45Z.

## Analytical queries

Times in milliseconds: median, with the 95th percentile in parentheses.

| Query | Question | OLTP (PostgreSQL) | OLAP (DuckDB) | Winner |
|---|---|---:|---:|---|
| `q1` | How many requests of each complaint type were created per month in each borough? | 2,373.8 (2,390.2) | 28.1 (30.1) | OLAP, 84.6x faster |
| `q2` | For each ZIP code, which are the 10 most frequent complaint types and how long do they take to resolve on average? | 1,260.2 (1,267.0) | 22.8 (25.4) | OLAP, 55.3x faster |
| `q3` | What share of requests does each agency close within 30 days, by channel? | 692.3 (695.8) | 11.6 (15.3) | OLAP, 59.9x faster |
| `q4` | What is the 90th percentile of resolution time per agency and quarter? | 4,419.2 (4,444.8) | 32.2 (35.7) | OLAP, 137.2x faster |
| `q5` | In Brooklyn, when do noise complaints concentrate, by day of week and hour? | 1,018.5 (1,030.0) | 5.5 (8.1) | OLAP, 183.7x faster |
| `q6` | How is each quarter's volume split across channels? | 1,989.4 (1,998.2) | 12.2 (17.0) | OLAP, 163.3x faster |

## Verdict

**Significance threshold reached.** 6 of 6 analytical queries are at least 3x faster on the OLAP model. Rule: OLAP at least 3x faster on the median in at least two thirds of analytical queries.

## Method

- 1 discarded warm-up run(s), then 10 measured runs per query and model; the 95th percentile is taken over those 10 runs.
- Timer: perf_counter, execute + full fetch, measured from the client.
- For each query, all runs on one model and then all runs on the other; nothing else running concurrently.
- The difference combines two effects: the schema (normalized vs star) and the storage engine (row vs columnar).

## Environment

- Machine: arm, 10 cores, 16.0 GB RAM, macOS-27.0.1-arm64-arm-64bit-Mach-O
- Python 3.13.9
- PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) (docker container, reached over local TCP): max_parallel_workers_per_gather = 2, max_parallel_workers = 8, shared_buffers = 128MB, work_mem = 4MB, jit = on
- DuckDB 1.5.6 (embedded in the benchmark process): threads = 10, memory_limit = 12.7 GiB
