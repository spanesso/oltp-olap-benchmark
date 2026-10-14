# Benchmark results: full profile

5,000,000 requests from NYC 311 Service Requests (erm2-nwe9), created 2024-01-01T00:00:00 to 2025-06-10T09:03:00. Generated 2026-10-14T22:13:05Z.

## Analytical queries

Times in milliseconds: median, with the 95th percentile in parentheses.

| Query | Question | OLTP (PostgreSQL) | OLAP (DuckDB) | Winner |
|---|---|---:|---:|---|
| `q1` | How many requests of each complaint type were created per month in each borough? | 4,334.1 (5,701.1) | 86.0 (165.4) | OLAP, 50.4x faster |
| `q2` | For each ZIP code, which are the 10 most frequent complaint types and how long do they take to resolve on average? | 2,544.2 (3,794.5) | 51.4 (63.1) | OLAP, 49.5x faster |
| `q3` | What share of requests does each agency close within 30 days, by channel? | 907.4 (1,591.4) | 19.2 (41.3) | OLAP, 47.3x faster |
| `q4` | What is the 90th percentile of resolution time per agency and quarter? | 4,997.3 (5,198.4) | 40.6 (46.6) | OLAP, 123.1x faster |
| `q5` | In Brooklyn, when do noise complaints concentrate, by day of week and hour? | 1,197.6 (1,317.7) | 6.3 (6.9) | OLAP, 191.5x faster |
| `q6` | How is each quarter's volume split across channels? | 2,145.3 (2,286.2) | 21.7 (23.8) | OLAP, 98.7x faster |

## Verdict

**Significance threshold reached.** 6 of 6 analytical queries are at least 3x faster on the OLAP model. Rule: OLAP at least 3x faster on the median in at least two thirds of analytical queries.

## Transactional operations

Not counted in the verdict above.

| Operation | OLTP (PostgreSQL) | OLAP (DuckDB) | Winner |
|---|---:|---:|---|
| Read one request by its identifier, with all its descriptive attributes. | 2.14 | 4.13 | OLTP, 1.9x faster |
| Register one new request (insert inside a transaction that is rolled back, so the commit itself is not measured). | 1.34 | 0.47 | OLAP, 2.9x faster |

## Method

- 1 discarded warm-up run(s), then 10 measured runs per query and model; the 95th percentile is taken over those 10 runs.
- Timer: perf_counter, execute + full fetch, measured from the client.
- For each query, all runs on one model and then all runs on the other; nothing else running concurrently.
- The difference combines two effects: the schema (normalized vs star) and the storage engine (row vs columnar).

## Environment

- Machine: arm, 10 cores, 16.0 GB RAM, macOS-27.0.1-arm64-arm-64bit-Mach-O
- Python 3.13.9
- PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) (docker container, reached over local TCP): max_parallel_workers_per_gather = 2, max_parallel_workers = 8, shared_buffers = 128MB, work_mem = 4MB, jit = on
- DuckDB 1.5.6 (embedded in the benchmark process): threads = 10, memory_limit = 12.7 GiB

## Execution plans

### q1: How many requests of each complaint type were created per month in each borough?

**OLTP (PostgreSQL)**

```
Sort  (cost=2122533.20..2135033.55 rows=5000137 width=138) (actual time=8837.166..8840.993 rows=13367 loops=1)
  Sort Key: b.name COLLATE "C", (to_char((date_trunc('month'::text, r.created_at)), 'YYYY-MM'::text)), ct.name COLLATE "C"
  Sort Method: quicksort  Memory: 1706kB
  Buffers: shared hit=10528 read=36181
  ->  HashAggregate  (cost=672990.13..848385.56 rows=5000137 width=138) (actual time=8773.537..8786.246 rows=13367 loops=1)
        Group Key: b.name, date_trunc('month'::text, r.created_at), ct.name
        Planned Partitions: 128  Batches: 1  Memory Usage: 3089kB
        Buffers: shared hit=10528 read=36181
        ->  Hash Join  (cost=73.84..171413.88 rows=5000137 width=42) (actual time=241.289..6790.347 rows=5000000 loops=1)
              Hash Cond: (d.complaint_type_id = ct.complaint_type_id)
              Buffers: shared hit=10528 read=36181
              ->  Hash Join  (cost=67.27..145507.59 rows=5000137 width=21) (actual time=0.712..4981.300 rows=5000000 loops=1)
                    Hash Cond: (r.descriptor_id = d.descriptor_id)
                    Buffers: shared hit=10526 read=36181
                    ->  Hash Join  (cost=31.41..132299.78 rows=5000137 width=21) (actual time=0.324..3759.663 rows=5000000 loops=1)
                          Hash Cond: (l.borough_id = b.borough_id)
                          Buffers: shared hit=10517 read=36181
                          ->  Hash Join  (cost=30.27..109902.20 rows=5000137 width=16) (actual time=0.286..2685.670 rows=5000000 loops=1)
                                Hash Cond: (r.location_id = l.location_id)
                                Buffers: shared hit=10516 read=36181
                                ->  Seq Scan on service_request r  (cost=0.00..96690.37 rows=5000137 width=16) (actual time=0.031..1276.984 rows=5000000 loops=1)
                                      Buffers: shared hit=10508 read=36181
                                ->  Hash  (cost=17.90..17.90 rows=990 width=8) (actual time=0.225..0.235 rows=990 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 47kB
                                      Buffers: shared hit=8
                                      ->  Seq Scan on location l  (cost=0.00..17.90 rows=990 width=8) (actual time=0.024..0.129 rows=990 loops=1)
                                            Buffers: shared hit=8
                          ->  Hash  (cost=1.06..1.06 rows=6 width=13) (actual time=0.026..0.035 rows=6 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                Buffers: shared hit=1
                                ->  Seq Scan on borough b  (cost=0.00..1.06 rows=6 width=13) (actual time=0.022..0.031 rows=6 loops=1)
                                      Buffers: shared hit=1
                    ->  Hash  (cost=20.94..20.94 rows=1194 width=8) (actual time=0.335..0.336 rows=1194 loops=1)
                          Buckets: 2048  Batches: 1  Memory Usage: 63kB
                          Buffers: shared hit=9
                          ->  Seq Scan on complaint_descriptor d  (cost=0.00..20.94 rows=1194 width=8) (actual time=0.070..0.218 rows=1194 loops=1)
                                Buffers: shared hit=9
              ->  Hash  (cost=4.03..4.03 rows=203 width=21) (actual time=240.511..240.512 rows=203 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 19kB
                    Buffers: shared hit=2
                    ->  Seq Scan on complaint_type ct  (cost=0.00..4.03 rows=203 width=21) (actual time=240.356..240.427 rows=203 loops=1)
                          Buffers: shared hit=2
Planning:
  Buffers: shared hit=42
Planning Time: 2.230 ms
JIT:
  Functions: 39
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 7.401 ms (Deform 4.161 ms), Inlining 30.997 ms, Optimization 136.373 ms, Emission 78.065 ms, Total 252.835 ms
Execution Time: 8856.188 ms
```

**OLAP (DuckDB)**

