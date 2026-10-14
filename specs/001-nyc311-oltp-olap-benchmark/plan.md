# Implementation Plan: OLTP vs OLAP Benchmark on NYC 311

**Branch**: `001-nyc311-oltp-olap-benchmark` | **Date**: 2026-10-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-nyc311-oltp-olap-benchmark/spec.md`

**Status**: Approved (2026-10-12) — the human approved DuckDB as the OLAP engine and the two
new runtime dependencies, `duckdb` and `psycopg[binary]` (constitution principle V).

## Summary

Load a fixed, ordered cut of NYC 311 service requests from the Socrata API into PostgreSQL
through a resumable staging step; build a normalized OLTP model from it and, from that, a
star schema in an embedded columnar engine; run six analytical queries with the same logic on
both; and publish timings (median, p95, speedup) in `results/`. Integration tests prove that
both models hold the same requests and that every query returns equivalent results. Two
profiles share the whole pipeline and differ only in volume: full (5,000,000 rows, official
results) and quick (200,000 rows, for evaluators).

## Technical Context

**Language/Version**: Python 3.12+ (developed on 3.13.9)  
**Primary Dependencies**: `psycopg[binary]` 3.x and `duckdb` 1.5.x (both approved);
standard library for HTTP (`urllib`), CLI (`argparse`) and statistics  
**Storage**: PostgreSQL 17 via `docker compose` on port 5433 (staging and OLTP schemas);
DuckDB file `data/olap.duckdb` (star schema, git-ignored)  
**Testing**: pytest — unit tests plus integration tests against real PostgreSQL and DuckDB  
**Target Platform**: a developer laptop (macOS or Linux) with Docker; measured on Apple M1
Pro, 10 cores, 16 GB RAM  
**Project Type**: command-line data pipeline and benchmark  
**Performance Goals**: full profile prepared in under 1 hour (SC-002); quick profile end to
end in under 10 minutes (SC-008); OLAP at least 3x faster on the median in two thirds of the
analytical queries (SC-003) — the last one is an outcome to measure, not to engineer  
**Constraints**: API page size 50,000; sequential requests with an app token; no dependency
beyond the approved ones; `DESIGN.md` limited to 2 pages; everything in English  
**Scale/Scope**: 5,000,000 fact rows; 7 OLTP tables; 6 dimensions and 1 fact table; 6
analytical queries plus 2 optional transactional operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|---|---|---|
| I. Spec-Driven Development | Spec approved before this plan; implementation waits for plan approval and generated tasks | PASS |
| II. Benchmark Integrity | Significance is computed and reported by `run`, never enforced; exit code 0 either way; no tuning step exists to chase the threshold | PASS |
| III. Fair Comparison | One load feeds both models; identical query logic and parameters; default engine settings recorded in the results; schema-vs-engine and in-process-vs-TCP caveats documented in research R4 | PASS |
| IV. Verifiable Quality | Integration tests in `tests/integration/` run against real databases; ruff enforced by the commit hook | PASS |
| V. Simplicity and Bounded Scope | Two new runtime dependencies, both justified in research R5 | PASS (approved 2026-10-12) |
| VI. Traceability | One commit per task, explicit `git add`, no push | PASS |
| VII. Responsible Ingestion | App token from the environment, sequential requests, backoff on 429/5xx, idempotent and resumable staging | PASS |

**Post-design re-check (after Phase 1)**: no new violations. The design adds a staging schema
and a seventh table (`dim_status`) beyond what the spec names; both are justified in
[data-model.md](./data-model.md) and neither adds a dependency.

## Project Structure

### Documentation (this feature)

```text
specs/001-nyc311-oltp-olap-benchmark/
├── plan.md              # this file
├── research.md          # Phase 0: decisions, verified facts, open items
├── data-model.md        # Phase 1: staging, OLTP and OLAP models, parity invariants
├── quickstart.md        # Phase 1: end-to-end validation guide
├── contracts/
│   ├── cli.md           # commands, configuration, exit codes, retry policy
│   ├── queries.md       # the benchmark queries and equivalence rules
│   └── results-schema.md# format of the files in results/
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2, created by /speckit-tasks
```

### Source Code (repository root)

```text
benchmark.py                 # entry point (the "benchmark script" deliverable)
Makefile                     # up, install, bench, test, lint
pyproject.toml               # package metadata, dependencies, ruff and pytest config
.env.example
docker-compose.yml           # exists: PostgreSQL 17

src/nyc311_bench/
├── cli.py                   # argument parsing, command dispatch, exit codes
├── config.py                # environment variables, profiles, data cut
├── db.py                    # connections to both engines, SQL file loader
├── socrata.py               # paginated client: keyset, retries, backoff
├── ingest.py                # API pages -> staging, checkpoint, rejected rows
├── oltp.py                  # staging -> normalized model
├── olap.py                  # OLTP -> star schema in DuckDB
├── queries.py               # query registry: id, question, group, SQL file pair
├── runner.py                # parity guard, warm-up, timing, statistics
└── report.py                # JSON and Markdown results, significance verdict

