# Research: OLTP vs OLAP Benchmark on NYC 311

**Date**: 2026-10-12 | **Feature**: [spec.md](./spec.md)

Facts were gathered by a read-only research subagent against the live API and official
documentation. Each fact is tagged **[V]** (verified, source listed at the end) or **[U]**
(unverified: recollection or inference, to be confirmed by the task that depends on it).

## R1. Source dataset

- The dataset `erm2-nwe9` is named "311 Service Requests from 2020 to Present" and holds
  22,761,196 rows, created 2020-01-01 to 2026-10-10 [V].
- It has 48 columns; 44 are data columns and 4 are `:@computed_region_*` [V].
- The JSON API returns every value as a string, including `number` columns, and **omits keys
  whose value is null** [V]. The loader must cast and must tolerate missing keys.
- Dates are ISO timestamps without a time zone (`2026-10-10T03:03:53.000`) [V].

Columns used by this feature (all `text` unless noted) [V]:

| Source field | Type | Used for |
|---|---|---|
| `unique_key` | text (numeric string) | request identifier |
| `created_date` | calendar_date | creation timestamp, time dimension |
| `closed_date` | calendar_date, nullable | closing timestamp, resolution measure |
| `agency`, `agency_name` | text | agency |
| `complaint_type`, `descriptor` | text | complaint type and descriptor |
| `borough`, `incident_zip`, `community_board` | text | location |
| `open_data_channel_type` | text | channel |
| `status` | text | status |

Measured cardinalities and data-quality counts over the whole dataset [V]:

| Field | Distinct values | Notes |
|---|---|---|
| `agency` | 21 | NYPD 9.96 M, HPD 4.50 M, DSNY 2.55 M |
| `complaint_type` | 276 | |
| `descriptor` | 1,361 | |
| `borough` | 6 + missing | includes `Unspecified` (41,046) and 38,433 rows with no value |
| `open_data_channel_type` | 5 | ONLINE, PHONE, MOBILE, UNKNOWN, OTHER |
| `status` | 8 | Closed is 22.29 M of 22.76 M |
| `incident_zip`, `community_board` | not measured | the aggregate queries timed out [U] |

- 439,146 rows have no `closed_date`; 47,207 rows have `closed_date < created_date` [V].
- Rows per creation year [V]: 2020: 2,942,024 · 2021: 3,220,882 · 2022: 3,169,960 ·
  2023: 3,224,723 · 2024: 3,456,770 · 2025: 3,655,042 · 2026 (to Oct 10): 3,091,795.

## R2. Data cut and volume profiles

**Decision**: the cut is `created_date` in `[2024-01-01, 2026-01-01)`, read in ascending
`(created_date, unique_key)` order. A profile takes the first N rows of that cut: 5,000,000
(full) or 200,000 (quick).

**Rationale**: the range holds 7,111,812 rows [V], enough for the full profile. It ends more
than nine months before today, so nearly all requests are already closed and the rows are
unlikely to change between two loads, which is what FR-003 needs. Taking the first N rows of
a fixed ordered range makes both profiles deterministic.

**Alternatives considered**: the most recent rows (they are still being updated, so two
loads would differ); a random sample (not expressible as a stable paginated query).

**Known limitation**: the quick profile covers only the first weeks of January 2024, so its
monthly aggregations have few groups. It verifies that everything works; it is not
analytically representative. FR-026 already requires the report to say so.

## R3. API access and pagination

**Decision**: use the SODA 2.x endpoint `/resource/erm2-nwe9.json` with the `X-App-Token`
header, `$select` limited to the 12 fields above, keyset pagination on
`(created_date, unique_key)` and a page size of 50,000 (configurable).

**Rationale**:

- The header is the method Socrata documents as preferred; with a token requests are not
  throttled, without one they share a low per-IP pool and receive HTTP 429 [V].
- The maximum `$limit` is 50,000 on SODA 2.0 endpoints and unlimited on 2.1/3.0 [V]. 50,000
  is valid on every version, so the endpoint version does not need to be known. The full
  profile is then 100 requests.
- Keyset pagination (`$where` on the last key seen, with `$order`) keeps every page equally
  cheap and makes resuming trivial: the checkpoint is the last key. `$offset` pagination gets
  slower as the offset grows and gives no natural checkpoint [U].
- `unique_key` is `text`, so it orders lexicographically, not numerically [V]. That is still
  a stable total order, and the same comparison is used in `$order` and `$where`, so the
  keyset is consistent. It is only a tie-breaker behind `created_date`.

**Alternatives considered**: SODA 3 `/api/v3/views/.../query.json` (sources disagree on
whether it requires authentication [U]); the bulk CSV export `rows.csv` (not paginated, so
not resumable, and it bypasses the API the challenge asks for).

**Confirmed against the live API (task T009, 2026-10-12)** [V]:

