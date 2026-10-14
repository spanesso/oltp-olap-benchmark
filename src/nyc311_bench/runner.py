"""Measure every benchmark query on both models.

Timing is client-side wall-clock around execute plus full fetch of the result, which is what
an application would observe and is measured identically for both engines.
"""

from __future__ import annotations

import itertools
import math
import os
import platform
import statistics
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from nyc311_bench.queries import Query

MIN_WARMUP_RUNS = 1
MIN_MEASURED_RUNS = 10
DEFAULT_WARMUP_RUNS = 1
DEFAULT_MEASURED_RUNS = 10

POSTGRES_SETTINGS = (
    "max_parallel_workers_per_gather",
    "max_parallel_workers",
    "shared_buffers",
    "work_mem",
    "jit",
)
DUCKDB_SETTINGS = ("threads", "memory_limit")

Reporter = Callable[[str], None]


class ParityError(Exception):
    """The two models do not hold the same data, so measuring them would be meaningless."""


@dataclass(frozen=True)
class Timing:
    runs_ms: tuple[float, ...]
    median_ms: float
    p95_ms: float
    min_ms: float
    max_ms: float


@dataclass(frozen=True)
class QueryResult:
    query: Query
    result_rows: int
    oltp: Timing
    olap: Timing
    oltp_plan: str = ""
    olap_plan: str = ""

    @property
    def speedup(self) -> float:
        """How many times faster the analytical model is on the median (above 1: OLAP wins)."""
        return self.oltp.median_ms / self.olap.median_ms


def percentile(values: Sequence[float], percent: float) -> float:
    """Percentile with linear interpolation between the two nearest ranks."""
    if not values:
        raise ValueError("percentile() needs at least one value")
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize(runs_ms: Sequence[float]) -> Timing:
    return Timing(
        runs_ms=tuple(runs_ms),
        median_ms=statistics.median(runs_ms),
        p95_ms=percentile(runs_ms, 95),
        min_ms=min(runs_ms),
        max_ms=max(runs_ms),
    )


def validate_runs(warmup: int, repetitions: int) -> None:
    if warmup < MIN_WARMUP_RUNS:
        raise ValueError(f"at least {MIN_WARMUP_RUNS} warm-up run is required, got {warmup}")
    if repetitions < MIN_MEASURED_RUNS:
        raise ValueError(
            f"at least {MIN_MEASURED_RUNS} measured repetitions are required, got {repetitions}"
        )


def time_query(
    run: Callable[[], Sequence[Any]],
    warmup: int,
    repetitions: int,
    clock: Callable[[], float] = time.perf_counter,
) -> tuple[Timing, int]:
    """Run `run` warm-up times unmeasured, then `repetitions` times measured."""
    validate_runs(warmup, repetitions)
    for _ in range(warmup):
        run()
    runs_ms = []
    rows = 0
    for _ in range(repetitions):
        started = clock()
        rows = len(run())
        runs_ms.append((clock() - started) * 1000.0)
    return summarize(runs_ms), rows


def check_parity(postgres, duck, expected_rows: int | None = None) -> int:
    """Return the number of requests both models hold, or raise ParityError (FR-018)."""
    try:
        oltp_rows = postgres.execute("SELECT count(*) FROM oltp.service_request").fetchone()[0]
    except Exception as error:
        raise ParityError(f"the OLTP model is not built ({type(error).__name__})") from None
    try:
        olap_rows = duck.execute("SELECT count(*) FROM fact_service_request").fetchone()[0]
    except Exception as error:
        raise ParityError(f"the OLAP model is not built ({type(error).__name__})") from None

    if oltp_rows == 0 or olap_rows == 0:
        raise ParityError(f"a model is empty (OLTP {oltp_rows:,} rows, OLAP {olap_rows:,} rows)")
    if oltp_rows != olap_rows:
        raise ParityError(
            f"the models hold different data (OLTP {oltp_rows:,} rows, OLAP {olap_rows:,} rows)"
        )
    if expected_rows is not None and oltp_rows != expected_rows:
        raise ParityError(
            f"the models hold {oltp_rows:,} requests but the profile expects {expected_rows:,}"
        )
    return oltp_rows


def explain_query(postgres, duck, query: Query) -> tuple[str, str]:
    """Capture EXPLAIN ANALYZE output for a query on both models."""
    return explain_sql(postgres, duck, query.sql("oltp"), query.sql("olap"))


def explain_postgres(postgres, sql: str) -> str:
    rows = postgres.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {sql}").fetchall()
    return "\n".join(row[0] for row in rows)


