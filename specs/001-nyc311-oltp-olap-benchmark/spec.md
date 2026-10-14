# Feature Specification: OLTP vs OLAP Benchmark on NYC 311

**Feature Branch**: `001-nyc311-oltp-olap-benchmark`  
**Created**: 2026-10-12  
**Status**: Approved (2026-10-12)  
**Input**: User description: "OLTP vs OLAP benchmark on NYC 311 Service Requests: ingestion from the public API, normalized OLTP model, OLAP star-schema model, a fixed set of analytical queries, a benchmark script with results in results/, and integration tests for equivalence."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load the same data into both models (Priority: P1)

As an evaluator of the challenge, I want to fetch NYC 311 service requests from the public
API and have them loaded into a normalized transactional model and into an analytical star
model, so that any later comparison starts from exactly the same data.

**Why this priority**: without identical data in both models there is no defensible
benchmark. It is the foundation for everything else and on its own already demonstrates the
ingestion and both data designs.

**Independent Test**: run the load with a reduced volume and check that both models report
the same number of requests and the same totals per dimension.

**Acceptance Scenarios**:

1. **Given** an empty database and API access, **When** the load runs with a target volume,
   **Then** both models contain that number of requests, with no duplicates.
2. **Given** a completed load, **When** it is run again with the same parameters, **Then**
   the number of requests in both models does not change.
3. **Given** a load interrupted halfway, **When** it is relaunched, **Then** it continues
   from the last confirmed point without downloading again what is already loaded.
4. **Given** the API answers with a temporary error or a too-many-requests error, **When**
   the load is in progress, **Then** it waits, retries and finishes without losing or
   duplicating rows.
5. **Given** no API credential is configured, **When** the load is launched, **Then** this
   is reported with a clear message before anything is downloaded.

---

### User Story 2 - Measure the analytical queries on both models (Priority: P1)

As an evaluator, I want to run a single command that measures a fixed set of analytical
queries on both models and gives me the compared timings, so that I can see the performance
difference in numbers.

**Why this priority**: it is the central deliverable of the challenge: the measurable
evidence.

**Independent Test**: with both models loaded, run the benchmark and verify that it produces
a report with timings per query and per model, and the difference factor.

**Acceptance Scenarios**:

1. **Given** both models loaded, **When** the benchmark runs, **Then** every query is
   measured on both models with discarded warm-up runs and several measured repetitions.
2. **Given** a finished benchmark, **When** the results directory is opened, **Then** there
   is a machine-readable file and a human-readable summary with median, percentiles and
   difference factor per query.
3. **Given** a finished benchmark, **When** the report is read, **Then** it states the data
   volume, the execution environment, the date and the measurement parameters.
4. **Given** the difference does not reach the significance threshold, **When** the
   benchmark ends, **Then** the report states it explicitly and no data is altered.
5. **Given** an evaluator short on time, **When** they run load, benchmark and tests with the
   quick profile, **Then** everything finishes in minutes and the report warns that those
   timings are not the official ones.
6. **Given** an evaluator who does not want to run anything, **When** they open the
   repository, **Then** they find the official results of the full profile already published.

---

### User Story 3 - Verify that both models give the same answers (Priority: P2)

As an evaluator, I want automated tests confirming that every query returns equivalent
results on both models, so that I can trust that equal answers are being compared.

**Why this priority**: it gives the numbers their validity; without it the difference could
be due to the models answering different questions.

**Independent Test**: run the integration suite on a reduced load and check that it passes;
alter one row in a single model and check that it fails.

**Acceptance Scenarios**:

1. **Given** both models loaded, **When** the integration tests run, **Then** they verify
   that the number of requests and the totals per dimension match.
2. **Given** both models loaded, **When** every benchmark query runs on both, **Then** the
   results are equivalent (same rows and values, with a documented numeric tolerance for
   averages).
3. **Given** a discrepancy between models, **When** the tests run, **Then** they fail and
   indicate which query or which total differs.

---

### User Story 4 - Show the contrast on transactional operations (Priority: P3)

As an evaluator, I also want to see how both models behave on typical transactional
operations (looking up a request by its identifier, registering a new one), to understand
the full trade-off and not only the side that favors the analytical model.

**Why this priority**: it enriches the conclusion, but the challenge is fulfilled without
it. It is implemented only if time remains once stories 1 to 3 are complete.

