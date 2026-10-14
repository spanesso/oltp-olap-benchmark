"""Repeated measurements over a 2x2 grid of schema and engine.

Two questions the official run cannot answer on its own:

1. How much of the speedup comes from the schema (normalized vs star) and how much from the
   engine (PostgreSQL row store vs DuckDB column store)? Every combination is measured.
2. How stable are the numbers? The whole grid is measured several times, and the spread
   between repetitions is reported next to the medians.

The official results in `results/benchmark_<profile>.json` are never touched.
"""

from __future__ import annotations

import json
import math
import statistics
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from nyc311_bench.db import read_sql
from nyc311_bench.queries import Query
from nyc311_bench.runner import (
    DEFAULT_MEASURED_RUNS,
    DEFAULT_WARMUP_RUNS,
    Reporter,
    Timing,
    explain_duckdb,
    explain_postgres,
    time_query,
    validate_runs,
)

SCHEMA_VERSION = 1
MIN_REPEATS = 2
RELATIVE_TOLERANCE = 1e-9
REPEATABILITY_LIMIT_PERCENT = 20.0
MIN_MEASURABLE_MS = 1e-6


@dataclass(frozen=True)
class Cell:
    """One combination of schema and engine, with the directory holding its query files."""

    key: str
    label: str
    engine: str
    schema: str
    sql_dir: str

    def sql(self, query: Query) -> str:
        return read_sql(f"{self.sql_dir}/{query.id}.sql")


NORMALIZED_POSTGRES = Cell(
    "normalized_postgres", "Normalized on PostgreSQL", "postgres", "normalized", "oltp"
)
STAR_POSTGRES = Cell("star_postgres", "Star on PostgreSQL", "postgres", "star", "controls/star_pg")
NORMALIZED_DUCKDB = Cell(
    "normalized_duckdb", "Normalized on DuckDB", "duckdb", "normalized", "controls/3nf_duckdb"
)
STAR_DUCKDB = Cell("star_duckdb", "Star on DuckDB", "duckdb", "star", "olap")

CELLS = (NORMALIZED_POSTGRES, STAR_POSTGRES, NORMALIZED_DUCKDB, STAR_DUCKDB)


class EquivalenceError(Exception):
    """Two cells returned different results for the same question."""


def values_match(left: Any, right: Any) -> bool:
    """Exact match for text and integers, relative tolerance for floating point."""
    if left is None or right is None:
        return left is None and right is None
    numbers = (int, float, Decimal)
    if isinstance(left, numbers) and isinstance(right, numbers):
        if isinstance(left, float | Decimal) or isinstance(right, float | Decimal):
            return math.isclose(
                float(left), float(right), rel_tol=RELATIVE_TOLERANCE, abs_tol=1e-12
            )
        return left == right
    return left == right


def check_equivalent(
    query_id: str, reference_label: str, reference: Sequence[Sequence], label: str, rows
) -> None:
    """Raise EquivalenceError naming the first row and column that differ."""
    if len(reference) != len(rows):
        raise EquivalenceError(
            f"{query_id}: {reference_label} returns {len(reference)} rows, "
            f"{label} returns {len(rows)}"
        )
    for index, (expected, actual) in enumerate(zip(reference, rows, strict=True)):
        if len(expected) != len(actual) or not all(
            values_match(a, b) for a, b in zip(expected, actual, strict=True)
        ):
            raise EquivalenceError(
                f"{query_id}: row {index} differs between {reference_label} and {label}: "
                f"{tuple(expected)!r} vs {tuple(actual)!r}"
            )


def spread(medians_ms: Sequence[float]) -> dict[str, Any]:
    """Summarize the medians of one cell and query across repetitions of the whole grid."""
    mean = statistics.fmean(medians_ms)
    deviation = statistics.stdev(medians_ms) if len(medians_ms) > 1 else 0.0
    return {
        "medians_ms": [round(value, 3) for value in medians_ms],
        "median_ms": round(statistics.median(medians_ms), 3),
        "min_ms": round(min(medians_ms), 3),
        "max_ms": round(max(medians_ms), 3),
        "cv_percent": round(deviation / mean * 100.0, 1) if mean else 0.0,
        "range_percent": round(
            (max(medians_ms) - min(medians_ms)) / statistics.median(medians_ms) * 100.0, 1
        ),
    }