```
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
EXPLAIN ANALYZE -- Q1: How many requests of each complaint type were created per month in each borough? SELECT     l.borough,     printf('%d-%02d', d.year, d.month) AS month,     c.complaint_type,     count(*) AS requests FROM fact_service_request f JOIN dim_location l ON l.location_key = f.location_key JOIN dim_date d ON d.date_key = f.date_key JOIN dim_complaint c ON c.complaint_key = f.complaint_key GROUP BY l.borough, d.year, d.month, c.complaint_type ORDER BY l.borough, month, c.complaint_type; 
┌────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────┐│
││              Total Time: 0.120s              ││
│└──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
┌───────────────────────────┐
│           QUERY           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      EXPLAIN_ANALYZE      │
│    ────────────────────   │
│                           │
│           0 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│             #1            │
│             #2            │
│             #3            │
│                           │
│                           │
│                           │
│        13,367 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│          ORDER_BY         │
│    ────────────────────   │
│       l.borough ASC       │
│ printf('%d-%02d', d."year"│
│      , d."month") ASC     │
│    c.complaint_type ASC   │
│                           │
│                           │
│                           │
│        13,367 rows        │
│           0.01s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_string_│
│        uhugeint(#0)       │
│             #1            │
│             #2            │
│             #3            │
│                           │
│                           │
│                           │
│        13,367 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│          borough          │
│           month           │
│       complaint_type      │
│          requests         │
│                           │
│                           │
│                           │
│        13,367 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│__internal_decompress_integ│
│   ral_smallint(#1, 2024)  │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│        13,367 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│       HASH_GROUP_BY       │
│    ────────────────────   │
│          Groups:          │
│             #0            │
│             #1            │
│             #2            │
│             #3            │
│                           │
│        Aggregates:        │
│        count_star()       │
│                           │
│                           │
│                           │
│        13,367 rows        │
│           0.45s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│          borough          │
│            year           │
│           month           │
│       complaint_type      │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_integra│
│    l_utinyint(#0, 2024)   │
│             #1            │
│             #2            │
│__internal_compress_string_│
│        uhugeint(#3)       │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.01s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        │
│location_key = location_key├────────────────────────────────────────────────────────────────────────┐
│                           │                                                                        │
│                           │                                                                        │
│                           │                                                                        │
│       5,000,000 rows      │                                                                        │
│           0.03s           │                                                                        │
└─────────────┬─────────────┘                                                                        │
┌─────────────┴─────────────┐                                                          ┌─────────────┴─────────────┐
│         HASH_JOIN         │                                                          │         TABLE_SCAN        │
│    ────────────────────   │                                                          │    ────────────────────   │
│      Join Type: INNER     │                                                          │           Table:          │
│                           │                                                          │   olap.main.dim_location  │
│        Conditions:        │                                                          │                           │
│      complaint_key =      │                                                          │   Type: Sequential Scan   │
│        complaint_key      │                                                          │                           │
│                           ├───────────────────────────────────────────┐              │        Projections:       │
│                           │                                           │              │        location_key       │
│                           │                                           │              │          borough          │
│                           │                                           │              │                           │
│           0.01s           │                                           │              │                           │
│                           │                                           │              │                           │
│       5,000,000 rows      │                                           │              │          990 rows         │
│          (0.01s)          │                                           │              │           0.00s           │
└─────────────┬─────────────┘                                           │              └───────────────────────────┘
┌─────────────┴─────────────┐                             ┌─────────────┴─────────────┐
│         HASH_JOIN         │                             │         TABLE_SCAN        │
│    ────────────────────   │                             │    ────────────────────   │
│      Join Type: INNER     │                             │           Table:          │
│                           │                             │  olap.main.dim_complaint  │
│        Conditions:        │                             │                           │
│    date_key = date_key    │                             │   Type: Sequential Scan   │
│                           │                             │                           │
│                           ├──────────────┐              │        Projections:       │
│                           │              │              │       complaint_key       │
│                           │              │              │       complaint_type      │
│           0.02s           │              │              │                           │
│                           │              │              │                           │
│                           │              │              │                           │
│       5,000,000 rows      │              │              │         1,194 rows        │
│          (0.02s)          │              │              │           0.00s           │
└─────────────┬─────────────┘              │              └───────────────────────────┘
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         TABLE_SCAN        ││         TABLE_SCAN        │
│    ────────────────────   ││    ────────────────────   │
│           Table:          ││           Table:          │
│         olap.main         ││     olap.main.dim_date    │
│   .fact_service_request   ││                           │
│                           ││   Type: Sequential Scan   │
│   Type: Sequential Scan   ││                           │
│                           ││        Projections:       │
│        Projections:       ││          date_key         │
│        location_key       ││            year           │
│          date_key         ││           month           │
│       complaint_key       ││                           │
│                           ││                           │
│      Dynamic Filters:     ││                           │
│ optional: location_key>=1 ││                           │
│        AND optional:      ││           0.00s           │
│      location_key<=990    ││                           │
│    optional: date_key>    ││                           │
│  =20240101 AND optional:  ││                           │
│     date_key<=20250610    ││                           │
│ optional: complaint_key>=1││                           │
│        AND optional:      ││                           │
│     complaint_key<=1194   ││                           │
│                           ││                           │
│                           ││                           │
│                           ││                           │
│       5,000,000 rows      ││          527 rows         │
│           0.03s           ││          (0.00s)          │
└───────────────────────────┘└───────────────────────────┘

```

### q2: For each ZIP code, which are the 10 most frequent complaint types and how long do they take to resolve on average?

**OLTP (PostgreSQL)**

```
Sort  (cost=387025.18..387233.26 rows=83230 width=79) (actual time=3162.644..3173.119 rows=2521 loops=1)
  Sort Key: ranked.zip_code COLLATE "C", ranked.rank
  Sort Method: quicksort  Memory: 286kB
  Buffers: shared hit=11691 read=35093
  ->  Subquery Scan on ranked  (cost=347364.02..376523.79 rows=83230 width=79) (actual time=3088.959..3171.793 rows=2521 loops=1)
        Buffers: shared hit=11691 read=35093
        ->  WindowAgg  (cost=347364.02..375691.49 rows=83230 width=79) (actual time=3088.944..3171.084 rows=2521 loops=1)
              Run Condition: (row_number() OVER (?) <= 10)
              Buffers: shared hit=11691 read=35093
              ->  Incremental Sort  (cost=347363.68..374026.89 rows=83230 width=71) (actual time=3088.877..3166.521 rows=24553 loops=1)
                    Sort Key: per_zip.zip_code, per_zip.requests DESC, ((per_zip.complaint_type)::text) COLLATE "C"
                    Presorted Key: per_zip.zip_code
                    Full-sort Groups: 206  Sort Method: quicksort  Average Memory: 30kB  Peak Memory: 30kB
                    Pre-sorted Groups: 269  Sort Method: quicksort  Average Memory: 25kB  Peak Memory: 25kB
                    Buffers: shared hit=11691 read=35093
                    ->  Subquery Scan on per_zip  (cost=347234.94..369361.61 rows=83230 width=71) (actual time=3088.662..3150.584 rows=24553 loops=1)
                          Buffers: shared hit=11691 read=35093
                          ->  Finalize GroupAggregate  (cost=347234.94..369361.61 rows=83230 width=39) (actual time=3088.650..3147.211 rows=24553 loops=1)
                                Group Key: l.zip_code, ct.name
                                Buffers: shared hit=11691 read=35093
                                ->  Gather Merge  (cost=347234.94..366656.63 rows=166460 width=63) (actual time=3088.503..3124.546 rows=63426 loops=1)
                                      Workers Planned: 2
                                      Workers Launched: 2
                                      Buffers: shared hit=11691 read=35093
                                      ->  Sort  (cost=346234.92..346442.99 rows=83230 width=63) (actual time=3053.066..3059.152 rows=21142 loops=3)
                                            Sort Key: l.zip_code, ct.name
                                            Sort Method: quicksort  Memory: 2810kB
                                            Buffers: shared hit=11691 read=35093
                                            Worker 0:  Sort Method: quicksort  Memory: 2829kB
                                            Worker 1:  Sort Method: quicksort  Memory: 2821kB
                                            ->  Partial HashAggregate  (cost=302915.25..336300.52 rows=83230 width=63) (actual time=3014.243..3017.257 rows=21142 loops=3)
                                                  Group Key: l.zip_code, ct.name
                                                  Planned Partitions: 4  Batches: 1  Memory Usage: 4625kB
                                                  Buffers: shared hit=11675 read=35093
                                                  Worker 0:  Batches: 1  Memory Usage: 4625kB
                                                  Worker 1:  Batches: 1  Memory Usage: 4625kB
                                                  ->  Hash Join  (cost=72.71..84159.30 rows=2083390 width=39) (actual time=16.905..1603.651 rows=1666667 loops=3)
                                                        Hash Cond: (d.complaint_type_id = ct.complaint_type_id)
                                                        Buffers: shared hit=11675 read=35093
                                                        ->  Hash Join  (cost=66.14..78569.66 rows=2083390 width=26) (actual time=0.775..1229.918 rows=1666667 loops=3)
                                                              Hash Cond: (r.descriptor_id = d.descriptor_id)
                                                              Buffers: shared hit=11647 read=35093
                                                              ->  Hash Join  (cost=30.27..73045.48 rows=2083390 width=26) (actual time=0.396..810.179 rows=1666667 loops=3)
                                                                    Hash Cond: (r.location_id = l.location_id)
                                                                    Buffers: shared hit=11620 read=35093
                                                                    ->  Parallel Seq Scan on service_request r  (cost=0.00..67522.90 rows=2083390 width=24) (actual time=0.037..286.545 rows=1666667 loops=3)
                                                                          Buffers: shared hit=11596 read=35093
                                                                    ->  Hash  (cost=17.90..17.90 rows=990 width=10) (actual time=0.342..0.343 rows=990 loops=3)
                                                                          Buckets: 1024  Batches: 1  Memory Usage: 51kB
                                                                          Buffers: shared hit=24
                                                                          ->  Seq Scan on location l  (cost=0.00..17.90 rows=990 width=10) (actual time=0.018..0.159 rows=990 loops=3)
                                                                                Buffers: shared hit=24
                                                              ->  Hash  (cost=20.94..20.94 rows=1194 width=8) (actual time=0.361..0.362 rows=1194 loops=3)
                                                                    Buckets: 2048  Batches: 1  Memory Usage: 63kB
                                                                    Buffers: shared hit=27
                                                                    ->  Seq Scan on complaint_descriptor d  (cost=0.00..20.94 rows=1194 width=8) (actual time=0.035..0.183 rows=1194 loops=3)
                                                                          Buffers: shared hit=27
                                                        ->  Hash  (cost=4.03..4.03 rows=203 width=21) (actual time=16.017..16.018 rows=203 loops=3)
                                                              Buckets: 1024  Batches: 1  Memory Usage: 19kB
                                                              Buffers: shared hit=6
                                                              ->  Seq Scan on complaint_type ct  (cost=0.00..4.03 rows=203 width=21) (actual time=15.942..15.973 rows=203 loops=3)
                                                                    Buffers: shared hit=6
Planning:
  Buffers: shared hit=38
Planning Time: 2.638 ms
JIT:
  Functions: 103
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 7.576 ms (Deform 2.004 ms), Inlining 0.000 ms, Optimization 3.225 ms, Emission 44.819 ms, Total 55.620 ms
Execution Time: 3177.664 ms
```

