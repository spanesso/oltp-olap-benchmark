"""Measure every benchmark query on both models.

Timing is client-side wall-clock around execute plus full fetch of the result, which is what
an application would observe and is measured identically for both engines.
"""

from __future__ import annotations

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
    oltp_sql = query.sql("oltp")
    olap_sql = query.sql("olap")
    oltp_rows = postgres.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {oltp_sql}").fetchall()
    oltp_plan = "\n".join(row[0] for row in oltp_rows)
    olap_rows = duck.execute(f"EXPLAIN ANALYZE {olap_sql}").fetchall()
    # DuckDB EXPLAIN ANALYZE returns (key, value) rows; row[1] is the plan text.
    olap_plan = "\n".join(row[1] for row in olap_rows)
    return oltp_plan, olap_plan


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
