# Contract: Benchmark Queries

Each query is one business question with two SQL expressions of the same logic (FR-014): one
over the normalized OLTP tables and one over the star schema. Both must return the same
columns, in the same order, with the same rows (FR-022). Every query has a deterministic
`ORDER BY` including a tie-breaker, so results can be compared row by row.

Each query lives in two files, `sql/oltp/<id>.sql` and `sql/olap/<id>.sql`, with the business
question as a header comment.

## Analytical queries (measured, count towards SC-003)

| Id | Business question | Shape | Output columns |
|---|---|---|---|
| `q1_volume_by_type_month_borough` | How many requests of each complaint type were created per month in each borough? | aggregation by period, 3 group keys | `borough`, `month`, `complaint_type`, `requests` |
| `q2_top_types_per_zip` | For each ZIP code, which are the 10 most frequent complaint types and how long do they take to resolve on average? | top-N per group (window function) + average of the measure | `zip_code`, `rank`, `complaint_type`, `requests`, `avg_resolution_hours` |
| `q3_closure_rate_agency_channel` | What share of requests does each agency close within 30 days, by channel? | ratio by two dimensions | `agency`, `channel`, `requests`, `closed_within_30d`, `closure_rate` |
| `q4_resolution_p90_agency_quarter` | What is the 90th percentile of resolution time per agency and quarter? | percentile by dimension and period | `agency`, `year`, `quarter`, `resolved_requests`, `p90_resolution_hours` |
| `q5_noise_by_weekday_hour` | In one borough, when do noise complaints concentrate, by day of week and hour? | filter by two dimensions + aggregation | `day_of_week`, `hour`, `requests` |
| `q6_channel_share_by_quarter` | How is each quarter's volume split across channels? | aggregation by period + share of total (window function) | `year`, `quarter`, `channel`, `requests`, `share` |

Parameters are fixed constants, identical on both sides: `q5` uses borough `BROOKLYN` and
complaint types starting with `Noise`.

## Transactional operations (optional, User Story 4 / FR-020)

Measured only with `--include-transactional`, reported in a separate section, and excluded
from SC-003.

| Id | Operation |
|---|---|
| `t1_lookup_by_id` | Read one request by identifier with all its descriptive attributes. Uses a fixed list of identifiers, cycled across repetitions. |
| `t2_insert_request` | Insert one new request, inside a transaction that is rolled back so the data set does not change. |

## Equivalence rules (used by the integration tests)

- Text and integer columns must match exactly.
- Floating-point columns (`avg_resolution_hours`, `p90_resolution_hours`, `closure_rate`,
  `share`) must match within a relative tolerance of 1e-9.
- Percentiles use the same definition on both engines (continuous, linear interpolation).
- Resolution measures use only requests with a valid resolution: closed, and closed at or
  after creation.
- If two engines can order ties differently, the tie-breaker in `ORDER BY` removes the
  ambiguity; a query without a total order is a defect.