**OLAP (DuckDB)**

```
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
EXPLAIN ANALYZE -- Q2: For each ZIP code, which are the 10 most frequent complaint types and how long do -- they take to resolve on average? WITH per_zip AS (     SELECT         l.zip_code,         c.complaint_type,         count(*) AS requests,         avg(f.resolution_hours) AS avg_resolution_hours     FROM fact_service_request f     JOIN dim_location l ON l.location_key = f.location_key     JOIN dim_complaint c ON c.complaint_key = f.complaint_key     GROUP BY l.zip_code, c.complaint_type ), ranked AS (     SELECT         *,         row_number() OVER (PARTITION BY zip_code ORDER BY requests DESC, complaint_type) AS rank     FROM per_zip ) SELECT zip_code, rank, complaint_type, requests, avg_resolution_hours FROM ranked WHERE rank <= 10 ORDER BY zip_code, rank; 
┌────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────┐│
││              Total Time: 0.0503s             ││
│└──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
┌───────────────────────────┐
│           QUERY           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      EXPLAIN_ANALYZE      │
│    ────────────────────   │
│                           │
│           0 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│             #1            │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│         2,521 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│          ORDER_BY         │
│    ────────────────────   │
│    ranked.zip_code ASC    │
│      ranked.rank ASC      │
│                           │
│                           │
│                           │
│         2,521 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_string_│
│        ubigint(#0)        │
│             #1            │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│         2,521 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│          zip_code         │
│            rank           │
│       complaint_type      │
│          requests         │
│    avg_resolution_hours   │
│                           │
│                           │
│                           │
│         2,521 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│           FILTER          │
│    ────────────────────   │
│        (rank <= 10)       │
│                           │
│                           │
│                           │
│         2,521 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│             #0            │
│             #1            │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│        24,553 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│           WINDOW          │
│    ────────────────────   │
│        Projections:       │
│     ROW_NUMBER() OVER     │
│   (PARTITION BY zip_code  │
│   ORDER BY requests DESC  │
│         NULLS LAST,       │
│  complaint_type ASC NULLS │
│            LAST)          │
│                           │
│                           │
│                           │
│        24,553 rows        │
│           0.04s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│             #1            │
│             #2            │
│             #3            │
│                           │
│                           │
│                           │
│        24,553 rows        │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│       HASH_GROUP_BY       │
│    ────────────────────   │
│          Groups:          │
│             #0            │
│             #1            │
│                           │
│        Aggregates:        │
│        count_star()       │
│          avg(#2)          │
│                           │
│                           │
│                           │
│        24,553 rows        │
│           0.27s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│          zip_code         │
│       complaint_type      │
│      resolution_hours     │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│             #0            │
│             #1            │
│__internal_compress_string_│
│        ubigint(#2)        │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        │
│location_key = location_key├───────────────────────────────────────────┐
│                           │                                           │
│                           │                                           │
│                           │                                           │
│       5,000,000 rows      │                                           │
│           0.01s           │                                           │
└─────────────┬─────────────┘                                           │
┌─────────────┴─────────────┐                             ┌─────────────┴─────────────┐
│         HASH_JOIN         │                             │         TABLE_SCAN        │
│    ────────────────────   │                             │    ────────────────────   │
│      Join Type: INNER     │                             │           Table:          │
│                           │                             │   olap.main.dim_location  │
│        Conditions:        │                             │                           │
│      complaint_key =      │                             │   Type: Sequential Scan   │
│        complaint_key      │                             │                           │
│                           ├──────────────┐              │        Projections:       │
│                           │              │              │        location_key       │
│                           │              │              │          zip_code         │
│                           │              │              │                           │
│           0.01s           │              │              │                           │
│                           │              │              │                           │
│       5,000,000 rows      │              │              │          990 rows         │
│          (0.01s)          │              │              │           0.00s           │
└─────────────┬─────────────┘              │              └───────────────────────────┘
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         TABLE_SCAN        ││         TABLE_SCAN        │
│    ────────────────────   ││    ────────────────────   │
│           Table:          ││           Table:          │
│         olap.main         ││  olap.main.dim_complaint  │
│   .fact_service_request   ││                           │
│                           ││   Type: Sequential Scan   │
│   Type: Sequential Scan   ││                           │
│                           ││        Projections:       │
│        Projections:       ││       complaint_key       │
│        location_key       ││       complaint_type      │
│       complaint_key       ││                           │
│      resolution_hours     ││                           │
│                           ││                           │
│      Dynamic Filters:     ││                           │
│ optional: location_key>=1 ││           0.00s           │
│        AND optional:      ││                           │
│      location_key<=990    ││                           │
│ optional: complaint_key>=1││                           │
│        AND optional:      ││                           │
│     complaint_key<=1194   ││                           │
│                           ││                           │
│                           ││                           │
│                           ││                           │
│       5,000,000 rows      ││         1,194 rows        │
│           0.02s           ││          (0.00s)          │
└───────────────────────────┘└───────────────────────────┘

```

### q3: What share of requests does each agency close within 30 days, by channel?

**OLTP (PostgreSQL)**

```
Sort  (cost=122128.96..122129.15 rows=75 width=98) (actual time=1499.795..1504.440 rows=50 loops=1)
  Sort Key: a.code COLLATE "C", c.name COLLATE "C"
  Sort Method: quicksort  Memory: 28kB
  Buffers: shared hit=12752 read=33981
  ->  Finalize GroupAggregate  (cost=122106.31..122126.63 rows=75 width=98) (actual time=1499.670..1504.382 rows=50 loops=1)
        Group Key: a.code, c.name
        Buffers: shared hit=12752 read=33981
        ->  Gather Merge  (cost=122106.31..122123.81 rows=150 width=26) (actual time=1499.630..1504.306 rows=142 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=12752 read=33981
              ->  Sort  (cost=121106.29..121106.48 rows=75 width=26) (actual time=1485.173..1485.178 rows=47 loops=3)
                    Sort Key: a.code, c.name
                    Sort Method: quicksort  Memory: 27kB
                    Buffers: shared hit=12752 read=33981
                    Worker 0:  Sort Method: quicksort  Memory: 27kB
                    Worker 1:  Sort Method: quicksort  Memory: 27kB
                    ->  Partial HashAggregate  (cost=121103.20..121103.95 rows=75 width=26) (actual time=1485.100..1485.111 rows=47 loops=3)
                          Group Key: a.code, c.name
                          Batches: 1  Memory Usage: 24kB
                          Buffers: shared hit=12736 read=33981
                          Worker 0:  Batches: 1  Memory Usage: 32kB
                          Worker 1:  Batches: 1  Memory Usage: 32kB
                          ->  Hash Join  (cost=2.45..84643.88 rows=2083390 width=26) (actual time=13.601..939.005 rows=1666667 loops=3)
                                Hash Cond: (r.channel_id = c.channel_id)
                                Buffers: shared hit=12736 read=33981
                                ->  Hash Join  (cost=1.34..74538.33 rows=2083390 width=24) (actual time=0.069..590.807 rows=1666667 loops=3)
                                      Hash Cond: (r.agency_id = a.agency_id)
                                      Buffers: shared hit=12711 read=33981
                                      ->  Parallel Seq Scan on service_request r  (cost=0.00..67522.90 rows=2083390 width=24) (actual time=0.036..185.072 rows=1666667 loops=3)
                                            Buffers: shared hit=12708 read=33981
                                      ->  Hash  (cost=1.15..1.15 rows=15 width=8) (actual time=0.022..0.022 rows=15 loops=3)
                                            Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                            Buffers: shared hit=3
                                            ->  Seq Scan on agency a  (cost=0.00..1.15 rows=15 width=8) (actual time=0.017..0.018 rows=15 loops=3)
                                                  Buffers: shared hit=3
                                ->  Hash  (cost=1.05..1.05 rows=5 width=10) (actual time=13.502..13.503 rows=5 loops=3)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      Buffers: shared hit=3
                                      ->  Seq Scan on channel c  (cost=0.00..1.05 rows=5 width=10) (actual time=13.483..13.487 rows=5 loops=3)
                                            Buffers: shared hit=3
Planning:
  Buffers: shared hit=4
Planning Time: 1.328 ms
JIT:
  Functions: 72
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 5.288 ms (Deform 2.083 ms), Inlining 0.000 ms, Optimization 1.314 ms, Emission 39.320 ms, Total 45.922 ms
Execution Time: 1507.759 ms
```