def repeatability(queries: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """How many query-and-model series stayed within SC-006 across repetitions.

    SC-006: medians of consecutive runs differ by less than 20%. The range of each series
    (maximum minus minimum, over the median) is the strictest reading of "differ".
    """
    series = [
        (query["id"], key, summary["range_percent"])
        for query in queries
        for key, summary in query["cells"].items()
    ]
    within = [item for item in series if item[2] < REPEATABILITY_LIMIT_PERCENT]
    return {
        "limit_percent": REPEATABILITY_LIMIT_PERCENT,
        "series": len(series),
        "within_limit": len(within),
        "worst": max(series, key=lambda item: item[2])[2] if series else 0.0,
    }


def ratio_summary(numerators: Sequence[float], denominators: Sequence[float]) -> dict[str, Any]:
    """Per-repetition ratio of two series, with its median, minimum and maximum."""
    # A median below the timer resolution would read as zero; never divide by it.
    ratios = [
        top / max(bottom, MIN_MEASURABLE_MS)
        for top, bottom in zip(numerators, denominators, strict=True)
    ]
    return {
        "median": round(statistics.median(ratios), 2),
        "min": round(min(ratios), 2),
        "max": round(max(ratios), 2),
    }


def effects(medians: dict[str, Sequence[float]]) -> dict[str, dict[str, Any]]:
    """How many times faster one side of each comparison is, repetition by repetition.

    Each ratio is "slower / faster" in the direction the hypothesis expects, so a value
    above 1 means the second named factor helps.
    """
    return {
        "engine_on_normalized": ratio_summary(
            medians[NORMALIZED_POSTGRES.key], medians[NORMALIZED_DUCKDB.key]
        ),
        "engine_on_star": ratio_summary(medians[STAR_POSTGRES.key], medians[STAR_DUCKDB.key]),
        "schema_on_postgres": ratio_summary(
            medians[NORMALIZED_POSTGRES.key], medians[STAR_POSTGRES.key]
        ),
        "schema_on_duckdb": ratio_summary(medians[NORMALIZED_DUCKDB.key], medians[STAR_DUCKDB.key]),
        "combined": ratio_summary(medians[NORMALIZED_POSTGRES.key], medians[STAR_DUCKDB.key]),
    }


def _connections(postgres, duck_star, duck_normalized) -> dict[str, Any]:
    return {
        NORMALIZED_POSTGRES.key: postgres,
        STAR_POSTGRES.key: postgres,
        NORMALIZED_DUCKDB.key: duck_normalized,
        STAR_DUCKDB.key: duck_star,
    }


def explain_plan(connection, cell: Cell, query: Query) -> str:
    sql = cell.sql(query)
    return (
        explain_postgres(connection, sql)
        if cell.engine == "postgres"
        else explain_duckdb(connection, sql)
    )


def run_grid(
    postgres,
    duck_star,
    duck_normalized,
    queries: Sequence[Query],
    *,
    repeats: int,
    warmup: int = DEFAULT_WARMUP_RUNS,
    repetitions: int = DEFAULT_MEASURED_RUNS,
    report: Reporter = print,
    clock: Callable[[], float] | None = None,
) -> dict[str, Any]:
    """Measure every query on every cell, `repeats` times, and return the raw results.

    Results are verified once, before the first measurement: all four cells must return the
    same rows as the normalized PostgreSQL model, which is the reference.
    """
    if repeats < MIN_REPEATS:
        raise ValueError(f"at least {MIN_REPEATS} repeats are required, got {repeats}")
    validate_runs(warmup, repetitions)
    connections = _connections(postgres, duck_star, duck_normalized)
    kwargs = {"clock": clock} if clock is not None else {}

    reference_rows: dict[str, list] = {}
    for query in queries:
        reference_rows[query.id] = (
            connections[NORMALIZED_POSTGRES.key].execute(NORMALIZED_POSTGRES.sql(query)).fetchall()
        )
        for cell in CELLS[1:]:
            rows = connections[cell.key].execute(cell.sql(query)).fetchall()
            check_equivalent(
                query.id,
                NORMALIZED_POSTGRES.label,
                reference_rows[query.id],
                cell.label,
                rows,
            )
    report(f"Results verified: all {len(CELLS)} models agree on {len(queries)} queries.")

    medians: dict[str, dict[str, list[float]]] = {
        query.id: {cell.key: [] for cell in CELLS} for query in queries
    }
    runs: dict[str, dict[str, list[Timing]]] = {
        query.id: {cell.key: [] for cell in CELLS} for query in queries
    }
    for repeat in range(1, repeats + 1):
        report(f"Repetition {repeat} of {repeats}")
        for query in queries:
            line = []
            for cell in CELLS:
                connection = connections[cell.key]
                sql = cell.sql(query)
                timing, _ = time_query(
                    lambda connection=connection, sql=sql: connection.execute(sql).fetchall(),
                    warmup,
                    repetitions,
                    **kwargs,
                )
                medians[query.id][cell.key].append(timing.median_ms)
                runs[query.id][cell.key].append(timing)
                line.append(f"{cell.key} {timing.median_ms:,.1f} ms")
            report(f"  {query.id}: " + ", ".join(line))

    plans = {
        query.id: {
            cell.key: explain_plan(connections[cell.key], cell, query)
            for cell in (STAR_POSTGRES, NORMALIZED_DUCKDB)
        }
        for query in queries
    }
    return {
        "queries": queries,
        "medians": medians,
        "result_rows": {query.id: len(reference_rows[query.id]) for query in queries},
        "plans": plans,
        "repeats": repeats,
        "warmup": warmup,
        "repetitions": repetitions,
    }


def build_report(
    profile, raw: dict[str, Any], dataset: dict[str, Any], environment: dict[str, Any]
) -> dict[str, Any]:
    queries = []
    for query in raw["queries"]:
        per_cell = raw["medians"][query.id]
        queries.append(
            {
                "id": query.id,
                "question": query.question,
                "result_rows": raw["result_rows"][query.id],
                "cells": {cell.key: spread(per_cell[cell.key]) for cell in CELLS},
                "effects": effects(per_cell),
                "plans": raw["plans"][query.id],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": profile.name,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataset": dataset,
        "environment": environment,
        "method": {
            "repeats": raw["repeats"],
            "warmup_runs": raw["warmup"],
            "measured_runs": raw["repetitions"],
            "timer": "perf_counter, execute + full fetch",
            "statistic": "median of the measured runs, then median across repeats",
        },
        "cells": [
            {"key": cell.key, "label": cell.label, "engine": cell.engine, "schema": cell.schema}
            for cell in CELLS
        ],
        "queries": queries,
        "repeatability": repeatability(queries),
    }


def _ms(value: float) -> str:
    return f"{value:,.1f}"


def _range(summary: dict[str, Any]) -> str:
    return f"{summary['median']:,.1f}x ({summary['min']:,.1f}-{summary['max']:,.1f})"


def render_markdown(report: dict[str, Any]) -> str:
    method = report["method"]
    dataset = report["dataset"]
    lines = [
        f"# Schema and engine experiments: {report['profile']} profile",
        "",
        f"{dataset['rows']:,} requests from NYC 311. The whole grid of four models was measured "
        f"{method['repeats']} times ({method['warmup_runs']} warm-up and "
        f"{method['measured_runs']} measured runs per query and model each time). "
        f"Generated {report['generated_at']}.",
        "",
        "Every model returns the same rows for every query (verified before measuring).",
        "",
        "## Median time per model (ms)",
        "",
        "Median across repetitions, with the spread (minimum-maximum) and the coefficient of "
        "variation in parentheses.",
        "",
        "| Query | " + " | ".join(cell["label"] for cell in report["cells"]) + " |",
        "|---|" + "---:|" * len(report["cells"]),
    ]
    for query in report["queries"]:
        cells = []
        for cell in report["cells"]:
            summary = query["cells"][cell["key"]]
            cells.append(
                f"{_ms(summary['median_ms'])} "
                f"({_ms(summary['min_ms'])}-{_ms(summary['max_ms'])}, CV {summary['cv_percent']}%)"
            )
        lines.append(f"| `{query['id'].split('_')[0]}` | " + " | ".join(cells) + " |")

    lines += [
        "",
        "## What explains the speedup",
        "",
        "Each value is how many times faster the second factor makes the same query, as the "
        "median across repetitions with the minimum-maximum in parentheses. "
        "*Engine* compares PostgreSQL with DuckDB on the same schema; "
        "*schema* compares the normalized model with the star schema on the same engine.",
        "",
        "| Query | Engine (normalized) | Engine (star) | Schema (PostgreSQL) | "
        "Schema (DuckDB) | Combined (official) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for query in report["queries"]:
        e = query["effects"]
        lines.append(
            f"| `{query['id'].split('_')[0]}` | {_range(e['engine_on_normalized'])} | "
            f"{_range(e['engine_on_star'])} | {_range(e['schema_on_postgres'])} | "
            f"{_range(e['schema_on_duckdb'])} | {_range(e['combined'])} |"
        )
    stability = report["repeatability"]
    lines += [
        "",
        "## Repeatability",
        "",
        f"{stability['within_limit']} of {stability['series']} series (one per query and model) "
        f"kept their medians within {stability['limit_percent']:.0f}% across repetitions "
        f"(maximum minus minimum, over the median). The widest spread was "
        f"{stability['worst']:.1f}%.",
        "",
        "## Method",
        "",
        f"- Timer: {method['timer']}, measured from the client.",
        "- Models: normalized (3NF) and star schema, each on PostgreSQL 17 and on DuckDB. The "
        "star schema in PostgreSQL has a primary key on every table and an index per foreign key "
        "of the fact table, like the normalized model; both DuckDB models store the fact table "
        "in creation order.",
        "- Queries are the same business questions as the official benchmark, written in each "
        "engine's dialect (`sql/controls/`).",
        "- Official numbers: `results/benchmark_full.md`. This run does not change them.",
        "",
    ]
    return "\n".join(lines)


def write_report(report: dict[str, Any], results_dir: Path) -> tuple[Path, Path]:
    results_dir.mkdir(parents=True, exist_ok=True)
    stem = f"experiments_{report['profile']}"
    json_path = results_dir / f"{stem}.json"
    markdown_path = results_dir / f"{stem}.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    markdown_path.write_text(render_markdown(report))
    return json_path, markdown_path
