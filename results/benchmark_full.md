# Benchmark results: full profile

5,000,000 requests from NYC 311 Service Requests (erm2-nwe9), created 2024-01-01T00:00:00 to 2025-06-10T09:03:00. Generated 2026-10-13T17:02:26Z.

## Analytical queries

Times in milliseconds: median, with the 95th percentile in parentheses.

| Query | Question | OLTP (PostgreSQL) | OLAP (DuckDB) | Winner |
|---|---|---:|---:|---|
| `q1` | How many requests of each complaint type were created per month in each borough? | 3,488.9 (3,996.9) | 65.0 (99.8) | OLAP, 53.7x faster |
| `q2` | For each ZIP code, which are the 10 most frequent complaint types and how long do they take to resolve on average? | 1,919.7 (2,468.2) | 34.3 (39.4) | OLAP, 55.9x faster |
| `q3` | What share of requests does each agency close within 30 days, by channel? | 724.4 (880.4) | 15.3 (18.3) | OLAP, 47.3x faster |
| `q4` | What is the 90th percentile of resolution time per agency and quarter? | 6,952.4 (9,098.9) | 39.3 (45.0) | OLAP, 176.8x faster |
| `q5` | In Brooklyn, when do noise complaints concentrate, by day of week and hour? | 1,119.5 (1,142.4) | 6.5 (10.8) | OLAP, 173.5x faster |
| `q6` | How is each quarter's volume split across channels? | 2,398.4 (2,803.2) | 28.3 (47.1) | OLAP, 84.8x faster |

## Verdict