**OLAP (DuckDB)**

```
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
EXPLAIN ANALYZE -- Q3: What share of requests does each agency close within 30 days, by channel? SELECT     a.code AS agency,     c.name AS channel,     count(*) AS requests,     count(*) FILTER (WHERE f.closed_within_30d) AS closed_within_30d,     CAST(count(*) FILTER (WHERE f.closed_within_30d) AS DOUBLE) / count(*) AS closure_rate FROM fact_service_request f JOIN dim_agency a ON a.agency_key = f.agency_key JOIN dim_channel c ON c.channel_key = f.channel_key GROUP BY a.code, c.name ORDER BY a.code, c.name; 
┌────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────┐│
││              Total Time: 0.0187s             ││
│└──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
┌───────────────────────────┐
│           QUERY           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      EXPLAIN_ANALYZE      │
│    ────────────────────   │
│                           │
│           0 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│__internal_decompress_strin│
│           g(#1)           │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          50 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│          ORDER_BY         │
│    ────────────────────   │
│         a.code ASC        │
│        c."name" ASC       │
│                           │
│                           │
│                           │
│          50 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_string_│
│        ubigint(#0)        │
│__internal_compress_string_│
│        ubigint(#1)        │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          50 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│           agency          │
│          channel          │
│          requests         │
│     closed_within_30d     │
│        closure_rate       │
│                           │
│                           │
│                           │
│          50 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│__internal_decompress_strin│
│           g(#1)           │
│             #2            │
│             #3            │
│                           │
│                           │
│                           │
│          50 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│       HASH_GROUP_BY       │
│    ────────────────────   │
│          Groups:          │
│             #0            │
│             #1            │
│                           │
│        Aggregates:        │
│        count_star()       │
│ count_star() FILTER (WHERE│
│       #0) Filter: #0      │
│                           │
│                           │
│                           │
│          50 rows          │
│           0.10s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│            code           │
│            name           │
│     closed_within_30d     │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│             #0            │
│__internal_compress_string_│
│        ubigint(#1)        │
│__internal_compress_string_│
│        ubigint(#2)        │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.01s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        │
│ channel_key = channel_key ├───────────────────────────────────────────┐
│                           │                                           │
│                           │                                           │
│                           │                                           │
│       5,000,000 rows      │                                           │
│           0.01s           │                                           │
└─────────────┬─────────────┘                                           │
┌─────────────┴─────────────┐                             ┌─────────────┴─────────────┐
│         HASH_JOIN         │                             │         TABLE_SCAN        │
│    ────────────────────   │                             │    ────────────────────   │
│      Join Type: INNER     │                             │           Table:          │
│                           │                             │   olap.main.dim_channel   │
│        Conditions:        │                             │                           │
│  agency_key = agency_key  │                             │   Type: Sequential Scan   │
│                           │                             │                           │
│                           ├──────────────┐              │        Projections:       │
│                           │              │              │        channel_key        │
│                           │              │              │            name           │
│           0.01s           │              │              │                           │
│                           │              │              │                           │
│                           │              │              │                           │
│       5,000,000 rows      │              │              │           5 rows          │
│          (0.01s)          │              │              │           0.00s           │
└─────────────┬─────────────┘              │              └───────────────────────────┘
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         TABLE_SCAN        ││         TABLE_SCAN        │
│    ────────────────────   ││    ────────────────────   │
│           Table:          ││           Table:          │
│         olap.main         ││    olap.main.dim_agency   │
│   .fact_service_request   ││                           │
│                           ││   Type: Sequential Scan   │
│   Type: Sequential Scan   ││                           │
│                           ││        Projections:       │
│        Projections:       ││         agency_key        │
│         agency_key        ││            code           │
│        channel_key        ││                           │
│     closed_within_30d     ││                           │
│                           ││                           │
│      Dynamic Filters:     ││                           │
│  optional: agency_key>=1  ││           0.00s           │
│  AND optional: agency_key<││                           │
│            =15            ││                           │
│  optional: channel_key>=1 ││                           │
│  AND optional: channel_key││                           │
│            <=5            ││                           │
│                           ││                           │
│                           ││                           │
│                           ││                           │
│       5,000,000 rows      ││          15 rows          │
│           0.01s           ││          (0.00s)          │
└───────────────────────────┘└───────────────────────────┘

```

### q4: What is the 90th percentile of resolution time per agency and quarter?

**OLTP (PostgreSQL)**

```
Sort  (cost=879566.70..883733.48 rows=1666712 width=124) (actual time=5724.141..5738.944 rows=84 loops=1)
  Sort Key: a.code COLLATE "C", (((EXTRACT(year FROM r.created_at)))::integer), (((EXTRACT(quarter FROM r.created_at)))::integer)
  Sort Method: quicksort  Memory: 30kB
  Buffers: shared hit=14051 read=32829, temp read=54886 written=54996
  ->  GroupAggregate  (cost=213390.23..490841.91 rows=1666712 width=124) (actual time=1701.551..5738.645 rows=84 loops=1)
        Group Key: a.code, (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at))
        Buffers: shared hit=14051 read=32829, temp read=54886 written=54996
        ->  Gather Merge  (cost=213390.23..407506.31 rows=1666712 width=84) (actual time=1698.600..3229.315 rows=4914706 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=14051 read=32829, temp read=50529 written=50616
              ->  Sort  (cost=212390.21..214126.36 rows=694463 width=84) (actual time=1668.864..1975.448 rows=1638235 loops=3)
                    Sort Key: a.code, (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at))
                    Sort Method: external merge  Disk: 68672kB
                    Buffers: shared hit=14051 read=32829, temp read=50529 written=50616
                    Worker 0:  Sort Method: external merge  Disk: 66848kB
                    Worker 1:  Sort Method: external merge  Disk: 66728kB
                    ->  Hash Join  (cost=1.34..78543.06 rows=694463 width=84) (actual time=107.256..772.305 rows=1638235 loops=3)
                          Hash Cond: (r.agency_id = a.agency_id)
                          Buffers: shared hit=13923 read=32829
                          ->  Parallel Seq Scan on service_request r  (cost=0.00..72731.38 rows=694463 width=20) (actual time=107.139..287.772 rows=1638235 loops=3)
                                Filter: (closed_at >= created_at)
                                Rows Removed by Filter: 28431
                                Buffers: shared hit=13860 read=32829
                          ->  Hash  (cost=1.15..1.15 rows=15 width=8) (actual time=0.038..0.039 rows=15 loops=3)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                Buffers: shared hit=3
                                ->  Seq Scan on agency a  (cost=0.00..1.15 rows=15 width=8) (actual time=0.030..0.032 rows=15 loops=3)
                                      Buffers: shared hit=3
Planning:
  Buffers: shared hit=4
Planning Time: 1.193 ms
JIT:
  Functions: 43
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 3.695 ms (Deform 1.467 ms), Inlining 141.639 ms, Optimization 100.029 ms, Emission 79.763 ms, Total 325.125 ms
Execution Time: 5748.722 ms
```

