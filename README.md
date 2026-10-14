# OLTP vs OLAP Benchmark on NYC 311 Service Requests

A benchmark that loads NYC 311 service requests from the public Socrata API, builds a
normalized OLTP model in PostgreSQL and a star-schema OLAP model in DuckDB, runs six
analytical queries on both, and publishes compared timings. The goal is to show, with
measurable numbers, the performance difference between a transactional and an analytical
data model.

## Results

5,000,000 requests from NYC 311, measured on Apple M1 Pro (10 cores, 16 GB RAM).

| Query | Question | OLTP (ms) | OLAP (ms) | Speedup |
|-------|----------|----------:|----------:|---------|
| q1 | Requests per complaint type, month and borough | 4,334.1 | 86.0 | 50.4x |
| q2 | Top 10 complaint types per ZIP with avg resolution | 2,544.2 | 51.4 | 49.5x |
| q3 | Closure rate within 30 days by agency and channel | 907.4 | 19.2 | 47.3x |
| q4 | 90th percentile resolution time by agency and quarter | 4,997.3 | 40.6 | 123.1x |
| q5 | Noise complaints in Brooklyn by day of week and hour | 1,197.6 | 6.3 | 191.5x |
| q6 | Channel share of volume by quarter | 2,145.3 | 21.7 | 98.7x |

**Verdict**: significance threshold reached. All 6 analytical queries are at least 3x
faster on the OLAP model (rule: at least two thirds).

These are the numbers in `results/benchmark_full.json`. Absolute times move between runs
on a laptop that is also running other software (q1 on OLTP measured 2,374 ms, 2,486 ms,
3,489 ms and 4,334 ms across four full runs), but the speedup of the official run was above
47x on every query, and the lowest value seen in any repetition of any run was 31x (q3).

### Is it the schema or the engine?

The comparison above changes two things at once. To separate them, the same queries were
also run on the star schema inside PostgreSQL and on the normalized schema inside DuckDB.
All four models return identical rows, and the whole grid was measured three times
(`python benchmark.py experiments --profile full`, results in
[`results/experiments_full.md`](results/experiments_full.md)):

| Query | Engine alone (normalized schema) | Schema alone (on PostgreSQL) | Both (official) |
|---|---:|---:|---:|
| q1 | 64.5x | 2.8x | 77.8x |
| q2 | 36.9x | 1.6x | 45.8x |
| q3 | 25.6x | 1.0x | 41.6x |
| q4 | 108.7x | 1.1x | 136.2x |
| q5 | 185.4x | 8.0x | 233.2x |
| q6 | 119.1x | 3.5x | 143.5x |

Most of the speedup comes from the column-store engine. The star schema helps PostgreSQL
a lot on q5 (8x, because the hour and day are precomputed and the joins are fewer) and
barely at all on q3 and q4. Of the 24 series (query x model), 16 kept their medians within
20% across repetitions; the widest spread was 82% on a few-millisecond DuckDB query.

### Transactional operations

With `--include-transactional` the runner also measures the other side of the trade-off:

| Operation | OLTP (ms) | OLAP (ms) | Winner |
|---|---:|---:|---|
| Read one request by id (7 joins on OLTP, 5 on the star) | 2.14 | 4.13 | OLTP, 1.9x |
| Insert one request (rolled back) | 1.34 | 0.47 | OLAP, 2.9x |

OLTP wins the lookup, but by a much smaller margin than the analytical queries go the other
way. The insert is measured inside a transaction that is rolled back so the data set does
not change; that leaves out the commit (and its write to disk), which is where a
transactional engine earns its keep, so this number should not be read as "OLAP is better at
writes".

Full details, including per-run timings: [`results/benchmark_full.md`](results/benchmark_full.md).

## Quickstart

### Prerequisites

