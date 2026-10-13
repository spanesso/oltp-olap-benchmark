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
| q1 | Requests per complaint type, month and borough | 2,373.8 | 28.1 | 84.6x |
| q2 | Top 10 complaint types per ZIP with avg resolution | 1,260.2 | 22.8 | 55.3x |
| q3 | Closure rate within 30 days by agency and channel | 692.3 | 11.6 | 59.9x |
| q4 | 90th percentile resolution time by agency and quarter | 4,419.2 | 32.2 | 137.2x |
| q5 | Noise complaints in Brooklyn by day of week and hour | 1,018.5 | 5.5 | 183.7x |
| q6 | Channel share of volume by quarter | 1,989.4 | 12.2 | 163.3x |

**Verdict**: significance threshold reached. All 6 analytical queries are at least 3x
faster on the OLAP model (rule: at least two thirds). Medians are repeatable within 10%
across consecutive runs.

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

A React dashboard reads `results/benchmark_full.json` and renders the speedup chart,
per-query detail table, execution plans, and environment card.

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