**OLAP (DuckDB)**

```
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
EXPLAIN ANALYZE -- Q4: What is the 90th percentile of resolution time per agency and quarter? SELECT     a.code AS agency,     CAST(d.year AS INTEGER) AS year,     CAST(d.quarter AS INTEGER) AS quarter,     count(*) AS resolved_requests,     quantile_cont(f.resolution_hours, 0.9) AS p90_resolution_hours FROM fact_service_request f JOIN dim_agency a ON a.agency_key = f.agency_key JOIN dim_date d ON d.date_key = f.date_key WHERE f.has_valid_resolution GROUP BY a.code, d.year, d.quarter ORDER BY a.code, year, quarter; 
┌────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────┐│
││              Total Time: 0.0554s             ││
│└──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
┌───────────────────────────┐
│           QUERY           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      EXPLAIN_ANALYZE      │
│    ────────────────────   │
│                           │
│           0 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│__internal_decompress_integ│
│   ral_integer(#1, 2024)   │
│__internal_decompress_integ│
│     ral_integer(#2, 1)    │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          84 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│          ORDER_BY         │
│    ────────────────────   │
│         a.code ASC        │
│ CAST(d."year" AS INTEGER) │
│             ASC           │
│    CAST(d."quarter" AS    │
│        INTEGER) ASC       │
│                           │
│                           │
│                           │
│          84 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_string_│
│        ubigint(#0)        │
│__internal_compress_integra│
│    l_utinyint(#1, 2024)   │
│__internal_compress_integra│
│     l_utinyint(#2, 1)     │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          84 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│           agency          │
│            year           │
│          quarter          │
│     resolved_requests     │
│    p90_resolution_hours   │
│                           │
│                           │
│                           │
│          84 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_strin│
│           g(#0)           │
│__internal_decompress_integ│
│   ral_smallint(#1, 2024)  │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          84 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│       HASH_GROUP_BY       │
│    ────────────────────   │
│          Groups:          │
│             #0            │
│             #1            │
│             #2            │
│                           │
│        Aggregates:        │
│        count_star()       │
│     quantile_cont(#3)     │
│                           │
│                           │
│                           │
│          84 rows          │
│           0.33s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│            code           │
│            year           │
│          quarter          │
│      resolution_hours     │
│                           │
│                           │
│                           │
│       4,914,706 rows      │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│             #0            │
│__internal_compress_integra│
│    l_utinyint(#1, 2024)   │
│             #2            │
│__internal_compress_string_│
│        ubigint(#3)        │
│                           │
│                           │
│                           │
│       4,914,706 rows      │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        │
│  agency_key = agency_key  ├───────────────────────────────────────────┐
│                           │                                           │
│                           │                                           │
│                           │                                           │
│       4,914,706 rows      │                                           │
│           0.01s           │                                           │
└─────────────┬─────────────┘                                           │
┌─────────────┴─────────────┐                             ┌─────────────┴─────────────┐
│         HASH_JOIN         │                             │         TABLE_SCAN        │
│    ────────────────────   │                             │    ────────────────────   │
│      Join Type: INNER     │                             │           Table:          │
│                           │                             │    olap.main.dim_agency   │
│        Conditions:        │                             │                           │
│    date_key = date_key    │                             │   Type: Sequential Scan   │
│                           │                             │                           │
│                           ├──────────────┐              │        Projections:       │
│                           │              │              │         agency_key        │
│                           │              │              │            code           │
│           0.01s           │              │              │                           │
│                           │              │              │                           │
│                           │              │              │                           │
│       4,914,706 rows      │              │              │          15 rows          │
│          (0.01s)          │              │              │           0.00s           │
└─────────────┬─────────────┘              │              └───────────────────────────┘
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         TABLE_SCAN        ││         TABLE_SCAN        │
│    ────────────────────   ││    ────────────────────   │
│           Table:          ││           Table:          │
│         olap.main         ││     olap.main.dim_date    │
│   .fact_service_request   ││                           │
│                           ││   Type: Sequential Scan   │
│   Type: Sequential Scan   ││                           │
│                           ││        Projections:       │
│        Projections:       ││          date_key         │
│         agency_key        ││            year           │
│          date_key         ││          quarter          │
│      resolution_hours     ││                           │
│                           ││                           │
│          Filters:         ││                           │
│    has_valid_resolution   ││                           │
│                           ││           0.00s           │
│      Dynamic Filters:     ││                           │
│  optional: agency_key>=1  ││                           │
│  AND optional: agency_key<││                           │
│            =15            ││                           │
│    optional: date_key>    ││                           │
│  =20240101 AND optional:  ││                           │
│     date_key<=20250610    ││                           │
│                           ││                           │
│                           ││                           │
│                           ││                           │
│       4,914,706 rows      ││          527 rows         │
│           0.04s           ││          (0.00s)          │
└───────────────────────────┘└───────────────────────────┘

```

### q5: In Brooklyn, when do noise complaints concentrate, by day of week and hour?

**OLTP (PostgreSQL)**

```
Sort  (cost=22727.17..22809.27 rows=32842 width=80) (actual time=1388.049..1388.060 rows=168 loops=1)
  Sort Key: (((EXTRACT(isodow FROM r.created_at)))::integer), (((EXTRACT(hour FROM r.created_at)))::integer)
  Sort Method: quicksort  Memory: 32kB
  Buffers: shared hit=48447 read=277630
  ->  HashAggregate  (cost=19442.43..20263.48 rows=32842 width=80) (actual time=1387.785..1387.981 rows=168 loops=1)
        Group Key: EXTRACT(isodow FROM r.created_at), EXTRACT(hour FROM r.created_at)
        Batches: 1  Memory Usage: 1569kB
        Buffers: shared hit=48447 read=277630
        ->  Hash Join  (cost=17.69..19196.12 rows=32842 width=72) (actual time=0.470..1330.445 rows=272132 loops=1)
              Hash Cond: (r.location_id = l.location_id)
              Buffers: shared hit=48447 read=277630
              ->  Nested Loop  (cost=0.86..17947.72 rows=197050 width=12) (actual time=0.337..1195.056 rows=1093077 loops=1)
                    Buffers: shared hit=48445 read=277627
                    ->  Nested Loop  (cost=0.43..120.30 rows=47 width=4) (actual time=0.307..0.875 rows=53 loops=1)
                          Buffers: shared hit=404 read=17
                          ->  Index Scan using complaint_descriptor_pkey on complaint_descriptor d  (cost=0.28..54.19 rows=1194 width=8) (actual time=0.006..0.218 rows=1194 loops=1)
                                Buffers: shared hit=5 read=10
                          ->  Memoize  (cost=0.15..0.19 rows=1 width=4) (actual time=0.000..0.000 rows=0 loops=1194)
                                Cache Key: d.complaint_type_id
                                Cache Mode: logical
                                Hits: 991  Misses: 203  Evictions: 0  Overflows: 0  Memory Usage: 14kB
                                Buffers: shared hit=399 read=7
                                ->  Index Scan using complaint_type_pkey on complaint_type ct  (cost=0.14..0.18 rows=1 width=4) (actual time=0.001..0.001 rows=0 loops=203)
                                      Index Cond: (complaint_type_id = d.complaint_type_id)
                                      Filter: (name ~~ 'Noise%'::text)
                                      Rows Removed by Filter: 1
                                      Buffers: shared hit=399 read=7
                    ->  Index Scan using service_request_descriptor_idx on service_request r  (cost=0.43..303.55 rows=7576 width=16) (actual time=0.011..20.513 rows=20624 loops=53)
                          Index Cond: (descriptor_id = d.descriptor_id)
                          Buffers: shared hit=48041 read=277610
              ->  Hash  (cost=14.76..14.76 rows=165 width=4) (actual time=0.109..0.110 rows=175 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 15kB
                    Buffers: shared hit=2 read=3
                    ->  Nested Loop  (cost=0.15..14.76 rows=165 width=4) (actual time=0.044..0.092 rows=175 loops=1)
                          Buffers: shared hit=2 read=3
                          ->  Seq Scan on borough b  (cost=0.00..1.07 rows=1 width=4) (actual time=0.006..0.006 rows=1 loops=1)
                                Filter: (name = 'BROOKLYN'::text)
                                Rows Removed by Filter: 5
                                Buffers: shared hit=1
                          ->  Index Scan using location_borough_idx on location l  (cost=0.15..12.04 rows=165 width=8) (actual time=0.038..0.069 rows=175 loops=1)
                                Index Cond: (borough_id = b.borough_id)
                                Buffers: shared hit=1 read=3
Planning:
  Buffers: shared hit=18 read=24
Planning Time: 1.114 ms
Execution Time: 1388.213 ms
```