**Significance threshold reached.** 6 of 6 analytical queries are at least 3x faster on the OLAP model. Rule: OLAP at least 3x faster on the median in at least two thirds of analytical queries.

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
Sort  (cost=2122481.02..2134981.02 rows=5000000 width=138) (actual time=6338.610..6339.472 rows=13367 loops=1)
  Sort Key: b.name COLLATE "C", (to_char((date_trunc('month'::text, r.created_at)), 'YYYY-MM'::text)), ct.name COLLATE "C"
  Sort Method: quicksort  Memory: 1706kB
  Buffers: shared hit=382 read=46327
  ->  HashAggregate  (cost=672972.98..848363.60 rows=5000000 width=138) (actual time=6307.198..6313.619 rows=13367 loops=1)
        Group Key: b.name, date_trunc('month'::text, r.created_at), ct.name
        Planned Partitions: 128  Batches: 1  Memory Usage: 3089kB
        Buffers: shared hit=382 read=46327
        ->  Hash Join  (cost=73.84..171410.48 rows=5000000 width=42) (actual time=174.596..4963.154 rows=5000000 loops=1)
              Hash Cond: (d.complaint_type_id = ct.complaint_type_id)
              Buffers: shared hit=382 read=46327
              ->  Hash Join  (cost=67.27..145504.89 rows=5000000 width=21) (actual time=0.846..3536.353 rows=5000000 loops=1)
                    Hash Cond: (r.descriptor_id = d.descriptor_id)
                    Buffers: shared hit=380 read=46327
                    ->  Hash Join  (cost=31.41..132297.43 rows=5000000 width=21) (actual time=0.533..2616.461 rows=5000000 loops=1)
                          Hash Cond: (l.borough_id = b.borough_id)
                          Buffers: shared hit=371 read=46327
                          ->  Hash Join  (cost=30.27..109900.47 rows=5000000 width=16) (actual time=0.503..1793.177 rows=5000000 loops=1)
                                Hash Cond: (r.location_id = l.location_id)
                                Buffers: shared hit=370 read=46327
                                ->  Seq Scan on service_request r  (cost=0.00..96689.00 rows=5000000 width=16) (actual time=0.278..803.748 rows=5000000 loops=1)
                                      Buffers: shared hit=362 read=46327
                                ->  Hash  (cost=17.90..17.90 rows=990 width=8) (actual time=0.213..0.219 rows=990 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 47kB
                                      Buffers: shared hit=8
                                      ->  Seq Scan on location l  (cost=0.00..17.90 rows=990 width=8) (actual time=0.021..0.112 rows=990 loops=1)
                                            Buffers: shared hit=8
                          ->  Hash  (cost=1.06..1.06 rows=6 width=13) (actual time=0.025..0.025 rows=6 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                Buffers: shared hit=1
                                ->  Seq Scan on borough b  (cost=0.00..1.06 rows=6 width=13) (actual time=0.021..0.022 rows=6 loops=1)
                                      Buffers: shared hit=1
                    ->  Hash  (cost=20.94..20.94 rows=1194 width=8) (actual time=0.275..0.280 rows=1194 loops=1)
                          Buckets: 2048  Batches: 1  Memory Usage: 63kB
                          Buffers: shared hit=9
                          ->  Seq Scan on complaint_descriptor d  (cost=0.00..20.94 rows=1194 width=8) (actual time=0.056..0.161 rows=1194 loops=1)
                                Buffers: shared hit=9
              ->  Hash  (cost=4.03..4.03 rows=203 width=21) (actual time=173.708..173.709 rows=203 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 19kB
                    Buffers: shared hit=2
                    ->  Seq Scan on complaint_type ct  (cost=0.00..4.03 rows=203 width=21) (actual time=173.610..173.653 rows=203 loops=1)
                          Buffers: shared hit=2
Planning:
  Buffers: shared hit=42
Planning Time: 1.769 ms
JIT:
  Functions: 39
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 2.301 ms (Deform 0.949 ms), Inlining 27.730 ms, Optimization 88.712 ms, Emission 57.771 ms, Total 176.514 ms
Execution Time: 6344.130 ms
```

**OLAP (DuckDB)**

```
analyzed_plan
```

### q2: For each ZIP code, which are the 10 most frequent complaint types and how long do they take to resolve on average?

**OLTP (PostgreSQL)**

```
Sort  (cost=387017.29..387225.36 rows=83230 width=79) (actual time=1789.182..1790.358 rows=2521 loops=1)
  Sort Key: ranked.zip_code COLLATE "C", ranked.rank
  Sort Method: quicksort  Memory: 286kB
  Buffers: shared hit=1545 read=45239
  ->  Subquery Scan on ranked  (cost=347356.12..376515.89 rows=83230 width=79) (actual time=1746.122..1789.756 rows=2521 loops=1)
        Buffers: shared hit=1545 read=45239
        ->  WindowAgg  (cost=347356.12..375683.59 rows=83230 width=79) (actual time=1746.120..1789.501 rows=2521 loops=1)
              Run Condition: (row_number() OVER (?) <= 10)
              Buffers: shared hit=1545 read=45239
              ->  Incremental Sort  (cost=347355.78..374018.99 rows=83230 width=71) (actual time=1746.113..1786.916 rows=24553 loops=1)
                    Sort Key: per_zip.zip_code, per_zip.requests DESC, ((per_zip.complaint_type)::text) COLLATE "C"
                    Presorted Key: per_zip.zip_code
                    Full-sort Groups: 206  Sort Method: quicksort  Average Memory: 30kB  Peak Memory: 30kB
                    Pre-sorted Groups: 269  Sort Method: quicksort  Average Memory: 25kB  Peak Memory: 25kB
                    Buffers: shared hit=1545 read=45239
                    ->  Subquery Scan on per_zip  (cost=347227.05..369353.71 rows=83230 width=71) (actual time=1746.004..1777.351 rows=24553 loops=1)
                          Buffers: shared hit=1545 read=45239
                          ->  Finalize GroupAggregate  (cost=347227.05..369353.71 rows=83230 width=39) (actual time=1746.002..1774.990 rows=24553 loops=1)
                                Group Key: l.zip_code, ct.name
                                Buffers: shared hit=1545 read=45239
                                ->  Gather Merge  (cost=347227.05..366648.74 rows=166460 width=63) (actual time=1745.971..1761.576 rows=63410 loops=1)
                                      Workers Planned: 2
                                      Workers Launched: 2
                                      Buffers: shared hit=1545 read=45239
                                      ->  Sort  (cost=346227.02..346435.10 rows=83230 width=63) (actual time=1728.836..1730.134 rows=21137 loops=3)
                                            Sort Key: l.zip_code, ct.name
                                            Sort Method: quicksort  Memory: 2805kB
                                            Buffers: shared hit=1545 read=45239
                                            Worker 0:  Sort Method: quicksort  Memory: 2831kB
                                            Worker 1:  Sort Method: quicksort  Memory: 2823kB
                                            ->  Partial HashAggregate  (cost=302908.25..336292.63 rows=83230 width=63) (actual time=1698.120..1700.432 rows=21137 loops=3)
                                                  Group Key: l.zip_code, ct.name
                                                  Planned Partitions: 4  Batches: 1  Memory Usage: 4625kB
                                                  Buffers: shared hit=1529 read=45239
                                                  Worker 0:  Batches: 1  Memory Usage: 4625kB
                                                  Worker 1:  Batches: 1  Memory Usage: 4625kB
                                                  ->  Hash Join  (cost=72.71..84158.28 rows=2083333 width=39) (actual time=12.836..959.006 rows=1666667 loops=3)
                                                        Hash Cond: (d.complaint_type_id = ct.complaint_type_id)
                                                        Buffers: shared hit=1529 read=45239
                                                        ->  Hash Join  (cost=66.14..78568.79 rows=2083333 width=26) (actual time=0.588..695.992 rows=1666667 loops=3)
                                                              Hash Cond: (r.descriptor_id = d.descriptor_id)
                                                              Buffers: shared hit=1501 read=45239
                                                              ->  Hash Join  (cost=30.27..73044.76 rows=2083333 width=26) (actual time=0.301..425.658 rows=1666667 loops=3)
                                                                    Hash Cond: (r.location_id = l.location_id)
                                                                    Buffers: shared hit=1474 read=45239
                                                                    ->  Parallel Seq Scan on service_request r  (cost=0.00..67522.33 rows=2083333 width=24) (actual time=0.064..128.419 rows=1666667 loops=3)
                                                                          Buffers: shared hit=1450 read=45239
                                                                    ->  Hash  (cost=17.90..17.90 rows=990 width=10) (actual time=0.227..0.228 rows=990 loops=3)
                                                                          Buckets: 1024  Batches: 1  Memory Usage: 51kB
                                                                          Buffers: shared hit=24
                                                                          ->  Seq Scan on location l  (cost=0.00..17.90 rows=990 width=10) (actual time=0.014..0.107 rows=990 loops=3)
                                                                                Buffers: shared hit=24
                                                              ->  Hash  (cost=20.94..20.94 rows=1194 width=8) (actual time=0.276..0.277 rows=1194 loops=3)
                                                                    Buckets: 2048  Batches: 1  Memory Usage: 63kB
                                                                    Buffers: shared hit=27
                                                                    ->  Seq Scan on complaint_descriptor d  (cost=0.00..20.94 rows=1194 width=8) (actual time=0.026..0.145 rows=1194 loops=3)
                                                                          Buffers: shared hit=27
                                                        ->  Hash  (cost=4.03..4.03 rows=203 width=21) (actual time=12.223..12.224 rows=203 loops=3)
                                                              Buckets: 1024  Batches: 1  Memory Usage: 19kB
                                                              Buffers: shared hit=6
                                                              ->  Seq Scan on complaint_type ct  (cost=0.00..4.03 rows=203 width=21) (actual time=12.166..12.187 rows=203 loops=3)
                                                                    Buffers: shared hit=6
Planning:
  Buffers: shared hit=38
Planning Time: 0.703 ms
JIT:
  Functions: 103
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 2.919 ms (Deform 1.043 ms), Inlining 0.000 ms, Optimization 1.311 ms, Emission 35.322 ms, Total 39.552 ms
Execution Time: 1791.687 ms
```

**OLAP (DuckDB)**

```
analyzed_plan
```

### q3: What share of requests does each agency close within 30 days, by channel?

**OLTP (PostgreSQL)**

```
Sort  (cost=122126.93..122127.12 rows=75 width=98) (actual time=1072.637..1076.583 rows=50 loops=1)
  Sort Key: a.code COLLATE "C", c.name COLLATE "C"
  Sort Method: quicksort  Memory: 28kB
  Buffers: shared hit=2646 read=44087
  ->  Finalize GroupAggregate  (cost=122104.28..122124.59 rows=75 width=98) (actual time=1072.427..1076.500 rows=50 loops=1)
        Group Key: a.code, c.name
        Buffers: shared hit=2646 read=44087
        ->  Gather Merge  (cost=122104.28..122121.78 rows=150 width=26) (actual time=1072.386..1076.382 rows=142 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=2646 read=44087
              ->  Sort  (cost=121104.26..121104.44 rows=75 width=26) (actual time=1063.857..1063.865 rows=47 loops=3)
                    Sort Key: a.code, c.name
                    Sort Method: quicksort  Memory: 27kB
                    Buffers: shared hit=2646 read=44087
                    Worker 0:  Sort Method: quicksort  Memory: 27kB
                    Worker 1:  Sort Method: quicksort  Memory: 27kB
                    ->  Partial HashAggregate  (cost=121101.17..121101.92 rows=75 width=26) (actual time=1063.797..1063.807 rows=47 loops=3)
                          Group Key: a.code, c.name
                          Batches: 1  Memory Usage: 24kB
                          Buffers: shared hit=2630 read=44087
                          Worker 0:  Batches: 1  Memory Usage: 32kB
                          Worker 1:  Batches: 1  Memory Usage: 32kB
                          ->  Hash Join  (cost=2.45..84642.84 rows=2083333 width=26) (actual time=7.821..666.354 rows=1666667 loops=3)
                                Hash Cond: (r.channel_id = c.channel_id)
                                Buffers: shared hit=2630 read=44087
                                ->  Hash Join  (cost=1.34..74537.56 rows=2083333 width=24) (actual time=0.077..407.009 rows=1666667 loops=3)
                                      Hash Cond: (r.agency_id = a.agency_id)
                                      Buffers: shared hit=2605 read=44087
                                      ->  Parallel Seq Scan on service_request r  (cost=0.00..67522.33 rows=2083333 width=24) (actual time=0.050..115.505 rows=1666667 loops=3)
                                            Buffers: shared hit=2602 read=44087
                                      ->  Hash  (cost=1.15..1.15 rows=15 width=8) (actual time=0.017..0.017 rows=15 loops=3)
                                            Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                            Buffers: shared hit=3
                                            ->  Seq Scan on agency a  (cost=0.00..1.15 rows=15 width=8) (actual time=0.012..0.014 rows=15 loops=3)
                                                  Buffers: shared hit=3
                                ->  Hash  (cost=1.05..1.05 rows=5 width=10) (actual time=7.728..7.729 rows=5 loops=3)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      Buffers: shared hit=3
                                      ->  Seq Scan on channel c  (cost=0.00..1.05 rows=5 width=10) (actual time=7.714..7.717 rows=5 loops=3)
                                            Buffers: shared hit=3
Planning:
  Buffers: shared hit=24
Planning Time: 0.397 ms
JIT:
  Functions: 72
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 1.877 ms (Deform 0.752 ms), Inlining 0.000 ms, Optimization 0.887 ms, Emission 22.662 ms, Total 25.426 ms
Execution Time: 1077.470 ms
```

**OLAP (DuckDB)**

```
analyzed_plan
```

### q4: What is the 90th percentile of resolution time per agency and quarter?

**OLTP (PostgreSQL)**

```
Sort  (cost=879544.49..883711.16 rows=1666667 width=124) (actual time=5289.589..5297.486 rows=84 loops=1)
  Sort Key: a.code COLLATE "C", (((EXTRACT(year FROM r.created_at)))::integer), (((EXTRACT(quarter FROM r.created_at)))::integer)
  Sort Method: quicksort  Memory: 30kB
  Buffers: shared hit=3945 read=42935, temp read=54887 written=54997
  ->  GroupAggregate  (cost=213387.48..490831.67 rows=1666667 width=124) (actual time=1558.100..5297.246 rows=84 loops=1)
        Group Key: a.code, (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at))
        Buffers: shared hit=3945 read=42935, temp read=54887 written=54997
        ->  Gather Merge  (cost=213387.48..407498.32 rows=1666667 width=84) (actual time=1555.200..2873.768 rows=4914706 loops=1)
              Workers Planned: 2
              Workers Launched: 2
              Buffers: shared hit=3945 read=42935, temp read=50530 written=50617
              ->  Sort  (cost=212387.46..214123.57 rows=694445 width=84) (actual time=1540.671..1756.381 rows=1638235 loops=3)
                    Sort Key: a.code, (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at))
                    Sort Method: external merge  Disk: 68072kB
                    Buffers: shared hit=3945 read=42935, temp read=50530 written=50617
                    Worker 0:  Sort Method: external merge  Disk: 67216kB
                    Worker 1:  Sort Method: external merge  Disk: 66960kB
                    ->  Hash Join  (cost=1.34..78542.19 rows=694445 width=84) (actual time=85.862..700.478 rows=1638235 loops=3)
                          Hash Cond: (r.agency_id = a.agency_id)
                          Buffers: shared hit=3817 read=42935
                          ->  Parallel Seq Scan on service_request r  (cost=0.00..72730.67 rows=694445 width=20) (actual time=85.764..217.339 rows=1638235 loops=3)
                                Filter: (closed_at >= created_at)
                                Rows Removed by Filter: 28431
                                Buffers: shared hit=3754 read=42935
                          ->  Hash  (cost=1.15..1.15 rows=15 width=8) (actual time=0.035..0.035 rows=15 loops=3)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                Buffers: shared hit=3
                                ->  Seq Scan on agency a  (cost=0.00..1.15 rows=15 width=8) (actual time=0.029..0.030 rows=15 loops=3)
                                      Buffers: shared hit=3
Planning:
  Buffers: shared hit=20
Planning Time: 0.630 ms
JIT:
  Functions: 43
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 3.142 ms (Deform 0.930 ms), Inlining 104.695 ms, Optimization 80.848 ms, Emission 71.677 ms, Total 260.362 ms
Execution Time: 5305.817 ms
```

**OLAP (DuckDB)**

```
analyzed_plan
```

### q5: In Brooklyn, when do noise complaints concentrate, by day of week and hour?

**OLTP (PostgreSQL)**

```
Sort  (cost=22697.47..22779.57 rows=32841 width=80) (actual time=1649.540..1649.552 rows=168 loops=1)
  Sort Key: (((EXTRACT(isodow FROM r.created_at)))::integer), (((EXTRACT(hour FROM r.created_at)))::integer)
  Sort Method: quicksort  Memory: 32kB
  Buffers: shared hit=48441 read=277636
  ->  HashAggregate  (cost=19412.84..20233.87 rows=32841 width=80) (actual time=1649.303..1649.499 rows=168 loops=1)
        Group Key: EXTRACT(isodow FROM r.created_at), EXTRACT(hour FROM r.created_at)
        Batches: 1  Memory Usage: 1569kB
        Buffers: shared hit=48441 read=277636
        ->  Hash Join  (cost=17.69..19166.54 rows=32841 width=72) (actual time=0.377..1577.512 rows=272132 loops=1)
              Hash Cond: (r.location_id = l.location_id)
              Buffers: shared hit=48441 read=277636
              ->  Nested Loop  (cost=0.86..17918.18 rows=197044 width=12) (actual time=0.299..1409.146 rows=1093077 loops=1)
                    Buffers: shared hit=48439 read=277633
                    ->  Nested Loop  (cost=0.43..120.30 rows=47 width=4) (actual time=0.283..0.776 rows=53 loops=1)
                          Buffers: shared hit=404 read=17
                          ->  Index Scan using complaint_descriptor_pkey on complaint_descriptor d  (cost=0.28..54.19 rows=1194 width=8) (actual time=0.006..0.215 rows=1194 loops=1)
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
                    ->  Index Scan using service_request_descriptor_idx on service_request r  (cost=0.43..303.15 rows=7553 width=16) (actual time=0.010..24.199 rows=20624 loops=53)
                          Index Cond: (descriptor_id = d.descriptor_id)
                          Buffers: shared hit=48035 read=277616
              ->  Hash  (cost=14.76..14.76 rows=165 width=4) (actual time=0.067..0.068 rows=175 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 15kB
                    Buffers: shared hit=2 read=3
                    ->  Nested Loop  (cost=0.15..14.76 rows=165 width=4) (actual time=0.010..0.051 rows=175 loops=1)
                          Buffers: shared hit=2 read=3
                          ->  Seq Scan on borough b  (cost=0.00..1.07 rows=1 width=4) (actual time=0.004..0.004 rows=1 loops=1)
                                Filter: (name = 'BROOKLYN'::text)
                                Rows Removed by Filter: 5
                                Buffers: shared hit=1
                          ->  Index Scan using location_borough_idx on location l  (cost=0.15..12.04 rows=165 width=8) (actual time=0.006..0.031 rows=175 loops=1)
                                Index Cond: (borough_id = b.borough_id)
                                Buffers: shared hit=1 read=3
Planning:
  Buffers: shared hit=18 read=24
Planning Time: 0.469 ms
Execution Time: 1649.626 ms
```

**OLAP (DuckDB)**

```
analyzed_plan
```

### q6: How is each quarter's volume split across channels?

**OLTP (PostgreSQL)**

```
Sort  (cost=2553488.29..2565988.29 rows=5000000 width=126) (actual time=3732.583..3732.757 rows=30 loops=1)
  Sort Key: (((EXTRACT(year FROM r.created_at)))::integer), (((EXTRACT(quarter FROM r.created_at)))::integer), c.name COLLATE "C"
  Sort Method: quicksort  Memory: 27kB
  Buffers: shared hit=16310 read=30532, temp read=48487 written=48573
  ->  WindowAgg  (cost=492838.06..1347732.87 rows=5000000 width=126) (actual time=3355.815..3732.709 rows=30 loops=1)
        Buffers: shared hit=16310 read=30532, temp read=48487 written=48573
        ->  Finalize GroupAggregate  (cost=492837.92..1147732.87 rows=5000000 width=86) (actual time=3269.988..3732.365 rows=30 loops=1)
              Group Key: (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at)), c.name
              Buffers: shared hit=16310 read=30532, temp read=48487 written=48573
              ->  Gather Merge  (cost=492837.92..1031066.21 rows=4166666 width=86) (actual time=3228.203..3732.163 rows=86 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    Buffers: shared hit=16310 read=30532, temp read=48487 written=48573
                    ->  Partial GroupAggregate  (cost=491837.89..549129.55 rows=2083333 width=86) (actual time=2577.131..3110.540 rows=29 loops=3)
                          Group Key: (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at)), c.name
                          Buffers: shared hit=16310 read=30532, temp read=48487 written=48573
                          ->  Sort  (cost=491837.89..497046.22 rows=2083333 width=78) (actual time=2558.751..2814.618 rows=1666667 loops=3)
                                Sort Key: (EXTRACT(year FROM r.created_at)), (EXTRACT(quarter FROM r.created_at)), c.name
                                Sort Method: external merge  Disk: 61416kB
                                Buffers: shared hit=16310 read=30532, temp read=48487 written=48573
                                Worker 0:  Sort Method: external merge  Disk: 69512kB
                                Worker 1:  Sort Method: external merge  Disk: 63088kB
                                ->  Hash Join  (cost=1.11..88044.28 rows=2083333 width=78) (actual time=248.544..1302.429 rows=1666667 loops=3)
                                      Hash Cond: (r.channel_id = c.channel_id)
                                      Buffers: shared hit=16182 read=30532
                                      ->  Parallel Seq Scan on service_request r  (cost=0.00..67522.33 rows=2083333 width=12) (actual time=0.050..305.861 rows=1666667 loops=3)
                                            Buffers: shared hit=16157 read=30532
                                      ->  Hash  (cost=1.05..1.05 rows=5 width=10) (actual time=248.420..248.421 rows=5 loops=3)
                                            Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                            Buffers: shared hit=3
                                            ->  Seq Scan on channel c  (cost=0.00..1.05 rows=5 width=10) (actual time=248.361..248.377 rows=5 loops=3)
                                                  Buffers: shared hit=3
Planning:
  Buffers: shared hit=3 read=1
Planning Time: 3.488 ms
JIT:
  Functions: 53
  Options: Inlining true, Optimization true, Expressions true, Deforming true
  Timing: Generation 4.156 ms (Deform 1.913 ms), Inlining 214.373 ms, Optimization 291.545 ms, Emission 246.454 ms, Total 756.529 ms
Execution Time: 3741.532 ms
```

**OLAP (DuckDB)**

```
analyzed_plan
```