**Independent Test**: run the benchmark with the transactional operations group enabled and
check that the report presents them separately from the analytical ones.

**Acceptance Scenarios**:

1. **Given** both models loaded, **When** the transactional group runs, **Then** the report
   shows its timings in a section separate from the analytical queries.

---

### User Story 5 - Separate the effect of the schema from the effect of the engine (Priority: P3)

*Added after the first official run, when the combined schema-and-engine effect was
identified as the main limitation of the comparison.*

As an evaluator, I want to know how much of the speedup comes from the data model (normalized
vs star schema) and how much from the storage engine (row store vs column store), and how
stable the measurements are across repetitions.

**Why this priority**: the challenge is fulfilled without it, but it answers the most
obvious objection to the result ("you changed two things at once").

**Independent Test**: run the experiments command and check that every combination of
schema and engine returns the same rows and appears in the report, with the spread of the
repetitions.

**Acceptance Scenarios**:

1. **Given** both models loaded, **When** the experiments run, **Then** the star schema is
   also measured on PostgreSQL and the normalized schema on DuckDB.
2. **Given** the four models, **When** a query is measured, **Then** it first returns the same
   rows on all of them; otherwise nothing is measured.
3. **Given** several repetitions, **When** the report is written, **Then** it shows the
   median, the range and the coefficient of variation of each model, the effect of the engine
   and of the schema, and how many series satisfy SC-006.

---

### Edge Cases

- Requests without a closing date (still open): they have no resolution time and must not
  count in resolution averages, but they do count in totals.
- Requests whose closing date precedes their creation date: they are loaded, flagged as
  invalid for the resolution measure, and counted in the data-quality report.
- Missing or empty dimension values (borough, ZIP code, channel): they are assigned to an
  "Unknown" member in both models, never dropped in only one.
- The source adds or modifies requests while the load is running: the load works on a fixed
  cut (closed range of creation dates) with a stable pagination order.
- The API returns fewer rows than requested or an empty page before the target is reached.
- The requested target volume exceeds the rows available in the chosen range.
- The benchmark is launched with an empty model or with different counts between models: it
  must refuse to measure and explain why.

## Requirements *(mandatory)*

### Functional Requirements

**Ingestion**

- **FR-001**: The system MUST fetch NYC 311 service requests from the public API, page by
  page and in a stable order.
- **FR-002**: The target volume MUST be configurable, with two predefined profiles: **full**
  (5,000,000 requests, the one used for the official results) and **quick** (200,000
  requests, so that an evaluator can verify everything works in minutes). The accepted
  minimum is 100,000.
- **FR-003**: Ingestion MUST work on a fixed, declared cut of the data (range of creation
  dates), so that two loads with the same parameters obtain the same rows.
- **FR-004**: Ingestion MUST be idempotent: re-running it does not duplicate requests.
- **FR-005**: Ingestion MUST be resumable after an interruption, from the last confirmed
  point.
- **FR-006**: Ingestion MUST respect the API limits, retrying with a wait on temporary errors
  and stopping with a clear message on persistent errors.
- **FR-007**: The API credential MUST be read from the environment and never appear in the
  repository or in execution logs.
- **FR-008**: Ingestion MUST report its progress and, on completion, a summary: rows loaded,
  rows rejected with their reason, and duration.

**Data models**

- **FR-009**: The transactional model MUST be normalized: the request references agency,
  complaint type with its descriptor, location, channel and status, each stored only once.
- **FR-010**: The analytical model MUST be organized as a star schema: one fact per request
  with time, agency, complaint type, location and channel dimensions, and resolution time as
  a measure.
- **FR-011**: Both models MUST derive from the same load and contain exactly the same set of
  requests.
- **FR-012**: Missing values in a dimension MUST be treated identically in both models.

**Queries and benchmark**

- **FR-013**: The system MUST define a fixed set of at least 6 analytical queries, each with
  its business question documented, covering: aggregation by period, top-N, filter by
  dimension, and the resolution measure. At minimum it includes:
  - requests by complaint type and month, per borough;
  - the 10 most frequent complaint types per ZIP code with their average resolution time;
  - 30-day closure rate by agency and channel.
- **FR-014**: Each query MUST be expressed with the same logic on both models.
- **FR-015**: The benchmark MUST measure each query on each model with at least 1 discarded
  warm-up run and at least 10 measured repetitions, both configurable.