- Docker Desktop running.
- Python 3.12 or later.
- A free Socrata app token from [NYC Open Data](https://data.cityofnewyork.us), exported
  as `SOCRATA_APP_TOKEN` or placed in `.env` (copy from `.env.example`).

### Quick profile (verify everything works)

```bash
make up                      # start PostgreSQL 17 on port 5433
make install                 # create .venv and install dependencies
make bench PROFILE=quick     # load 200,000 requests, build both models, measure
make test                    # run unit and integration tests
```

The quick profile finishes in under 10 minutes. Its results warn that they are not the
official timings.

### Full profile (reproduce the official numbers)

```bash
make bench PROFILE=full
```

Optional extras, on top of a loaded full profile:

```bash
python benchmark.py run --profile full --include-transactional   # lookup and insert
python benchmark.py experiments --profile full                   # schema vs engine, 3 repeats
```

Downloads and loads 5,000,000 requests in about 27 minutes, then measures. The official
results are written to `results/benchmark_full.md`.

### Read the results without running anything

Open [`results/benchmark_full.md`](results/benchmark_full.md).

## How it works

```
NYC 311 API ──▶ staging (PostgreSQL) ──▶ OLTP model (PostgreSQL, 3NF) ──▶ OLAP model (DuckDB, star schema)
                                                                                │
                                                                         benchmark runner
                                                                                │
                                                                         results/ (JSON + Markdown)
```

1. **Ingest**: pages of up to 50,000 rows are fetched sequentially from the Socrata API
   with keyset pagination. Each page is committed to a staging table with a checkpoint, so
   the load is idempotent and resumable.
2. **Build OLTP**: the staging rows are normalized into eight tables in third normal form
   (agencies, complaint types, descriptors, boroughs, locations, channels, statuses, and
   service requests). No derived column is stored.
3. **Build OLAP**: the OLTP data is transformed into a star schema with six dimensions and
   one fact table. The fact table precomputes resolution hours, a closed-within-30-days
   flag, and other measures that the OLTP model computes at query time.
4. **Measure**: each of the six queries is executed on both models — 1 warm-up run
   (discarded) followed by 10 measured runs. Timing is client-side wall-clock around
   execute and full fetch.
5. **Report**: the runner writes a JSON file with every run and a Markdown summary with
   medians, 95th percentiles, speedup factors, and the significance verdict.

## Dashboard

A React dashboard reads `results/benchmark_full.json` (and `experiments_full.json` when it
exists) and renders the speedup chart, per-query detail table, the schema-vs-engine
breakdown, transactional operations, execution plans, and environment card.

```bash
cd dashboard && npm run dev        # http://localhost:5173
```

### Live re-measurement

An optional API server (standard library only, no extra dependencies) lets you re-run the
benchmark from the dashboard and refresh the displayed numbers without reloading the page.

```bash
# Terminal 1
make api           # starts http://localhost:8788

# Terminal 2
make dashboard     # starts http://localhost:5173
```

Click **"▶ Actualizar medición en vivo"** in the dashboard header. The server runs
`benchmark.py run --profile full`, copies the updated JSON to `dashboard/public/`, and the
dashboard shows the fresh numbers. On the next cold start the updated numbers load
automatically from the static file.

## Project structure

```
benchmark.py              CLI entry point
src/nyc311_bench/          package: config, db, ingest, oltp, olap, queries, runner, report
sql/
  staging/schema.sql       landing area for API pages
  oltp/                    normalized schema, indexes, and the 6 queries
  olap/                    star schema, load transform, and the 6 queries
tests/
  unit/                    fast tests (no database)
  integration/             tests against real PostgreSQL and DuckDB
  fixtures/                synthetic sample data (2,004 rows)
results/                   benchmark output (JSON and Markdown)
dashboard/                 React SPA + api_server.py (live re-measurement)
specs/                     specification, plan, research, data model, tasks
docker-compose.yml         PostgreSQL 17 on port 5433
Makefile                   up, install, bench, test, lint, api, dashboard
```

## Limitations

- PostgreSQL ran with the default settings of the official Docker image (`shared_buffers`
  128 MB, `work_mem` 4 MB) inside the Docker Desktop virtual machine. DuckDB ran natively
  with 10 threads. Neither engine was tuned.
- The measured difference combines two effects: the schema design (normalized vs star with
  precomputed measures) and the storage engine (row-oriented vs columnar). This benchmark
  does not separate the two.
- One machine, one configuration, no concurrent users.

## Data attribution

Data provided by [NYC Open Data](https://data.cityofnewyork.us) (NYC 311 Service
Requests, dataset `erm2-nwe9`). The repository commits no real data; the benchmark
downloads it from the public API.
