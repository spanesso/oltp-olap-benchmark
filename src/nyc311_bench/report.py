"""Turn measurements into the two result files and the significance verdict."""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nyc311_bench.config import CUT_END, CUT_START, DATASET_NAME, Profile
from nyc311_bench.queries import ANALYTICAL
from nyc311_bench.runner import QueryResult, Timing

SCHEMA_VERSION = 1
SPEEDUP_THRESHOLD = 3.0
SIGNIFICANCE_RULE = (
    "OLAP at least 3x faster on the median in at least two thirds of analytical queries"
)
TIMER = "perf_counter, execute + full fetch"


def significance(results: Sequence[QueryResult], official: bool) -> dict[str, Any]:
    """SC-003, evaluated only on the official (full) profile."""
    analytical = [r for r in results if r.query.group == ANALYTICAL]
    meeting = sum(1 for r in analytical if r.speedup >= SPEEDUP_THRESHOLD)
    reached = meeting * 3 >= len(analytical) * 2 if analytical else False
    return {
        "evaluated": official,
        "rule": SIGNIFICANCE_RULE,
        "queries_meeting_3x": meeting,
        "analytical_queries": len(analytical),
        "reached": reached if official else None,
    }


def _timing(timing: Timing) -> dict[str, Any]:
    return {
        "runs_ms": [round(value, 3) for value in timing.runs_ms],
        "median_ms": round(timing.median_ms, 3),
        "p95_ms": round(timing.p95_ms, 3),
        "min_ms": round(timing.min_ms, 3),
        "max_ms": round(timing.max_ms, 3),
    }


def build_report(
    profile: Profile,
    results: Sequence[QueryResult],
    dataset: dict[str, Any],
    environment: dict[str, Any],
    warmup: int,
    repetitions: int,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now(UTC)
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": profile.name,
        "official": profile.official,
        "generated_at": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataset": {
            "source": DATASET_NAME,
            "cut_start": CUT_START.isoformat(),
            "cut_end": CUT_END.isoformat(),
            **dataset,
        },
        "environment": environment,
        "method": {"warmup_runs": warmup, "measured_runs": repetitions, "timer": TIMER},
        "queries": [
            {
                "id": r.query.id,
                "group": r.query.group,
                "question": r.query.question,
                "result_rows": r.result_rows,
                "oltp": _timing(r.oltp),
                "olap": _timing(r.olap),
                "speedup": round(r.speedup, 2),
                **(
                    {"oltp_explain": r.oltp_plan, "olap_explain": r.olap_plan}
                    if r.oltp_plan
                    else {}
                ),
            }
            for r in results
        ],
        "significance": significance(results, profile.official),
    }


def _winner(speedup: float) -> str:
    if speedup > 1:
        return f"OLAP, {speedup:,.1f}x faster"
    if speedup < 1:
        return f"OLTP, {1 / speedup:,.1f}x faster"
    return "tie"


def _verdict(report: dict[str, Any]) -> str:
    verdict = report["significance"]
    counts = (
        f"{verdict['queries_meeting_3x']} of {verdict['analytical_queries']} analytical queries "
        "are at least 3x faster on the OLAP model"
    )
    rule = f"Rule: {verdict['rule']}."
    if not verdict["evaluated"]:
        return (
            f"**Not evaluated on this profile.** {counts}, but the significance threshold is "
            "only judged on the full profile."
        )
    if verdict["reached"]:
        return f"**Significance threshold reached.** {counts}. {rule}"
    return (
        f"**Significance threshold NOT reached.** Only {counts}. {rule} "
        "The data, queries and configuration were left as they are."
    )


def render_markdown(report: dict[str, Any]) -> str:
    dataset, method, env = report["dataset"], report["method"], report["environment"]
    lines = [
        f"# Benchmark results: {report['profile']} profile",
        "",
        f"{dataset['rows']:,} requests from {dataset['source']}, "
        f"created {dataset['first_created_at']} to {dataset['last_created_at']}. "
        f"Generated {report['generated_at']}.",
        "",
    ]
    if not report["official"]:
        lines += [
            "> **These are not the official timings.** This profile exists to check that "
            "everything works; the official results are in `benchmark_full.md`.",
            "",
        ]
    lines += [
        "## Analytical queries",
        "",
        "Times in milliseconds: median, with the 95th percentile in parentheses.",
        "",
        "| Query | Question | OLTP (PostgreSQL) | OLAP (DuckDB) | Winner |",
        "|---|---|---:|---:|---|",
    ]
    for query in report["queries"]:
        if query["group"] != ANALYTICAL:
            continue
        lines.append(
            f"| `{query['id'].split('_')[0]}` | {query['question']} "
            f"| {query['oltp']['median_ms']:,.1f} ({query['oltp']['p95_ms']:,.1f}) "
            f"| {query['olap']['median_ms']:,.1f} ({query['olap']['p95_ms']:,.1f}) "
            f"| {_winner(query['speedup'])} |"
        )
    lines += ["", "## Verdict", "", _verdict(report), ""]

    others = [q for q in report["queries"] if q["group"] != ANALYTICAL]
    if others:
        lines += [
            "## Transactional operations",
            "",
            "Not counted in the verdict above.",
            "",
            "| Operation | OLTP (PostgreSQL) | OLAP (DuckDB) | Winner |",
            "|---|---:|---:|---|",
        ]
        lines += [
            f"| {q['question']} | {q['oltp']['median_ms']:,.2f} | {q['olap']['median_ms']:,.2f} "
            f"| {_winner(q['speedup'])} |"
            for q in others
        ]
        lines.append("")

    lines += [
        "## Method",
        "",
        f"- {method['warmup_runs']} discarded warm-up run(s), then {method['measured_runs']} "
        f"measured runs per query and model; the 95th percentile is taken over those "
        f"{method['measured_runs']} runs.",
        f"- Timer: {method['timer']}, measured from the client.",
        "- For each query, all runs on one model and then all runs on the other; nothing else "
        "running concurrently.",
        "- The difference combines two effects: the schema (normalized vs star) and the storage "
        "engine (row vs columnar).",
        "",
        "## Environment",
        "",
        f"- Machine: {env['cpu']}, {env['cores']} cores, {env['memory_gb']} GB RAM, {env['os']}",
        f"- Python {env['python']}",
        f"- PostgreSQL {env['postgresql']} ({env['postgresql_runtime']}): "
        + ", ".join(f"{k} = {v}" for k, v in env["postgresql_settings"].items()),
        f"- DuckDB {env['duckdb']} ({env['duckdb_runtime']}): "
        + ", ".join(f"{k} = {v}" for k, v in env["duckdb_settings"].items()),
        "",
    ]

    has_plans = any(q.get("oltp_explain") for q in report["queries"])
    if has_plans:
        lines += ["## Execution plans", ""]
        for query in report["queries"]:
            if not query.get("oltp_explain"):
                continue
            short_id = query["id"].split("_")[0]
            lines += [
                f"### {short_id}: {query['question']}",
                "",
                "**OLTP (PostgreSQL)**",
                "",
                "```",
                query["oltp_explain"],
                "```",
                "",
                "**OLAP (DuckDB)**",
                "",
                "```",
                query["olap_explain"],
                "```",
                "",
            ]

    return "\n".join(lines)


def write_report(report: dict[str, Any], results_dir: Path) -> tuple[Path, Path]:
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = results_dir / f"benchmark_{report['profile']}.json"
    markdown_path = results_dir / f"benchmark_{report['profile']}.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    markdown_path.write_text(render_markdown(report))
    return json_path, markdown_path