- **FR-016**: The benchmark MUST report per query and model: median, 95th percentile,
  minimum, maximum, and the difference factor between models on the median.
- **FR-017**: The benchmark MUST write to `results/` a machine-readable file and a
  human-readable summary, including data volume, execution environment, date and measurement
  parameters.
- **FR-018**: The benchmark MUST refuse to measure if the models do not contain the same
  number of requests.
- **FR-019**: The report MUST state whether the significance threshold (SC-003) is reached.
  If it is not, it says so explicitly; under no circumstances are data, queries or
  configuration modified in order to reach it.
- **FR-020**: The benchmark MAY include a separate group of transactional operations (reading
  one request by identifier and inserting one request), reported apart from the analytical
  queries.

- **FR-027**: The experiments MUST measure the four combinations of schema (normalized,
  star) and engine (PostgreSQL, DuckDB), built from the same OLTP data, and MUST NOT change
  the official result files.
- **FR-028**: Before measuring, the experiments MUST verify that all four models return the
  same rows for every query, and MUST repeat the whole grid at least twice to report the
  spread between repetitions.

**Verification**

- **FR-021**: Integration tests MUST verify, against the two real models, that the number of
  requests and the totals per dimension match.
- **FR-022**: Integration tests MUST verify that every benchmark query returns equivalent
  results on both models.
- **FR-023**: Integration tests MUST be runnable on a reduced volume without depending on the
  full load.

**Reproduction by the evaluator**

- **FR-024**: The official results, measured with the full profile, MUST be published in
  `results/` inside the repository, so that they can be read without running anything.
- **FR-025**: The quick profile MUST run the same load, the same queries and the same tests
  as the full one, changing only the volume.
- **FR-026**: Every results report MUST state which profile and volume produced it. The
  significance threshold (SC-003) is evaluated only on the full profile; a quick-profile
  report MUST warn that its timings are not the official ones.

### Key Entities

- **Service request**: a complaint or notice from a citizen. It has a unique source
  identifier, a creation date, an optional closing date, and references to agency, complaint
  type, location, channel and status.
- **Agency**: the city body responsible for handling the request.
- **Complaint type**: the category of the request, with a more specific descriptor.
- **Location**: borough, ZIP code and community board where the problem occurs.
- **Channel**: the means by which the request was registered (phone, web, mobile or other).
- **Status**: the state of the request (open, closed, etc.).
- **Time**: the creation date broken down into day, month, quarter, year and day of week.
- **Resolution time**: derived measure, the difference between closing and creation.
- **Benchmark query**: a business question with its equivalent expression on each model.
- **Benchmark run**: a set of measurements with its environment, volume and parameters.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A person with the repository and an API credential reproduces load, benchmark
  and tests by following only the README, with no more than 5 commands.
- **SC-002**: With the full profile (5,000,000 requests), the whole data preparation process
  — download from the API and load into both models — finishes in under 1 hour on a laptop
  with a home connection.
- **SC-003**: The difference is considered significant if, with the full profile, the
  analytical model is at least 3 times faster on the median in at least two thirds of the
  analytical queries.
- **SC-004**: 100% of the benchmark queries return equivalent results on both models, as
  verified by the integration tests.
- **SC-005**: Relaunching a completed load leaves the number of requests unchanged (0
  duplicates) in both models.
- **SC-006**: Two consecutive benchmark runs on the same data give medians that differ by
  less than 20% per query and model.
- **SC-007**: The results report lets a reader identify in under 1 minute which model wins
  each query and by how much.
- **SC-008**: With the quick profile (200,000 requests), an evaluator completes load,
  benchmark and integration tests in under 10 minutes.
- **SC-009**: An evaluator can read the official results in the repository without running
  any command.

## Assumptions

- The source is the public NYC 311 Service Requests dataset, accessible with a free
  credential that the user creates and configures in their environment.
- The default data cut is a closed range of creation dates large enough to reach the target
  volume.
- The benchmark runs on a single machine, with no concurrent users; concurrency is out of
  scope.
- Timings are measured end to end from the client, including full retrieval of the result.
- The exact names and availability of the source fields are confirmed against the API during
  the planning phase.
- The data usage license is verified during the planning phase and cited in the README.
- The specific analytical engine, the indexes and the format of the result files are
  decisions of the plan, not of this spec.
- Out of scope: web interface, cloud deployment, real-time incremental updates, and
  geospatial analysis with coordinates.