sql/
├── staging/schema.sql
├── oltp/schema.sql          # tables; indexes.sql is applied after load.sql
├── oltp/load.sql
├── oltp/indexes.sql
├── oltp/q1_….sql … q6_….sql
├── olap/schema.sql
├── olap/load.sql
└── olap/q1_….sql … q6_….sql

tests/
├── fixtures/                # small sample of source rows, including edge cases
├── unit/                    # cursor logic, row parsing, statistics, report rendering
└── integration/             # parity of models, equivalence of every query

results/                     # benchmark_<profile>.json and .md

README.md  DESIGN.md  AI_WORKFLOW.md
```

**Structure Decision**: a single Python package under `src/` with SQL kept in `.sql` files
rather than in strings. The queries are the subject of the benchmark, so an evaluator should
be able to read each pair side by side without reading Python.

## Implementation Approach

Order follows the spec's priorities; each stage is independently testable.

1. **Foundation**: `pyproject.toml`, `Makefile`, `.env.example`, configuration and profiles,
   the three schemas.
2. **User Story 1 — load**: Socrata client, staging with checkpoint, OLTP build, OLAP build,
   and the parity integration tests. Confirms the open items in research (keyset predicate,
   `unique_key` form, agency key).
3. **User Story 2 — measure**: the six query pairs, the runner, the report, and the
   significance verdict.
4. **User Story 3 — verify**: equivalence integration tests for every query, on the fixture.
5. **Measurement**: quick profile, then full profile; commit `results/`. If SC-003 is not
   reached, stop and report (principle II).
6. **Documentation**: README, DESIGN (2 pages), AI_WORKFLOW; license check from research R8.
7. **User Story 4 — transactional operations**: done after the documentation phase, with
   the human's authorization. Measured only with `--include-transactional`.
8. **User Story 5 — schema versus engine** (added after the first official run, spec US5,
   FR-027, FR-028): see the section below.

## User Story 5 design (added after the first official run)

**Why**: the official comparison changes the schema and the engine at once (DESIGN.md names
this as its main limitation). Two control models complete a 2x2 grid:

| | PostgreSQL | DuckDB |
|---|---|---|
| Normalized | official OLTP model | control: `control_3nf.duckdb`, schema `oltp` |
| Star | control: schema `star_pg` | official OLAP model |

- `sql/controls/star_pg/` builds the star schema inside PostgreSQL from the OLTP tables, with a
  primary key on every table and an index per fact foreign key, like the normalized model.
- `sql/controls/3nf_duckdb/` holds the six queries for the normalized schema in DuckDB's
  dialect; `src/nyc311_bench/controls.py` copies the OLTP tables into a separate DuckDB file
  (postgres extension, `COPY` fallback), storing the fact table in creation order like the
  star fact table.
- `src/nyc311_bench/experiments.py` and the `experiments` subcommand verify that the four
  models return the same rows, measure the grid `--repeats` times (default 3) and write
  `results/experiments_<profile>.json` and `.md`. The official `benchmark_*.json/md` files
  are never touched.
- The controls are rebuilt on every run (about 25 seconds), so a control can never be stale.

**Constitution Check for this addition**: I (a spec section, FR-027/028 and tasks T058–T064
exist; this plan section was written after the implementation, which `/speckit-analyze` flagged
as finding C1); II (nothing is tuned, equivalence verified before measuring); III (same
data, same logical queries, same harness); IV (unit and integration tests on the fixture); V
(two additional SQL schemas and one module, justified below); VI (reports state method and
repetitions); VII (no new API access).

**Complexity Tracking**

| Addition | Why it is needed | Simpler alternative rejected |
|---|---|---|
| Two control models and 12 dialect-specific query files | the only way to attribute the speedup to schema or engine | arguing it from first principles, which is not a measurement |
| Repeated grid with a repeatability count | SC-006 could not be judged from single runs | quoting one run |

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| SoQL rejects the compound keyset predicate | pagination design changes | fall back to `$offset` with the same `$order`; checkpoint becomes the offset |
| Download slower than estimated | SC-002 missed | measure on the quick profile first; report rather than relax the criterion |
| DuckDB `postgres` extension cannot be downloaded | OLAP build fails | stream each table out with `COPY` and insert from Python |
| SC-003 not reached | benchmark not significant | stop and report; do not tune |
| NYC Open Data terms forbid committing sample rows | fixture cannot be real data | generate the fixture synthetically |
| Engine defaults favor one side (parallelism) | fairness questioned | record settings in the results and discuss in DESIGN.md |

## Complexity Tracking

No constitution violations. The two new dependencies, approved by the human on 2026-10-12:

| Item | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| New dependency `duckdb` | a columnar engine is what makes the OLAP side analytical | a star schema inside PostgreSQL stays row-oriented and measures the schema alone |
| New dependency `psycopg[binary]` | no PostgreSQL driver exists in the standard library | shelling out to `psql` for loads and timed queries would distort the measurements |