- SoQL accepts the compound keyset predicate
  `created_date > X OR (created_date = X AND unique_key > K)` combined with the cut range.
- Two consecutive 1,000-row pages had no overlap and no duplicates, and were globally sorted
  by `(created_date, unique_key)`; 137 of those 2,000 rows share a `created_date` with
  another row, so the `unique_key` tie-breaker is necessary.
- Every `unique_key` in 52,000 rows read was an 8-digit numeric string. With equal length,
  text order and numeric order coincide.
- The response contains exactly the 12 selected fields; missing values are omitted keys.
- Latency: about 8 to 11 seconds for a 1,000-row page and 15.8 seconds for a 50,000-row page
  (19.7 MB of JSON). Cost is dominated by the query, not the page size, so large pages are
  the right choice. The full profile (100 pages) is therefore estimated at about 26 minutes
  of download, and the quick profile (4 pages) at about 1 minute. One sample only.
- No agency code had more than one `agency_name` in those rows; this is a small sample from
  the first hours of the cut, so the `(code, name)` key stays until T022 checks more data.

**Still to confirm [U]**: that `unique_key` is unique across the whole cut (enforced anyway
by the staging primary key).

## R4. OLAP engine

**Decision (approved by the human on 2026-10-12)**: DuckDB, embedded, storing the star
schema in a local `.duckdb` file.

| | DuckDB | ClickHouse | Star schema inside PostgreSQL 17 |
|---|---|---|---|
| Storage | columnar [U] | columnar [U] | row-oriented |
| Deployment | in-process, no server | extra docker container | same instance |
| New Python dependency | `duckdb` 1.5.6, Python ≥ 3.10 [V] | `clickhouse-connect` 1.10.0 [V] | none |
| Load from PostgreSQL | `postgres` core extension: `ATTACH`, `CREATE TABLE AS` [V] | no verified native path [U] | `INSERT ... SELECT` |
| Memory | fits a laptop [U] | 16 GB+ advised, 32 GB recommended [V, partial] | already running |

**Rationale**:

- The benchmark machine has 16 GB of RAM. ClickHouse guidance warns of memory errors below
  16 GB with default settings, and PostgreSQL must run alongside it.
- DuckDB adds one pip package and no service, which keeps the evaluator's quick profile
  within SC-001 (five commands) and SC-008 (ten minutes).
- It can build the star schema by reading the OLTP tables directly, so both models derive
  from the same load (FR-011) without an intermediate export.
- A star schema inside PostgreSQL has zero dependencies but stays row-oriented. It would
  measure the effect of the schema alone and is likely to fall short of SC-003.

**Fairness notes to carry into DESIGN.md** (constitution principle III):

- The measured difference combines two things: the schema (normalized vs star) and the
  storage engine (row vs columnar). The report must say so and not attribute it all to one.
- PostgreSQL is reached over a local TCP connection; DuckDB runs in-process. For queries
  that take tens of milliseconds or more the transport cost is negligible, but it is
  recorded as a limitation.
- Both engines run with their default configuration plus `ANALYZE` after loading. Settings
  that affect the result (PostgreSQL parallel workers, DuckDB threads) are written into the
  results file.

**Risk**: the DuckDB `postgres` extension is downloaded on first use. If that is not possible
in the evaluator's network, the fallback is to stream each OLTP table out with `COPY` and
insert it into DuckDB from Python; no extra dependency is needed.

## R5. Python dependencies

**Decision (approved by the human on 2026-10-12)**:

| Package | Version seen | Use | Scope |
|---|---|---|---|
| `psycopg[binary]` | 3.3.6, Python ≥ 3.10, LGPL-3.0 [V] | PostgreSQL driver, bulk load with `COPY` [U] | runtime |
| `duckdb` | 1.5.6, Python ≥ 3.10 [V] | OLAP engine | runtime |
| `pytest` | already in the stack | tests | dev |
| `ruff` | already in the stack | lint and format | dev |

**HTTP client**: the standard library `urllib` is enough for sequential GET requests with one
header. Retries with backoff are about twenty lines of code, which is cheaper than a new
dependency (principle V).

**CLI and statistics**: `argparse` and `statistics` from the standard library.

**Alternatives considered**: `httpx`/`requests` (rejected, not needed); `pandas`/`polars`
for the transform (rejected, the transform is done in SQL inside each engine);
`pytest-benchmark` (rejected, the benchmark needs its own report format).

## R6. Measurement method

**Decision**: client-side wall-clock timing with `time.perf_counter()` around execute plus
full fetch of the result. Per query and per model: 1 discarded warm-up run, then 10 measured
runs (both configurable). Reported: median, p95, min, max, and `oltp_median / olap_median`.