def explain_duckdb(duck, sql: str) -> str:
    rows = duck.execute(f"EXPLAIN ANALYZE {sql}").fetchall()
    # DuckDB EXPLAIN ANALYZE returns (key, value) rows; row[1] is the plan text.
    return "\n".join(row[1] for row in rows)


def explain_sql(postgres, duck, oltp_sql: str, olap_sql: str) -> tuple[str, str]:
    """Capture EXPLAIN ANALYZE output for one statement per model."""
    return explain_postgres(postgres, oltp_sql), explain_duckdb(duck, olap_sql)


def run_queries(
    postgres,
    duck,
    queries: Sequence[Query],
    *,
    warmup: int = DEFAULT_WARMUP_RUNS,
    repetitions: int = DEFAULT_MEASURED_RUNS,
    report: Reporter = print,
) -> list[QueryResult]:
    """Measure each query: all runs on one model, then all runs on the other."""
    validate_runs(warmup, repetitions)
    results = []
    for query in queries:
        oltp_sql = query.sql("oltp")
        olap_sql = query.sql("olap")
        oltp, oltp_rows = time_query(
            lambda sql=oltp_sql: postgres.execute(sql).fetchall(), warmup, repetitions
        )
        olap, olap_rows = time_query(
            lambda sql=olap_sql: duck.execute(sql).fetchall(), warmup, repetitions
        )
        if oltp_rows != olap_rows:
            raise ParityError(
                f"query {query.id} returns {oltp_rows:,} rows on OLTP and {olap_rows:,} on OLAP"
            )
        oltp_plan, olap_plan = explain_query(postgres, duck, query)
        result = QueryResult(
            query=query,
            result_rows=oltp_rows,
            oltp=oltp,
            olap=olap,
            oltp_plan=oltp_plan,
            olap_plan=olap_plan,
        )
        results.append(result)
        report(
            f"  {query.id}: OLTP {oltp.median_ms:,.1f} ms, OLAP {olap.median_ms:,.1f} ms, "
            f"speedup {result.speedup:,.1f}x"
        )
    return results


TRANSACTIONAL_IDENTIFIERS = 20  # default list size; a run walks as many as it makes runs


def fill(sql: str, values: dict[str, int]) -> str:
    """Replace `@name@` tokens with integers. Only integers are accepted, so nothing a
    person typed can reach the statement."""
    for name, value in values.items():
        sql = sql.replace(f"@{name}@", str(int(value)))
    return sql


