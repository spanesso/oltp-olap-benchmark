# Data Model: OLTP vs OLAP Benchmark on NYC 311

**Date**: 2026-10-12 | **Feature**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

Data flows in one direction, so both models derive from a single load (FR-011):

```text
NYC 311 API ──▶ staging.service_request_raw ──▶ oltp.* (PostgreSQL, 3NF) ──▶ star schema (DuckDB)
                (PostgreSQL, text columns)
```

## 1. Staging (PostgreSQL, schema `staging`)

Landing area for API pages. It is what makes the load idempotent and resumable.

**`staging.service_request_raw`** — one row per source row, values as received.

| Column | Type | Notes |
|---|---|---|
| `unique_key` | text, primary key | re-inserting a page is a no-op (`ON CONFLICT DO NOTHING`) |
| `created_date` | timestamp, not null | |
| `closed_date` | timestamp, null | |
| `agency`, `agency_name` | text, null | |
| `complaint_type`, `descriptor` | text, null | |
| `borough`, `incident_zip`, `community_board` | text, null | |
| `open_data_channel_type` | text, null | |
| `status` | text, null | |

**`staging.ingest_checkpoint`** — one row per data cut.

| Column | Type | Notes |
|---|---|---|
| `cut_start`, `cut_end` | timestamp, primary key | the declared cut (FR-003) |
| `last_created_date`, `last_unique_key` | timestamp, text | keyset position of the last committed page |
| `rows_loaded` | bigint | rows of the cut present in staging |
| `updated_at` | timestamptz | |

Both profiles read the same cut in the same order, so the quick profile is a prefix of the
full one. Staging only ever grows: loading the full profile after the quick one continues
from row 200,001. The models are then built from the first N staged rows in
`(created_date, unique_key)` order, where N is the profile's target, so switching profile
never requires downloading again.

A page insert and its checkpoint update are committed in the same transaction, so an
interruption can never leave them out of step (FR-005).

**`staging.rejected_row`** — rows that cannot be loaded, with the reason (FR-008): missing or
non-numeric `unique_key`, missing or unparseable `created_date`, unparseable `closed_date`.

## 2. OLTP model (PostgreSQL, schema `oltp`, third normal form)

```text
agency ◀──┐
channel ◀─┤
status ◀──┼── service_request ──▶ complaint_descriptor ──▶ complaint_type
location ◀┘                │
   └──▶ borough
```

| Table | Columns | Keys and constraints |
|---|---|---|
| `agency` | `agency_id`, `code`, `name` | PK `agency_id`; unique `(code, name)` |
| `complaint_type` | `complaint_type_id`, `name` | PK; unique `name` |
| `complaint_descriptor` | `descriptor_id`, `complaint_type_id`, `name` | PK; FK to `complaint_type`; unique `(complaint_type_id, name)` |
| `borough` | `borough_id`, `name` | PK; unique `name` |
| `location` | `location_id`, `borough_id`, `zip_code`, `community_board` | PK; FK to `borough`; unique `(borough_id, zip_code, community_board)` |
| `channel` | `channel_id`, `name` | PK; unique `name` |
| `status` | `status_id`, `name` | PK; unique `name` |
| `service_request` | `request_id`, `created_at`, `closed_at`, `agency_id`, `descriptor_id`, `location_id`, `channel_id`, `status_id` | PK `request_id` (bigint, from `unique_key`); five FKs, all not null |

**Indexes** (idiomatic for a transactional workload): the primary keys, one B-tree index per
foreign key on `service_request`, and a B-tree index on `service_request.created_at`. They are
created after the bulk load (`sql/oltp/indexes.sql`).

**Rules**:

- A missing or empty source value maps to the member `Unknown` of its lookup table
  (FR-012). The source's own `Unspecified` value is kept as it is; the two are not merged.
- `agency` is keyed on `(code, name)` because it is not yet confirmed that the code
  determines the name (research open item).
- `closed_at` is null for open requests. No derived column is stored: resolution time is
  computed in queries as `closed_at - created_at`, as a normalized model would.
- Rows with `closed_at < created_at` are loaded unchanged.

## 3. OLAP model (DuckDB file, star schema)

```text
dim_date ◀──┐
dim_agency ◀┤
dim_complaint ◀┼── fact_service_request
dim_location ◀─┤
dim_channel ◀──┤
dim_status ◀───┘
```

| Table | Grain | Columns |
|---|---|---|
| `dim_date` | one row per calendar day between the first and last request loaded | `date_key` (yyyymmdd), `date`, `year`, `quarter`, `month`, `month_name`, `day`, `day_of_week`, `is_weekend` |
| `dim_agency` | one row per agency | `agency_key`, `code`, `name` |
| `dim_complaint` | one row per complaint type and descriptor | `complaint_key`, `complaint_type`, `descriptor` |
| `dim_location` | one row per location | `location_key`, `borough`, `zip_code`, `community_board` |
| `dim_channel` | one row per channel | `channel_key`, `name` |
| `dim_status` | one row per status | `status_key`, `name` |
| `fact_service_request` | one row per request | `request_id`, the six dimension keys, `created_at`, `created_hour`, `closed_at`, `is_closed`, `resolution_hours`, `has_valid_resolution`, `closed_within_30d` |

**Rules**:

- Dimensions are denormalized: `dim_complaint` flattens type and descriptor, `dim_location`
  flattens borough into the location. Surrogate keys are copied from the OLTP identifiers so
  the two models can be compared row by row in tests.
- `resolution_hours` is `closed_at - created_at` in hours. It is null, and
  `has_valid_resolution` is false, when the request is open or when `closed_at` precedes
  `created_at`. Resolution averages use only rows with `has_valid_resolution`.
- `closed_within_30d` is true when the request has a valid resolution of 30 days or less.
- Precomputing these measures is idiomatic for a star schema and is the counterpart of the
  OLTP rule that stores no derived column. Both sides must produce the same values; the
  integration tests check it (FR-022).
- The spec lists five dimensions; `dim_status` is added because status is a filter in the
  queries and it costs one small table.

## 3b. Control models (schema versus engine experiments, FR-027)

Built by `python benchmark.py experiments` from the OLTP tables; never part of the official
results.

- **`star_pg`** (PostgreSQL schema): the same seven tables and columns as section 3, with
  `smallint` instead of `tinyint`, a primary key on every table (`request_id` on the fact
  table) and one index per fact foreign key plus `created_at`.
- **`control_3nf.duckdb`** (DuckDB file, schema `oltp`): a copy of the eight normalized tables of
  section 2, without indexes. `service_request` is stored in creation order, as the star fact
  table is.

Both hold exactly the rows of the OLTP model; the experiments verify this by comparing the
result of every query across the four models before measuring.

## 4. Parity invariants (checked by integration tests, FR-021)

1. `count(oltp.service_request) = count(fact_service_request)` = the profile's target
   rows (rejected rows never reach staging, so they do not count towards the target).
2. For each dimension, the number of members and the request count per member match.
3. The set of `request_id` values is identical in both models.
4. The count of requests with a valid resolution, and the sum of resolution hours, match
   within the documented numeric tolerance.

## 5. Benchmark results (files in `results/`)

Described in [contracts/results-schema.md](./contracts/results-schema.md).
