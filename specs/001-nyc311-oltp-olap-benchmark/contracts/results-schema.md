# Contract: Results Files

`run` writes two files per profile (FR-017). They are overwritten on each run and committed
for the full profile (FR-024).

| File | Audience |
|---|---|
| `results/benchmark_<profile>.json` | machines |
| `results/benchmark_<profile>.md` | humans |

## `benchmark_<profile>.json`

```json
{
  "schema_version": 1,
  "profile": "full",
  "official": true,
  "generated_at": "2026-10-12T18:30:00Z",
  "dataset": {
    "source": "NYC 311 Service Requests (erm2-nwe9)",
    "cut_start": "2024-01-01T00:00:00",
    "cut_end": "2026-01-01T00:00:00",
    "rows": 5000000,
    "first_created_at": "…",
    "last_created_at": "…"
  },
  "environment": {
    "os": "…", "cpu": "…", "cores": 10, "memory_gb": 16,
    "python": "3.13.9",
    "postgresql": "17.x", "postgresql_settings": {"max_parallel_workers_per_gather": "…", "shared_buffers": "…", "work_mem": "…"},
    "duckdb": "1.5.x", "duckdb_settings": {"threads": 10, "memory_limit": "…"}
  },
  "method": {"warmup_runs": 1, "measured_runs": 10, "timer": "perf_counter, execute + full fetch"},
  "queries": [
    {
      "id": "q1_volume_by_type_month_borough",
      "group": "analytical",
      "question": "…",
      "result_rows": 1234,
      "oltp": {"runs_ms": [..], "median_ms": 0.0, "p95_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0},
      "olap": {"runs_ms": [..], "median_ms": 0.0, "p95_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0},
      "speedup": 0.0
    }
  ],
  "significance": {
    "evaluated": true,
    "rule": "OLAP at least 3x faster on the median in at least two thirds of analytical queries",
    "queries_meeting_3x": 0,
    "analytical_queries": 6,
    "reached": false
  }
}
```

Rules:

- `speedup` is `oltp.median_ms / olap.median_ms`; above 1 means the analytical model is
  faster.
- `official` is true only for the full profile. For the quick profile `significance.evaluated`
  is false and `reached` is null (FR-026).
- `runs_ms` keeps every measured run so the statistics can be recomputed.
- Queries of group `transactional` appear only when they were requested and are not counted
  in `significance`.

## `benchmark_<profile>.md`

1. A header line with profile, row count, date, and for the quick profile a warning that the
   timings are not the official ones.
2. One table of analytical queries: question, OLTP median, OLAP median, p95 of each, speedup,
   and which model wins (SC-007).
3. The significance verdict as one sentence, stated whether it is reached or not (FR-019).
4. A separate table for transactional operations, if measured.
5. Environment and method, as in the JSON.
