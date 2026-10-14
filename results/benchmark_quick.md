# Benchmark results: quick profile

200,000 requests from NYC 311 Service Requests (erm2-nwe9), created 2024-01-01T00:00:00 to 2024-01-22T14:04:16. Generated 2026-10-13T00:47:07Z.

> **These are not the official timings.** This profile exists to check that everything works; the official results are in `benchmark_full.md`.

## Analytical queries

Times in milliseconds: median, with the 95th percentile in parentheses.

| Query | Question | OLTP (PostgreSQL) | OLAP (DuckDB) | Winner |
|---|---|---:|---:|---|
| `q1` | How many requests of each complaint type were created per month in each borough? | 85.0 (87.2) | 6.8 (8.8) | OLAP, 12.4x faster |
| `q2` | For each ZIP code, which are the 10 most frequent complaint types and how long do they take to resolve on average? | 120.4 (124.6) | 8.8 (11.3) | OLAP, 13.6x faster |
| `q3` | What share of requests does each agency close within 30 days, by channel? | 32.1 (33.4) | 4.0 (4.9) | OLAP, 8.1x faster |
| `q4` | What is the 90th percentile of resolution time per agency and quarter? | 193.2 (194.5) | 6.8 (8.6) | OLAP, 28.5x faster |
| `q5` | In Brooklyn, when do noise complaints concentrate, by day of week and hour? | 7.4 (8.6) | 2.0 (2.1) | OLAP, 3.7x faster |
| `q6` | How is each quarter's volume split across channels? | 139.7 (140.9) | 4.2 (5.4) | OLAP, 33.4x faster |

## Verdict

**Not evaluated on this profile.** 6 of 6 analytical queries are at least 3x faster on the OLAP model, but the significance threshold is only judged on the full profile.

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