**OLAP (DuckDB)**

```
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
EXPLAIN ANALYZE -- Q5: In Brooklyn, when do noise complaints concentrate, by day of week and hour? -- day_of_week follows ISO numbering: 1 = Monday ... 7 = Sunday. SELECT     CAST(d.day_of_week AS INTEGER) AS day_of_week,     CAST(f.created_hour AS INTEGER) AS hour,     count(*) AS requests FROM fact_service_request f JOIN dim_location l ON l.location_key = f.location_key JOIN dim_complaint c ON c.complaint_key = f.complaint_key JOIN dim_date d ON d.date_key = f.date_key WHERE l.borough = 'BROOKLYN'   AND c.complaint_type LIKE 'Noise%' GROUP BY d.day_of_week, f.created_hour ORDER BY day_of_week, hour; 
┌────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────┐│
││              Total Time: 0.0077s             ││
│└──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
┌───────────────────────────┐
│           QUERY           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      EXPLAIN_ANALYZE      │
│    ────────────────────   │
│                           │
│           0 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_integ│
│     ral_integer(#0, 1)    │
│__internal_decompress_integ│
│     ral_integer(#1, 0)    │
│             #2            │
│                           │
│                           │
│                           │
│          168 rows         │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│          ORDER_BY         │
│    ────────────────────   │
│   CAST(d.day_of_week AS   │
│        INTEGER) ASC       │
│   CAST(f.created_hour AS  │
│        INTEGER) ASC       │
│                           │
│                           │
│                           │
│          168 rows         │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_integra│
│     l_utinyint(#0, 1)     │
│__internal_compress_integra│
│     l_utinyint(#1, 0)     │
│             #2            │
│                           │
│                           │
│                           │
│          168 rows         │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│        day_of_week        │
│            hour           │
│          requests         │
│                           │
│                           │
│                           │
│          168 rows         │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│   PERFECT_HASH_GROUP_BY   │
│    ────────────────────   │
│          Groups:          │
│             #0            │
│             #1            │
│                           │
│        Aggregates:        │
│        count_star()       │
│                           │
│                           │
│                           │
│          168 rows         │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│        day_of_week        │
│        created_hour       │
│                           │
│                           │
│                           │
│        272,132 rows       │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        │
│    date_key = date_key    ├────────────────────────────────────────────────────────────────────────┐
│                           │                                                                        │
│                           │                                                                        │
│                           │                                                                        │
│        272,132 rows       │                                                                        │
│           0.00s           │                                                                        │
└─────────────┬─────────────┘                                                                        │
┌─────────────┴─────────────┐                                                          ┌─────────────┴─────────────┐
│         HASH_JOIN         │                                                          │         TABLE_SCAN        │
│    ────────────────────   │                                                          │    ────────────────────   │
│      Join Type: INNER     │                                                          │           Table:          │
│                           │                                                          │     olap.main.dim_date    │
│        Conditions:        │                                                          │                           │
│location_key = location_key│                                                          │   Type: Sequential Scan   │
│                           │                                                          │                           │
│                           ├───────────────────────────────────────────┐              │        Projections:       │
│                           │                                           │              │          date_key         │
│                           │                                           │              │        day_of_week        │
│           0.01s           │                                           │              │                           │
│                           │                                           │              │                           │
│                           │                                           │              │                           │
│        272,132 rows       │                                           │              │          527 rows         │
│          (0.01s)          │                                           │              │           0.00s           │
└─────────────┬─────────────┘                                           │              └───────────────────────────┘
┌─────────────┴─────────────┐                             ┌─────────────┴─────────────┐
│         HASH_JOIN         │                             │         TABLE_SCAN        │
│    ────────────────────   │                             │    ────────────────────   │
│      Join Type: INNER     │                             │           Table:          │
│                           │                             │   olap.main.dim_location  │
│        Conditions:        │                             │                           │
│      complaint_key =      │                             │   Type: Sequential Scan   │
│        complaint_key      │                             │                           │
│                           │                             │        Projections:       │
│                           ├──────────────┐              │        location_key       │
│                           │              │              │                           │
│                           │              │              │          Filters:         │
│           0.01s           │              │              │     borough='BROOKLYN'    │
│                           │              │              │                           │
│                           │              │              │                           │
│                           │              │              │                           │
│        539,511 rows       │              │              │          175 rows         │
│          (0.01s)          │              │              │           0.00s           │
└─────────────┬─────────────┘              │              └───────────────────────────┘
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         TABLE_SCAN        ││         TABLE_SCAN        │
│    ────────────────────   ││    ────────────────────   │
│           Table:          ││           Table:          │
│         olap.main         ││  olap.main.dim_complaint  │
│   .fact_service_request   ││                           │
│                           ││   Type: Sequential Scan   │
│   Type: Sequential Scan   ││                           │
│                           ││        Projections:       │
│        Projections:       ││       complaint_key       │
│        location_key       ││                           │
│       complaint_key       ││          Filters:         │
│          date_key         ││  complaint_type>='Noise'  │
│        created_hour       ││ AND complaint_type<'Noisf'│
│                           ││                           │
│      Dynamic Filters:     ││                           │
│  optional: location_key>  ││                           │
│     =119 AND optional:    ││                           │
│      location_key<=293    ││           0.00s           │
│  optional: complaint_key> ││                           │
│     =585 AND optional:    ││                           │
│     complaint_key<=637    ││                           │
│    optional: date_key>    ││                           │
│  =20240101 AND optional:  ││                           │
│     date_key<=20250610    ││                           │
│                           ││                           │
│                           ││                           │
│                           ││                           │
│        539,511 rows       ││          53 rows          │
│           0.02s           ││          (0.00s)          │
└───────────────────────────┘└───────────────────────────┘

```

### q6: How is each quarter's volume split across channels?

**OLTP (PostgreSQL)**

```
Sort  (cost=2553556.45..2566056.79 rows=5000137 width=126) (actual time=3008.410..3008.777 rows=30 loops=1)
  Sort Key: (((EXTRACT(year FROM r.created_at)))::integer), (((EXTRACT(quarter FROM r.created_at)))::integer), c.name COLLATE "C"
  Sort Method: quicksort  Memory: 27kB
  Buffers: shared hit=16330 read=30512, temp read=48492 written=48577
  ->  WindowAgg  (cost=492852.59..1347770.80 rows=5000137 width=126) (actual time=2327.424..3008.748 rows=30 loops=1)
        Buffers: shared hit=16330 read=30512, temp read=48492 written=48577
        ->  Finalize GroupAggregate  (cost=492852.44..1147765.32 rows=5000137 width=86) (actual time=2243.383..3008.441 rows=30 loops=1)
              Group Key: (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at)), c.name
              Buffers: shared hit=16330 read=30512, temp read=48492 written=48577
              ->  Gather Merge  (cost=492852.44..1031095.46 rows=4166780 width=86) (actual time=2209.323..3008.233 rows=88 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    Buffers: shared hit=16330 read=30512, temp read=48492 written=48577
                    ->  Partial GroupAggregate  (cost=491852.41..549145.64 rows=2083390 width=86) (actual time=1679.363..2290.312 rows=29 loops=3)
                          Group Key: (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at)), c.name
                          Buffers: shared hit=16330 read=30512, temp read=48492 written=48577
                          ->  Sort  (cost=491852.41..497060.89 rows=2083390 width=78) (actual time=1663.815..1973.016 rows=1666667 loops=3)
                                Sort Key: (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at)), c.name
                                Sort Method: external merge  Disk: 64736kB
                                Buffers: shared hit=16330 read=30512, temp read=48492 written=48577
                                Worker 0:  Sort Method: external merge  Disk: 64576kB
                                Worker 1:  Sort Method: external merge  Disk: 64752kB
                                ->  Hash Join  (cost=1.11..88045.41 rows=2083390 width=78) (actual time=140.777..757.207 rows=1666667 loops=3)
                                      Hash Cond: (r.channel_id = c.channel_id)
                                      Buffers: shared hit=16202 read=30512
                                      ->  Parallel Seq Scan on service_request r  (cost=0.00..67522.90 rows=2083390 width=12) (actual time=0.172..140.538 rows=1666667 loops=3)
                                            Buffers: shared hit=16177 read=30512
                                      ->  Hash  (cost=1.05..1.05 rows=5 width=10) (actual time=140.562..140.562 rows=5 loops=3)
                                            Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                            Buffers: shared hit=3
                                            ->  Seq Scan on channel c  (cost=0.00..1.05 rows=5 width=10) (actual time=140.539..140.544 rows=5 loops=3)
                                                  Buffers: shared hit=3
Planning Time: 0.465 ms
JIT:
  Functions: 53
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 4.312 ms (Deform 1.889 ms), Inlining 138.129 ms, Optimization 149.811 ms, Emission 134.145 ms, Total 426.398 ms
Execution Time: 3020.152 ms
```