**Rationale**: this is what an application would observe and it is identical for both
engines. Warm-up removes cold-cache effects; the median resists outliers. p95 over 10 runs is
a coarse estimate, and the report says how many runs it is based on.

**Order of execution**: for each query, all runs on one model, then all runs on the other.
Nothing else is run concurrently.

## R7. Integration test data

**Decision**: integration tests load a small synthetic fixture committed under
`tests/fixtures/` (synthetic because of R8) into a dedicated PostgreSQL database and a temporary DuckDB file. They need
Docker but neither the network nor an app token. The same checks can also be pointed at the
currently loaded profile.

**Rationale**: FR-023 requires tests that do not depend on the full load, and tests that hit
the public API would be slow and flaky. The fixture includes the edge cases from the spec:
no `closed_date`, `closed_date` before `created_date`, and missing dimension values.

## R8. License and attribution

**Status: not verified (task T008, 2026-10-12).** A second research pass could not read the
official terms:

- `https://www.nyc.gov/html/data/terms.html` returned HTTP 404 on two attempts [V]. Its
  content is known only through a search-engine summary, which is not a reliable quote [U].
- The dataset landing page exposed no license, attribution or privacy text to the fetch
  tool, and the dataset metadata declares no license; its attribution is "311" [V].
- `https://www.nyc.gov/home/terms-of-use.page` is the generic NYC.gov site text; it has no
  open-data section [V].
- The search summary says the NYC Open Data Law (Local Law 11 of 2012) makes public data sets
  available without license requirement or restrictions on use, that the City may require
  the source to be identified, and that the City disclaims any warranty of accuracy [U].

**Decision**: because permission to redistribute rows is not verified, the repository
commits **no real rows**. The test fixture (R7) is synthetic, with the same shape as the
source. Real data is only ever downloaded by the user running the benchmark.

**Remaining action for the human**: open the terms page in a browser and confirm the
attribution wording before the README is published. The README will name the source and the
dataset id, state that the data is provided by the City as is, and link to the portal.

## R9. Findings from implementing User Story 1 (2026-10-12)

**Bulk load with psycopg (task T020)** [V, psycopg 3.3.6]: `cursor.copy("COPY ... FROM STDIN")`
with `copy.write_row()` loads a page into a temporary table, and iterating
`cursor.copy("COPY (...) TO STDOUT")` streams a table out. Both are used: the first for
staging, the second for the DuckDB fallback path.

**Source data checks on the 200,000 staged rows (task T022)** [V]:

- `unique_key` is unique (200,000 distinct values) and always 8 digits, so `bigint` is a
  valid primary key type.
- Every agency code has exactly one name (14 codes, 14 code-name pairs). The agency table
  keeps its `(code, name)` key anyway: it costs nothing and does not assume the property
  holds for the rest of the cut.
- 2,046 rows have no `closed_date` and 39 have `closed_date` before `created_date`.
- No dimension value is missing in this sample; the source uses its own `Unspecified` for
  borough. The `Unknown` member is exercised by the synthetic fixture only.

**First real run of the quick profile (task T026)** [V, one run, Apple M1 Pro]:

| Step | Duration |
|---|---|
| Download 200,000 rows (4 pages of 50,000) | 57.1 s |
| Build OLTP model (PostgreSQL) | 4.9 s |
| Build OLAP model (DuckDB, via the `postgres` extension) | 0.4 s |

- Both models hold 200,000 requests; a second `load` requests nothing from the API and a
  second `build` gives the same counts.
- The quick profile spans 2024-01-01 to 2024-01-22: three weeks, a single month.
- Sizes: 14 agencies, 168 complaint types, 814 descriptors, 6 boroughs, 613 locations,
  5 channels, 7 statuses. The DuckDB file is 13 MB; the OLTP request table with its indexes
  is 31 MB.
- Extrapolation to the full profile, assuming linear cost: about 24 minutes of download and
  about 2 minutes to build both models, inside the 1-hour limit of SC-002. This is an
  estimate until the full profile is actually run.

## Sources verified

- `https://data.cityofnewyork.us/resource/erm2-nwe9.json` (sample rows, counts, aggregates)
- `https://data.cityofnewyork.us/api/views/erm2-nwe9.json` and `.../columns.json`
- `https://dev.socrata.com/docs/app-tokens.html`
- `https://dev.socrata.com/docs/queries/limit`
- `https://pypi.org/pypi/duckdb/json`, `https://pypi.org/pypi/psycopg/json`,
  `https://pypi.org/pypi/clickhouse-connect/json`
- `https://duckdb.org/docs/current/core_extensions/postgres/overview.html`
- `https://clickhouse.com/docs/guides/oss/best-practices/tips` (via search summary only)

## Open items

| Item | Blocks | Resolved by |
|---|---|---|
| NYC Open Data terms of use (page returned 404) | README wording | human, in a browser |
