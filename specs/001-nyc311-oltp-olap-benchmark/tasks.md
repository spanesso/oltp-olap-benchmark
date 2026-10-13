# Tasks: OLTP vs OLAP Benchmark on NYC 311

**Input**: Design documents from `/specs/001-nyc311-oltp-olap-benchmark/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by constitution principle IV. Unit tests in `tests/unit/`; integration
tests in `tests/integration/` run against real PostgreSQL and DuckDB, never mocks.

**Organization**: Tasks are grouped by user story so each story can be implemented and
tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: the user story the task belongs to (US1 to US4)

## Rules for every task

- Atomic semantic commits, files added explicitly, no push. A commit may cover several task
  ids when they form one unit that is only testable together (for example a module and its
  tests); the message lists the ids.
- `ruff check` and `ruff format --check` must pass before the commit (enforced by the hook).
- Everything written is in English.
- If an error is not solved in 2 attempts, stop and report.
- Tasks marked **VERIFY** resolve an open item from research.md: record the finding in
  research.md, and if it contradicts the design, stop and report before continuing.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: project skeleton and tooling.

- [x] T001 Create `pyproject.toml` with package `nyc311_bench` under `src/`, Python `>=3.12`, runtime dependencies `psycopg[binary]>=3.2` and `duckdb>=1.4`, dev dependencies `pytest` and `ruff`, and the ruff and pytest configuration (pytest markers `integration` and `loaded`)
- [x] T002 Create the package skeleton: `src/nyc311_bench/__init__.py`, empty `tests/unit/__init__.py`, `tests/integration/__init__.py`, and directories `sql/staging/`, `sql/oltp/`, `sql/olap/`, `results/` (with `.gitkeep`)
- [x] T003 [P] Create `Makefile` with targets `up`, `install`, `bench` (with `PROFILE`, default `quick`), `test`, `lint`, as specified in contracts/cli.md
- [x] T004 [P] Create `.env.example` documenting `SOCRATA_APP_TOKEN`, the `POSTGRES_*` variables and `OLAP_PATH`, as specified in contracts/cli.md
- [x] T005 Install the project into `.venv` with `make install` and confirm `python -c "import duckdb, psycopg"` works (the two dependencies were approved by the human on 2026-10-12)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: configuration, connections, schemas, and the facts every story depends on.

**⚠️ CRITICAL**: no user story work starts until this phase is complete.

- [x] T006 Implement `src/nyc311_bench/config.py`: settings from environment variables with the defaults in contracts/cli.md, the profiles (`quick` = 200,000 rows, `full` = 5,000,000 rows), the data cut `[2024-01-01, 2026-01-01)`, and a redacting representation that never prints the token; unit tests in `tests/unit/test_config.py`
- [x] T007 Implement `src/nyc311_bench/db.py`: a PostgreSQL connection factory (psycopg) and a DuckDB connection factory, plus a helper that executes a `.sql` file from `sql/`; unit test for the SQL file loader in `tests/unit/test_db.py`
- [x] T008 **VERIFY** (research R8) Read the NYC Open Data terms of use at `https://www.nyc.gov/html/data/terms.html` through a read-only research subagent, record the relevant text and attribution requirement in `specs/001-nyc311-oltp-olap-benchmark/research.md`, and state whether committing a small sample of real rows is allowed
- [x] T009 **VERIFY** (research R3) With a real app token, request one page of 1,000 rows using `$select` of the 12 fields, `$order=created_date,unique_key` and the compound keyset predicate; confirm the predicate is accepted, that two consecutive pages do not overlap, and that every `unique_key` in the page is numeric; record the result in `specs/001-nyc311-oltp-olap-benchmark/research.md`
- [x] T010 Create `tests/fixtures/sample_311.json` with about 2,000 source rows (real rows from T009's cut if T008 allows it, otherwise synthetic rows with the same shape) including the edge cases: no `closed_date`, `closed_date` before `created_date`, missing `borough`, missing `incident_zip`, missing channel, and at least one row with a missing `unique_key`; document its origin in `tests/fixtures/README.md`
- [x] T011 [P] Write `sql/staging/schema.sql`: schema `staging` with `service_request_raw`, `ingest_checkpoint` and `rejected_row`, as specified in data-model.md section 1
- [x] T012 [P] Write `sql/oltp/schema.sql`: schema `oltp` with the eight tables, keys, foreign keys and indexes specified in data-model.md section 2
- [x] T013 [P] Write `sql/olap/schema.sql`: the six dimensions and `fact_service_request` specified in data-model.md section 3
- [x] T014 Create `tests/integration/conftest.py`: fixtures that create an isolated test database in the docker PostgreSQL and a temporary DuckDB file, apply the three schemas, and skip the `integration` tests with a clear message when PostgreSQL is not reachable

**Checkpoint**: configuration, schemas and test harness ready.

---

## Phase 3: User Story 1 - Load the same data into both models (Priority: P1) 🎯 MVP

**Goal**: the same requests end up in the normalized OLTP model and in the star schema,
through a load that is idempotent and resumable.

**Independent Test**: `python benchmark.py load --profile quick` followed by `build` prints
equal row counts for both models; running them again changes nothing.

### Tests for User Story 1

- [x] T015 [P] [US1] Unit tests for the Socrata client in `tests/unit/test_socrata.py` using a fake transport: keyset URL construction, page iteration, stop on empty page, retry with backoff on 429 and 5xx, honoring `Retry-After`, no retry on other 4xx, and the token never appearing in error messages
- [x] T016 [P] [US1] Unit tests for row parsing in `tests/unit/test_ingest_parsing.py`: missing keys become nulls, timestamps are parsed, and rows with a missing or non-numeric `unique_key` or an unparseable `created_date` are rejected with a reason
- [x] T017 [P] [US1] Integration test in `tests/integration/test_ingest.py`: loading the fixture pages into staging twice leaves the same row count; an interruption after the first page resumes from the checkpoint; rejected rows land in `staging.rejected_row`
- [x] T018 [P] [US1] Integration test in `tests/integration/test_model_parity.py` for the four parity invariants of data-model.md section 4, including that missing dimension values map to `Unknown` in both models

### Implementation for User Story 1

- [x] T019 [US1] Implement `src/nyc311_bench/socrata.py`: a paginated client over `urllib` with the `X-App-Token` header, `$select` of the 12 fields, keyset pagination on `(created_date, unique_key)` within the cut, configurable page size (default 50,000), and the retry policy of contracts/cli.md (makes T015 pass)
- [x] T020 [US1] **VERIFY** (research R5) Implement the bulk page insert in `src/nyc311_bench/ingest.py` with psycopg `COPY` into a temporary table followed by `INSERT ... ON CONFLICT DO NOTHING` into `staging.service_request_raw`; confirm the `COPY` API against the installed psycopg version and record it in `specs/001-nyc311-oltp-olap-benchmark/research.md`
- [x] T021 [US1] Complete `src/nyc311_bench/ingest.py`: row parsing and rejection, page insert and checkpoint update in one transaction, resume from the checkpoint, stop when the profile's target is staged, progress output and the final summary of rows loaded, rejected and duration (makes T016 and T017 pass)
- [x] T022 [US1] **VERIFY** (research open items) After staging the fixture, check whether `agency` determines `agency_name` and whether `unique_key` is unique; record the findings in `specs/001-nyc311-oltp-olap-benchmark/research.md` and adjust the `agency` key in `sql/oltp/schema.sql` and data-model.md only if the finding requires it
- [x] T023 [US1] Implement `src/nyc311_bench/oltp.py`: rebuild the `oltp` schema from the first N staged rows in `(created_date, unique_key)` order with set-based SQL (lookup tables first, then `service_request`), mapping missing values to `Unknown`, then `ANALYZE`
- [x] T024 [US1] Implement `src/nyc311_bench/olap.py`: rebuild the DuckDB star schema from the OLTP tables through the DuckDB `postgres` extension, with the fallback of streaming each table out with `COPY` if the extension is unavailable; generate `dim_date` for the cut and compute `resolution_hours`, `has_valid_resolution`, `closed_within_30d` and `created_hour` (makes T018 pass)
- [x] T025 [US1] Implement `src/nyc311_bench/cli.py` and `benchmark.py` with the `load` and `build` commands, argument validation, the missing-token check before any request, and exit codes 0, 1, 2 and 3 of contracts/cli.md; unit tests for argument validation and exit codes in `tests/unit/test_cli.py`
- [x] T026 [US1] Run `python benchmark.py load --profile quick` and `build --profile quick` against the real API, confirm equal row counts in both models and a no-op second run, and record the measured download and build durations in `specs/001-nyc311-oltp-olap-benchmark/research.md`

**Checkpoint**: both models hold the same 200,000 requests; User Story 1 is demonstrable.

---

## Phase 4: User Story 2 - Measure the analytical queries on both models (Priority: P1)

**Goal**: one command measures the six queries on both models and writes the results.

**Independent Test**: `python benchmark.py run --profile quick` writes
`results/benchmark_quick.json` and `.md` with median, p95 and speedup per query.

### Tests for User Story 2

- [x] T027 [P] [US2] Unit tests for the statistics in `tests/unit/test_runner_stats.py`: median, p95, min, max and speedup on known inputs, and rejection of fewer than 1 warm-up run or fewer than 10 repetitions
- [x] T028 [P] [US2] Unit tests for the report in `tests/unit/test_report.py`: JSON matches contracts/results-schema.md; the significance verdict is computed correctly at the 3x and two-thirds boundaries; the quick profile is marked not official with `significance.evaluated` false; the Markdown states the verdict whether reached or not
- [x] T029 [P] [US2] Integration test in `tests/integration/test_run.py`: `run` on the fixture produces both result files, and refuses with exit code 4 when one row is deleted from the fact table or a model is empty

### Implementation for User Story 2

- [x] T030 [P] [US2] Write `sql/oltp/q1_volume_by_type_month_borough.sql` and `sql/olap/q1_volume_by_type_month_borough.sql` per contracts/queries.md, each with the business question as a header comment and a total `ORDER BY`
- [x] T031 [P] [US2] Write `sql/oltp/q2_top_types_per_zip.sql` and `sql/olap/q2_top_types_per_zip.sql` per contracts/queries.md
- [x] T032 [P] [US2] Write `sql/oltp/q3_closure_rate_agency_channel.sql` and `sql/olap/q3_closure_rate_agency_channel.sql` per contracts/queries.md
- [x] T033 [P] [US2] Write `sql/oltp/q4_resolution_p90_agency_quarter.sql` and `sql/olap/q4_resolution_p90_agency_quarter.sql` per contracts/queries.md, using the same continuous percentile definition on both engines
- [x] T034 [P] [US2] Write `sql/oltp/q5_noise_by_weekday_hour.sql` and `sql/olap/q5_noise_by_weekday_hour.sql` per contracts/queries.md, with the same day-of-week numbering on both engines
- [x] T035 [P] [US2] Write `sql/oltp/q6_channel_share_by_quarter.sql` and `sql/olap/q6_channel_share_by_quarter.sql` per contracts/queries.md
- [x] T036 [US2] Implement `src/nyc311_bench/queries.py`: the registry of queries with id, business question, group and the pair of SQL files
- [x] T037 [US2] Implement `src/nyc311_bench/runner.py`: the parity guard on row counts, warm-up and measured runs timed with `perf_counter` around execute plus full fetch, per-model statistics, and collection of the environment and engine settings listed in contracts/results-schema.md (makes T027 pass)
- [x] T038 [US2] Implement `src/nyc311_bench/report.py`: write `results/benchmark_<profile>.json` and `.md` per contracts/results-schema.md, including the significance verdict and the quick-profile warning (makes T028 pass)
- [x] T039 [US2] Add the `run` and `all` commands to `src/nyc311_bench/cli.py` with `--warmup`, `--repetitions` and exit code 4 (makes T029 pass)

**Checkpoint**: the benchmark runs end to end on the quick profile.

---

## Phase 5: User Story 3 - Verify that both models give the same answers (Priority: P2)

**Goal**: automated proof that every query returns equivalent results on both models.

**Independent Test**: `pytest tests/integration` passes; altering one row in one model makes
it fail and name the query.

- [ ] T040 [US3] Implement the result comparison helper in `tests/integration/equivalence.py`: exact match for text and integers, relative tolerance 1e-9 for floats, and a failure message naming the query, the first differing row and the column
- [ ] T041 [US3] Integration test in `tests/integration/test_query_equivalence.py`, parametrized over every query in the registry, asserting equivalence on the fixture and that each query returns at least one row
- [ ] T042 [US3] Integration test in `tests/integration/test_equivalence_detects_drift.py`: after changing one fact row in DuckDB only, the equivalence check fails and reports which query differs
- [ ] T043 [US3] Add the `loaded` pytest marker path to `tests/integration/conftest.py` so the parity and equivalence tests can also be run against the currently loaded profile with `pytest -m loaded`, and run it on the quick profile

**Checkpoint**: equivalence is verified on the fixture and on real loaded data.

---

## Phase 6: Measurement

**Purpose**: produce the official numbers. This phase contains a hard gate.

- [ ] T044 Run `make bench PROFILE=quick` and `make test` from a clean state, time the whole sequence, and compare it with SC-008 (under 10 minutes); if it is not met, stop and report instead of relaxing the criterion
- [ ] T045 Run `python benchmark.py load --profile full` and `build --profile full`, time them, and compare with SC-002 (under 1 hour); if it is not met, stop and report
- [ ] T046 Run `python benchmark.py run --profile full` twice and check SC-006 (medians within 20% per query and model); if it is not met, identify the interference, rerun, and report what was found
- [ ] T047 **GATE (constitution principle II)** Read the significance verdict in `results/benchmark_full.json`. If SC-003 is not reached, **STOP and report to the human**: do not change data, queries, indexes or configuration. If it is reached, commit `results/benchmark_full.json`, `results/benchmark_full.md`, `results/benchmark_quick.json` and `results/benchmark_quick.md`
- [ ] T048 Run `pytest -m loaded` against the full profile and confirm SC-004 (every query equivalent on both models)

---

## Phase 7: Documentation and Polish

**Purpose**: the root deliverables.

- [ ] T049 [P] Write `README.md`: what the project shows, the official results table copied from `results/benchmark_full.md`, prerequisites, the quick-profile reproduction in at most 5 commands, the full-profile command, how to obtain the app token, and the data source attribution and terms from T008
- [ ] T050 [P] Write `DESIGN.md` (maximum 2 pages): the pipeline, both models and why each is shaped as it is, the six queries, the measurement method, and the limitations (schema and engine effects combined, in-process versus TCP, default engine settings, quick profile not representative)
- [ ] T051 [P] Write `AI_WORKFLOW.md` from the "Log for AI_WORKFLOW.md" in `CLAUDE.md`: the SDD flow followed, the agent modes and harness, and every real correction made to AI-generated work
- [ ] T052 Walk through `specs/001-nyc311-oltp-olap-benchmark/quickstart.md` end to end, including the checks table, and fix any deviation
- [ ] T053 Update "Current status" in `CLAUDE.md`, run `graphify update .`, and run `/speckit-analyze`

---

## Phase 8: User Story 4 - Transactional operations (Priority: P3, OPTIONAL)

**Goal**: show the side of the trade-off where the transactional model wins.

**Only if time remains** after Phase 7. Skipping this phase does not affect the deliverable.

**Independent Test**: `python benchmark.py run --profile quick --include-transactional`
adds a separate transactional section to the report.

- [ ] T054 [P] [US4] Write `sql/oltp/t1_lookup_by_id.sql`, `sql/olap/t1_lookup_by_id.sql`, `sql/oltp/t2_insert_request.sql` and `sql/olap/t2_insert_request.sql` per contracts/queries.md
- [ ] T055 [US4] Extend `src/nyc311_bench/queries.py`, `runner.py` and `cli.py` with the `transactional` group and the `--include-transactional` flag: fixed identifier list cycled across repetitions for `t1`, insert inside a rolled-back transaction for `t2`
- [ ] T056 [US4] Extend `src/nyc311_bench/report.py` and `tests/unit/test_report.py` so transactional operations are reported in a separate section and excluded from the significance verdict
- [ ] T057 [US4] Integration test in `tests/integration/test_transactional.py`: `t1` returns the same request on both models and `t2` leaves both row counts unchanged; then rerun the full profile with the flag and update `results/` and `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup. T008 decides the kind of fixture built in
  T010; T009 needs the app token from the human.
- **User Story 1 (Phase 3)**: depends on Foundational.
- **User Story 2 (Phase 4)**: depends on User Story 1 (it needs loaded models).
- **User Story 3 (Phase 5)**: depends on User Story 2 (it needs the query registry).
- **Measurement (Phase 6)**: depends on Phases 3 to 5. T047 is a gate.
- **Documentation (Phase 7)**: depends on Phase 6 passing its gate.
- **User Story 4 (Phase 8)**: optional, after Phase 7.

### Needs from the human

- A Socrata app token in `.env` before T009.
- Docker Desktop running before T014.
- A decision at T047 if SC-003 is not reached, and at T044 or T045 if a time target is missed.

### Within Each User Story

- Every module is committed together with the tests that cover it, and the suite is green
  at every commit.
- Schemas before builders, builders before the CLI, the CLI before real runs.

### Parallel Opportunities

- T003 and T004; T011, T012 and T013.
- T015 to T018 (four test files).
- T027 to T029; T030 to T035 (six independent query pairs).
- T049 to T051 (three documents).

## Parallel Example: User Story 2

```bash
# The six query pairs are independent files:
Task: "Write sql/oltp/q1_… and sql/olap/q1_…"
Task: "Write sql/oltp/q2_… and sql/olap/q2_…"
Task: "Write sql/oltp/q3_… and sql/olap/q3_…"
```

## Implementation Strategy

### MVP First (User Story 1)

Phases 1 to 3. Stop and validate: both models hold the same quick-profile data.

### Incremental Delivery

1. Phases 1 to 3: the load works and both models match.
2. Phase 4: the benchmark produces numbers on the quick profile.
3. Phase 5: the numbers are trustworthy.
4. Phase 6: official numbers, behind the significance gate.
5. Phase 7: the deliverables.
6. Phase 8: only with spare time.

Each phase ends with a stop: the human authorizes the next one (constitution principle I).

## Notes

- 57 tasks: 5 setup, 9 foundational, 12 for US1, 13 for US2, 4 for US3, 5 measurement,
  5 documentation, 4 optional for US4.
- Four tasks are marked VERIFY and one is marked GATE.
- Direct `curl` to the API is denied by the project permissions; live checks go through the
  project's own Python client or a research subagent.