**OLAP (DuckDB)**

```
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
EXPLAIN ANALYZE -- Q6: How is each quarter's volume split across channels? SELECT     CAST(d.year AS INTEGER) AS year,     CAST(d.quarter AS INTEGER) AS quarter,     c.name AS channel,     count(*) AS requests,     CAST(count(*) AS DOUBLE)         / CAST(sum(count(*)) OVER (PARTITION BY d.year, d.quarter) AS DOUBLE) AS share FROM fact_service_request f JOIN dim_date d ON d.date_key = f.date_key JOIN dim_channel c ON c.channel_key = f.channel_key GROUP BY d.year, d.quarter, c.name ORDER BY year, quarter, c.name; 
┌────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────┐│
││              Total Time: 0.0174s             ││
│└──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
┌───────────────────────────┐
│           QUERY           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      EXPLAIN_ANALYZE      │
│    ────────────────────   │
│                           │
│           0 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_integ│
│   ral_integer(#0, 2024)   │
│__internal_decompress_integ│
│     ral_integer(#1, 1)    │
│__internal_decompress_strin│
│           g(#2)           │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│          ORDER_BY         │
│    ────────────────────   │
│ CAST(d."year" AS INTEGER) │
│             ASC           │
│    CAST(d."quarter" AS    │
│        INTEGER) ASC       │
│        c."name" ASC       │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_integra│
│    l_utinyint(#0, 2024)   │
│__internal_compress_integra│
│     l_utinyint(#1, 1)     │
│__internal_compress_string_│
│        ubigint(#2)        │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│            year           │
│          quarter          │
│          channel          │
│          requests         │
│           share           │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│             #0            │
│             #1            │
│             #2            │
│             #3            │
│             #4            │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│           WINDOW          │
│    ────────────────────   │
│        Projections:       │
│  sum(count_star()) OVER   │
│    (PARTITION BY year,    │
│          quarter)         │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_decompress_integ│
│   ral_smallint(#0, 2024)  │
│             #1            │
│__internal_decompress_strin│
│           g(#2)           │
│             #3            │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│       HASH_GROUP_BY       │
│    ────────────────────   │
│          Groups:          │
│             #0            │
│             #1            │
│             #2            │
│                           │
│        Aggregates:        │
│        count_star()       │
│                           │
│                           │
│                           │
│          30 rows          │
│           0.10s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│            year           │
│          quarter          │
│            name           │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│__internal_compress_integra│
│    l_utinyint(#0, 2024)   │
│             #1            │
│__internal_compress_string_│
│        ubigint(#2)        │
│                           │
│                           │
│                           │
│       5,000,000 rows      │
│           0.01s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        │
│ channel_key = channel_key ├───────────────────────────────────────────┐
│                           │                                           │
│                           │                                           │
│                           │                                           │
│       5,000,000 rows      │                                           │
│           0.01s           │                                           │
└─────────────┬─────────────┘                                           │
┌─────────────┴─────────────┐                             ┌─────────────┴─────────────┐
│         HASH_JOIN         │                             │         TABLE_SCAN        │
│    ────────────────────   │                             │    ────────────────────   │
│      Join Type: INNER     │                             │           Table:          │
│                           │                             │   olap.main.dim_channel   │
│        Conditions:        │                             │                           │
│    date_key = date_key    │                             │   Type: Sequential Scan   │
│                           │                             │                           │
│                           ├──────────────┐              │        Projections:       │
│                           │              │              │        channel_key        │
│                           │              │              │            name           │
│           0.01s           │              │              │                           │
│                           │              │              │                           │
│                           │              │              │                           │
│       5,000,000 rows      │              │              │           5 rows          │
│          (0.01s)          │              │              │           0.00s           │
└─────────────┬─────────────┘              │              └───────────────────────────┘
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         TABLE_SCAN        ││         TABLE_SCAN        │
│    ────────────────────   ││    ────────────────────   │
│           Table:          ││           Table:          │
│         olap.main         ││     olap.main.dim_date    │
│   .fact_service_request   ││                           │
│                           ││   Type: Sequential Scan   │
│   Type: Sequential Scan   ││                           │
│                           ││        Projections:       │
│        Projections:       ││          date_key         │
│          date_key         ││            year           │
│        channel_key        ││          quarter          │
│                           ││                           │
│      Dynamic Filters:     ││                           │
│    optional: date_key>    ││                           │
│  =20240101 AND optional:  ││                           │
│     date_key<=20250610    ││           0.00s           │
│  optional: channel_key>=1 ││                           │
│  AND optional: channel_key││                           │
│            <=5            ││                           │
│                           ││                           │
│                           ││                           │
│                           ││                           │
│       5,000,000 rows      ││          527 rows         │
│           0.00s           ││          (0.00s)          │
└───────────────────────────┘└───────────────────────────┘

```

### t1: Read one request by its identifier, with all its descriptive attributes.

**OLTP (PostgreSQL)**

```
Nested Loop  (cost=1.26..29.02 rows=1 width=139) (actual time=0.088..0.091 rows=1 loops=1)
  Join Filter: (r.status_id = s.status_id)
  Rows Removed by Join Filter: 1
  Buffers: shared hit=17
  ->  Nested Loop  (cost=1.26..27.86 rows=1 width=135) (actual time=0.085..0.087 rows=1 loops=1)
        Join Filter: (r.channel_id = c.channel_id)
        Buffers: shared hit=16
        ->  Nested Loop  (cost=1.26..26.75 rows=1 width=133) (actual time=0.078..0.080 rows=1 loops=1)
              Buffers: shared hit=15
              ->  Nested Loop  (cost=1.13..26.58 rows=1 width=128) (actual time=0.066..0.068 rows=1 loops=1)
                    Buffers: shared hit=13
                    ->  Nested Loop  (cost=0.85..18.27 rows=1 width=109) (actual time=0.052..0.054 rows=1 loops=1)
                          Buffers: shared hit=10
                          ->  Nested Loop  (cost=0.71..18.10 rows=1 width=96) (actual time=0.043..0.044 rows=1 loops=1)
                                Join Filter: (r.agency_id = a.agency_id)
                                Rows Removed by Join Filter: 12
                                Buffers: shared hit=8
                                ->  Nested Loop  (cost=0.71..16.76 rows=1 width=64) (actual time=0.031..0.032 rows=1 loops=1)
                                      Buffers: shared hit=7
                                      ->  Index Scan using service_request_pkey on service_request r  (cost=0.43..8.45 rows=1 width=44) (actual time=0.015..0.016 rows=1 loops=1)
                                            Index Cond: (request_id = 59886871)
                                            Buffers: shared hit=4
                                      ->  Index Scan using complaint_descriptor_pkey on complaint_descriptor d  (cost=0.28..8.29 rows=1 width=28) (actual time=0.013..0.013 rows=1 loops=1)
                                            Index Cond: (descriptor_id = r.descriptor_id)
                                            Buffers: shared hit=3
                                ->  Seq Scan on agency a  (cost=0.00..1.15 rows=15 width=40) (actual time=0.009..0.010 rows=13 loops=1)
                                      Buffers: shared hit=1
                          ->  Index Scan using complaint_type_pkey on complaint_type ct  (cost=0.14..0.18 rows=1 width=21) (actual time=0.009..0.009 rows=1 loops=1)
                                Index Cond: (complaint_type_id = d.complaint_type_id)
                                Buffers: shared hit=2
                    ->  Index Scan using location_pkey on location l  (cost=0.28..8.29 rows=1 width=27) (actual time=0.012..0.012 rows=1 loops=1)
                          Index Cond: (location_id = r.location_id)
                          Buffers: shared hit=3
              ->  Index Scan using borough_pkey on borough b  (cost=0.13..0.16 rows=1 width=13) (actual time=0.012..0.012 rows=1 loops=1)
                    Index Cond: (borough_id = l.borough_id)
                    Buffers: shared hit=2
        ->  Seq Scan on channel c  (cost=0.00..1.05 rows=5 width=10) (actual time=0.006..0.006 rows=1 loops=1)
              Buffers: shared hit=1
  ->  Seq Scan on status s  (cost=0.00..1.07 rows=7 width=12) (actual time=0.002..0.002 rows=2 loops=1)
        Buffers: shared hit=1
Planning:
  Buffers: shared hit=66
Planning Time: 2.094 ms
Execution Time: 0.150 ms
```

