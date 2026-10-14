# Schema and engine experiments: full profile

5,000,000 requests from NYC 311. The whole grid of four models was measured 3 times (1 warm-up and 10 measured runs per query and model each time). Generated 2026-10-14T22:09:21Z.

Every model returns the same rows for every query (verified before measuring).

## Median time per model (ms)

Median across repetitions, with the spread (minimum-maximum) and the coefficient of variation in parentheses.

| Query | Normalized on PostgreSQL | Star on PostgreSQL | Normalized on DuckDB | Star on DuckDB |
|---|---:|---:|---:|---:|
| `q1` | 2,486.1 (2,408.5-2,658.4, CV 5.1%) | 936.0 (880.1-936.9, CV 3.5%) | 38.5 (37.9-43.6, CV 7.7%) | 31.9 (30.2-34.2, CV 6.3%) |
| `q2` | 1,485.4 (1,276.0-1,524.7, CV 9.4%) | 939.7 (815.1-1,173.7, CV 18.7%) | 41.3 (29.8-49.0, CV 24.2%) | 33.3 (24.7-33.8, CV 16.8%) |
| `q3` | 730.7 (685.0-743.6, CV 4.3%) | 706.6 (652.0-1,043.0, CV 26.5%) | 28.5 (21.9-45.4, CV 37.9%) | 17.6 (11.6-24.0, CV 35.0%) |
| `q4` | 4,916.9 (4,606.0-5,593.8, CV 10.0%) | 4,182.8 (4,172.8-4,362.2, CV 2.5%) | 45.2 (42.4-47.2, CV 5.4%) | 36.1 (33.2-36.6, CV 5.2%) |
| `q5` | 1,164.1 (1,155.0-1,186.0, CV 1.4%) | 144.6 (143.8-159.1, CV 5.8%) | 6.4 (5.8-6.7, CV 7.6%) | 5.0 (5.0-5.7, CV 8.3%) |
| `q6` | 2,059.2 (2,024.2-2,086.5, CV 1.5%) | 592.1 (589.1-630.2, CV 3.8%) | 17.0 (15.6-18.2, CV 7.6%) | 14.4 (12.9-16.7, CV 13.0%) |

## What explains the speedup

Each value is how many times faster the second factor makes the same query, as the median across repetitions with the minimum-maximum in parentheses. *Engine* compares PostgreSQL with DuckDB on the same schema; *schema* compares the normalized model with the star schema on the same engine.

| Query | Engine (normalized) | Engine (star) | Schema (PostgreSQL) | Schema (DuckDB) | Combined (official) |
|---|---:|---:|---:|---:|---:|
| `q1` | 64.5x (55.3-70.2) | 27.6x (27.4-31.0) | 2.8x (2.6-2.8) | 1.3x (1.2-1.3) | 77.8x (70.5-88.1) |
| `q2` | 36.9x (30.3-42.8) | 33.0x (28.2-34.7) | 1.6x (1.3-1.6) | 1.2x (1.2-1.4) | 45.8x (43.9-51.7) |
| `q3` | 25.6x (16.4-31.2) | 43.5x (40.2-56.3) | 1.0x (0.7-1.1) | 1.9x (1.6-1.9) | 41.6x (31.0-59.1) |
| `q4` | 108.7x (104.2-123.7) | 120.8x (114.4-125.7) | 1.1x (1.1-1.3) | 1.3x (1.2-1.4) | 136.2x (126.0-168.5) |
| `q5` | 185.4x (171.4-201.1) | 28.9x (27.8-29.2) | 8.0x (7.5-8.1) | 1.2x (1.1-1.4) | 233.2x (207.4-233.6) |
| `q6` | 119.1x (113.4-133.7) | 41.0x (37.8-46.0) | 3.5x (3.2-3.5) | 1.2x (1.0-1.3) | 143.5x (121.5-162.0) |

## Repeatability

16 of 24 series (one per query and model) kept their medians within 20% across repetitions (maximum minus minimum, over the median). The widest spread was 82.3%.

## Method

- Timer: perf_counter, execute + full fetch, measured from the client.
- Models: normalized (3NF) and star schema, each on PostgreSQL 17 and on DuckDB. The star schema in PostgreSQL has a primary key on every table and an index per foreign key of the fact table, like the normalized model; both DuckDB models store the fact table in creation order.
- Queries are the same business questions as the official benchmark, written in each engine's dialect (`sql/controls/`).
- Official numbers: `results/benchmark_full.md`. This run does not change them.