def pick_identifiers(postgres, count: int = TRANSACTIONAL_IDENTIFIERS) -> list[int]:
    """`count` existing request identifiers, evenly spread over the key order.

    The identifiers are the ones at ranks 1, 1 + total/count, 1 + 2 total/count ... so the
    list is fixed for a given data set and covers the whole range, even for tiny tables.
    """
    total = postgres.execute("SELECT count(*) FROM oltp.service_request").fetchone()[0]
    if total == 0:
        raise ParityError("the OLTP model has no requests to look up")
    ranks = sorted({(index * total) // count + 1 for index in range(count)})
    rows = postgres.execute(
        "SELECT request_id FROM ("
        "  SELECT request_id, row_number() OVER (ORDER BY request_id) AS n"
        "  FROM oltp.service_request) AS numbered "
        "WHERE n = ANY(%s) ORDER BY request_id",
        (ranks,),
    ).fetchall()
    return [row[0] for row in rows]


def _insert_values(postgres) -> dict[str, int]:
    """A new identifier and the keys of an existing request, for the T2 insert."""
    top, agency, descriptor, location, channel, status = postgres.execute(
        "SELECT (SELECT max(request_id) FROM oltp.service_request) + 1, "
        "agency_id, descriptor_id, location_id, channel_id, status_id "
        "FROM oltp.service_request ORDER BY request_id LIMIT 1"
    ).fetchone()
    return {
        "request_id": top,
        "agency": agency,
        "descriptor": descriptor,
        "location": location,
        "channel": channel,
        "status": status,
    }


def _in_rolled_back_transaction(connection, begin: str, sql: str) -> list:
    connection.execute(begin)
    try:
        connection.execute(sql)
    finally:
        connection.execute("ROLLBACK")
    return []


def _measure_lookup(
    postgres, duck, oltp_template, olap_template, identifiers, warmup, repetitions
) -> tuple[Timing, int, Timing, int]:
    """T1: each model walks the same identifier list, one identifier per run."""

    def timed(execute, template):
        cycle = itertools.count()

        def run():
            request_id = identifiers[next(cycle) % len(identifiers)]
            return execute(fill(template, {"request_id": request_id})).fetchall()

        return time_query(run, warmup, repetitions)

    oltp, oltp_rows = timed(postgres.execute, oltp_template)
    olap, olap_rows = timed(duck.execute, olap_template)
    return oltp, oltp_rows, olap, olap_rows


def _measure_insert(
    postgres, duck, oltp_insert, olap_insert, warmup, repetitions
) -> tuple[Timing, int, Timing, int]:
    """T2: begin, insert one request, roll back; the whole round trip is timed."""
    oltp, oltp_rows = time_query(
        lambda: _in_rolled_back_transaction(postgres, "BEGIN", oltp_insert), warmup, repetitions
    )
    olap, olap_rows = time_query(
        lambda: _in_rolled_back_transaction(duck, "BEGIN TRANSACTION", olap_insert),
        warmup,
        repetitions,
    )
    return oltp, oltp_rows, olap, olap_rows


def run_transactional(
    postgres,
    duck,
    queries: Sequence[Query],
    *,
    warmup: int = DEFAULT_WARMUP_RUNS,
    repetitions: int = DEFAULT_MEASURED_RUNS,
    report: Reporter = print,
) -> list[QueryResult]:
    """Measure the transactional operations (User Story 4).

    T1 walks a fixed, evenly spread list of identifiers, one per run, the same sequence on
    both models. T2 inserts one request inside a transaction that is rolled back, so it
    measures the work of the insert (constraint checks, index or column maintenance) but not
    the commit itself; afterwards both models must hold the rows they held before.
    """
    validate_runs(warmup, repetitions)
    rows_before = check_parity(postgres, duck)
    identifiers = pick_identifiers(postgres, warmup + repetitions)
    insert_values = _insert_values(postgres)
    results = []
    for query in queries:
        oltp_template = query.sql("oltp")
        olap_template = query.sql("olap")
        if query.id.startswith("t1"):
            oltp, oltp_rows, olap, olap_rows = _measure_lookup(
                postgres, duck, oltp_template, olap_template, identifiers, warmup, repetitions
            )
            first = {"request_id": identifiers[0]}
            oltp_plan, olap_plan = explain_sql(
                postgres, duck, fill(oltp_template, first), fill(olap_template, first)
            )
        else:
            oltp, oltp_rows, olap, olap_rows = _measure_insert(
                postgres,
                duck,
                fill(oltp_template, insert_values),
                fill(olap_template, insert_values),
                warmup,
                repetitions,
            )
            oltp_plan = olap_plan = ""
        if oltp_rows != olap_rows:
            raise ParityError(
                f"operation {query.id} returns {oltp_rows} rows on OLTP and {olap_rows} on OLAP"
            )
        result = QueryResult(
            query=query,
            result_rows=oltp_rows,
            oltp=oltp,
            olap=olap,
            oltp_plan=oltp_plan,
            olap_plan=olap_plan,
        )
        results.append(result)
        report(
            f"  {query.id}: OLTP {oltp.median_ms:,.2f} ms, OLAP {olap.median_ms:,.2f} ms, "
            f"speedup {result.speedup:,.2f}x"
        )
    rows_after = check_parity(postgres, duck)
    if rows_after != rows_before:
        raise ParityError(
            f"the transactional operations changed the data ({rows_before:,} rows before, "
            f"{rows_after:,} after)"
        )
    return results


def dataset_info(postgres) -> dict[str, Any]:
    rows, first, last = postgres.execute(
        "SELECT count(*), min(created_at), max(created_at) FROM oltp.service_request"
    ).fetchone()
    return {
        "rows": rows,
        "first_created_at": first.isoformat() if first else None,
        "last_created_at": last.isoformat() if last else None,
    }


def _memory_gb() -> float | None:
    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError, AttributeError):
        return None
    return round(total / 1024**3, 1)


def environment_info(postgres, duck) -> dict[str, Any]:
    """Machine, versions and the engine settings that influence the timings."""
    import duckdb

    return {
        "os": platform.platform(),
        "cpu": platform.processor() or platform.machine(),
        "cores": os.cpu_count(),
        "memory_gb": _memory_gb(),
        "python": platform.python_version(),
        "postgresql": postgres.execute("SHOW server_version").fetchone()[0],
        "postgresql_runtime": "docker container, reached over local TCP",
        "postgresql_settings": {
            name: postgres.execute(f"SHOW {name}").fetchone()[0] for name in POSTGRES_SETTINGS
        },
        "duckdb": duckdb.__version__,
        "duckdb_runtime": "embedded in the benchmark process",
        "duckdb_settings": {
            name: str(duck.execute(f"SELECT current_setting('{name}')").fetchone()[0])
            for name in DUCKDB_SETTINGS
        },
    }