**OLAP (DuckDB)**

```
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
EXPLAIN ANALYZE -- T1: read one request by its identifier, with every descriptive attribute. -- 59886871 is replaced by the runner with an identifier taken from a fixed list. SELECT     f.request_id,     f.created_at,     f.closed_at,     a.code AS agency,     a.name AS agency_name,     c.complaint_type,     c.descriptor,     l.borough,     l.zip_code,     l.community_board,     ch.name AS channel,     s.name AS status FROM fact_service_request f JOIN dim_agency a ON a.agency_key = f.agency_key JOIN dim_complaint c ON c.complaint_key = f.complaint_key JOIN dim_location l ON l.location_key = f.location_key JOIN dim_channel ch ON ch.channel_key = f.channel_key JOIN dim_status s ON s.status_key = f.status_key WHERE f.request_id = 59886871; 
┌────────────────────────────────────────────────┐
│┌──────────────────────────────────────────────┐│
││              Total Time: 0.0028s             ││
│└──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
┌───────────────────────────┐
│           QUERY           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      EXPLAIN_ANALYZE      │
│    ────────────────────   │
│                           │
│           0 rows          │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         PROJECTION        │
│    ────────────────────   │
│         request_id        │
│         created_at        │
│         closed_at         │
│           agency          │
│        agency_name        │
│       complaint_type      │
│         descriptor        │
│          borough          │
│          zip_code         │
│      community_board      │
│          channel          │
│           status          │
│                           │
│                           │
│                           │
│           1 row           │
│           0.00s           │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│         HASH_JOIN         │
│    ────────────────────   │
│      Join Type: INNER     │
│                           │
│        Conditions:        │
│  status_key = status_key  ├──────────────┐
│                           │              │
│                           │              │
│                           │              │
│           1 row           │              │
│           0.00s           │              │
└─────────────┬─────────────┘              │
┌─────────────┴─────────────┐┌─────────────┴─────────────┐
│         TABLE_SCAN        ││         HASH_JOIN         │
│    ────────────────────   ││    ────────────────────   │
│           Table:          ││      Join Type: INNER     │
│    olap.main.dim_status   ││                           │
│                           ││        Conditions:        │
│   Type: Sequential Scan   ││ channel_key = channel_key │
│                           ││                           │
│        Projections:       ││                           │
│         status_key        ││                           │
│            name           ││                           ├──────────────┐
│                           ││           0.00s           │              │
│      Dynamic Filters:     ││                           │              │
│        status_key=2       ││                           │              │
│                           ││                           │              │
│                           ││                           │              │
│                           ││                           │              │
│           1 row           ││           1 row           │              │
│           0.00s           ││          (0.00s)          │              │
└───────────────────────────┘└─────────────┬─────────────┘              │
                             ┌─────────────┴─────────────┐┌─────────────┴─────────────┐
                             │         TABLE_SCAN        ││         HASH_JOIN         │
                             │    ────────────────────   ││    ────────────────────   │
                             │           Table:          ││      Join Type: INNER     │
                             │   olap.main.dim_channel   ││                           │
                             │                           ││        Conditions:        │
                             │   Type: Sequential Scan   ││location_key = location_key│
                             │                           ││                           │
                             │        Projections:       ││                           │
                             │        channel_key        ││                           │
                             │            name           ││                           ├──────────────┐
                             │                           ││           0.00s           │              │
                             │      Dynamic Filters:     ││                           │              │
                             │       channel_key=1       ││                           │              │
                             │                           ││                           │              │
                             │                           ││                           │              │
                             │                           ││                           │              │
                             │           1 row           ││           1 row           │              │
                             │           0.00s           ││          (0.00s)          │              │
                             └───────────────────────────┘└─────────────┬─────────────┘              │
                                                          ┌─────────────┴─────────────┐┌─────────────┴─────────────┐
                                                          │         TABLE_SCAN        ││         HASH_JOIN         │
                                                          │    ────────────────────   ││    ────────────────────   │
                                                          │           Table:          ││      Join Type: INNER     │
                                                          │   olap.main.dim_location  ││                           │
                                                          │                           ││        Conditions:        │
                                                          │   Type: Sequential Scan   ││      complaint_key =      │
                                                          │                           ││        complaint_key      │
                                                          │        Projections:       ││                           │
                                                          │        location_key       ││                           │
                                                          │          borough          ││                           │
                                                          │          zip_code         ││                           ├──────────────┐
                                                          │      community_board      ││           0.00s           │              │
                                                          │                           ││                           │              │
                                                          │      Dynamic Filters:     ││                           │              │
                                                          │      location_key=77      ││                           │              │
                                                          │                           ││                           │              │
                                                          │                           ││                           │              │
                                                          │                           ││                           │              │
                                                          │           1 row           ││           1 row           │              │
                                                          │           0.00s           ││          (0.00s)          │              │
                                                          └───────────────────────────┘└─────────────┬─────────────┘              │
                                                                                       ┌─────────────┴─────────────┐┌─────────────┴─────────────┐
                                                                                       │         TABLE_SCAN        ││         HASH_JOIN         │
                                                                                       │    ────────────────────   ││    ────────────────────   │
                                                                                       │           Table:          ││      Join Type: INNER     │
                                                                                       │  olap.main.dim_complaint  ││                           │
                                                                                       │                           ││        Conditions:        │
                                                                                       │   Type: Sequential Scan   ││  agency_key = agency_key  │
                                                                                       │                           ││                           │
                                                                                       │        Projections:       ││                           │
                                                                                       │       complaint_key       ││                           │
                                                                                       │       complaint_type      ││                           ├──────────────┐
                                                                                       │         descriptor        ││           0.00s           │              │
                                                                                       │                           ││                           │              │
                                                                                       │      Dynamic Filters:     ││                           │              │
                                                                                       │     complaint_key=465     ││                           │              │
                                                                                       │                           ││                           │              │
                                                                                       │                           ││                           │              │
                                                                                       │                           ││                           │              │
                                                                                       │           1 row           ││           1 row           │              │
                                                                                       │           0.00s           ││          (0.00s)          │              │
                                                                                       └───────────────────────────┘└─────────────┬─────────────┘              │
                                                                                                                    ┌─────────────┴─────────────┐┌─────────────┴─────────────┐
                                                                                                                    │         TABLE_SCAN        ││         TABLE_SCAN        │
                                                                                                                    │    ────────────────────   ││    ────────────────────   │
                                                                                                                    │           Table:          ││           Table:          │
                                                                                                                    │    olap.main.dim_agency   ││         olap.main         │
                                                                                                                    │                           ││   .fact_service_request   │
                                                                                                                    │   Type: Sequential Scan   ││                           │
                                                                                                                    │                           ││   Type: Sequential Scan   │
                                                                                                                    │        Projections:       ││                           │
                                                                                                                    │         agency_key        ││        Projections:       │
                                                                                                                    │            code           ││         agency_key        │
                                                                                                                    │            name           ││       complaint_key       │
                                                                                                                    │                           ││        location_key       │
                                                                                                                    │      Dynamic Filters:     ││        channel_key        │
                                                                                                                    │       agency_key=13       ││         status_key        │
                                                                                                                    │                           ││         request_id        │
                                                                                                                    │                           ││         created_at        │
                                                                                                                    │                           ││         closed_at         │
                                                                                                                    │                           ││                           │
                                                                                                                    │           0.00s           ││          Filters:         │
                                                                                                                    │                           ││    request_id=59886871    │
                                                                                                                    │                           ││                           │
                                                                                                                    │                           ││                           │
                                                                                                                    │                           ││                           │
                                                                                                                    │           1 row           ││           1 row           │
                                                                                                                    │          (0.00s)          ││           0.00s           │
                                                                                                                    └───────────────────────────┘└───────────────────────────┘

```
