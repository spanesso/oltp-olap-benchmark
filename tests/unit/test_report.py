import json
from datetime import UTC, datetime

import pytest

from nyc311_bench.config import Profile
from nyc311_bench.queries import ANALYTICAL, Query
from nyc311_bench.report import build_report, render_markdown, significance, write_report
from nyc311_bench.runner import QueryResult, summarize

FULL = Profile("full", 5_000_000, True)
QUICK = Profile("quick", 200_000, False)
DATASET = {
    "rows": 5_000_000,
    "first_created_at": "2024-01-01T00:00:00",
    "last_created_at": "2025-06-01T00:00:00",
}
ENVIRONMENT = {
    "os": "TestOS",
    "cpu": "arm",
    "cores": 10,
    "memory_gb": 16.0,
    "python": "3.13.9",
    "postgresql": "17.0",
    "postgresql_runtime": "docker",
    "postgresql_settings": {"work_mem": "4MB"},
    "duckdb": "1.5.6",
    "duckdb_runtime": "embedded",
    "duckdb_settings": {"threads": "10"},
}


def result(index, speedup, group=ANALYTICAL):
    query = Query(f"q{index}_name", group, f"Question {index}?")
    return QueryResult(query, 7, summarize([100.0 * speedup] * 10), summarize([100.0] * 10))


def report_for(profile, speedups):
    results = [result(i, s) for i, s in enumerate(speedups, start=1)]
    return build_report(
        profile, results, DATASET, ENVIRONMENT, 1, 10, datetime(2026, 10, 12, 18, 30, tzinfo=UTC)
    )


@pytest.mark.parametrize(
    ("speedups", "meeting", "reached"),
    [
        ([3.0, 3.0, 3.0, 3.0, 1.0, 1.0], 4, True),
        ([3.0, 3.0, 3.0, 2.99, 1.0, 1.0], 3, False),
        ([10.0] * 6, 6, True),
        ([0.5] * 6, 0, False),
        ([3.0, 3.0, 1.0], 2, True),
        ([3.0, 1.0, 1.0], 1, False),
    ],
)
def test_significance_at_the_boundaries(speedups, meeting, reached):
    verdict = significance([result(i, s) for i, s in enumerate(speedups)], official=True)
    assert verdict["queries_meeting_3x"] == meeting
    assert verdict["analytical_queries"] == len(speedups)
    assert verdict["reached"] is reached
    assert verdict["evaluated"] is True


def test_quick_profile_is_never_judged():
    verdict = significance([result(i, 50.0) for i in range(6)], official=False)
    assert verdict["evaluated"] is False
    assert verdict["reached"] is None
    assert verdict["queries_meeting_3x"] == 6


def test_transactional_operations_do_not_count_towards_significance():
    results = [result(i, 5.0) for i in range(6)] + [result(9, 0.1, group="transactional")]
    verdict = significance(results, official=True)
    assert verdict["analytical_queries"] == 6
    assert verdict["reached"] is True


def test_report_matches_the_results_contract():
    report = report_for(FULL, [5.0, 4.0, 3.5, 3.0, 2.0, 1.0])
    assert set(report) == {
        "schema_version",
        "profile",
        "official",
        "generated_at",
        "dataset",
        "environment",
        "method",
        "queries",
        "significance",
    }
    assert report["schema_version"] == 1
    assert (report["profile"], report["official"]) == ("full", True)
    assert report["generated_at"] == "2026-10-12T18:30:00Z"
    assert report["dataset"]["rows"] == 5_000_000
    assert report["dataset"]["cut_start"] == "2024-01-01T00:00:00"
    assert report["method"] == {
        "warmup_runs": 1,
        "measured_runs": 10,
        "timer": "perf_counter, execute + full fetch",
    }
    first = report["queries"][0]
    assert set(first) == {"id", "group", "question", "result_rows", "oltp", "olap", "speedup"}
    assert set(first["oltp"]) == {"runs_ms", "median_ms", "p95_ms", "min_ms", "max_ms"}
    assert len(first["oltp"]["runs_ms"]) == 10
    assert first["speedup"] == 5.0
    json.dumps(report)


def test_markdown_states_a_reached_verdict():
    text = render_markdown(report_for(FULL, [5.0, 4.0, 3.5, 3.0, 2.0, 1.0]))
    assert "**Significance threshold reached.** 4 of 6 analytical queries" in text
    assert "OLAP, 5.0x faster" in text
    assert "not the official timings" not in text


def test_markdown_states_an_unreached_verdict_explicitly():
    text = render_markdown(report_for(FULL, [5.0, 2.0, 1.5, 1.0, 0.5, 0.5]))
    assert "**Significance threshold NOT reached.** Only 1 of 6" in text
    assert "left as they are" in text
    assert "OLTP, 2.0x faster" in text


def test_markdown_warns_that_the_quick_profile_is_not_official():
    text = render_markdown(report_for(QUICK, [5.0] * 6))
    assert "These are not the official timings" in text
    assert "Not evaluated on this profile" in text
    assert "threshold reached" not in text


def test_markdown_names_the_engines_and_the_environment():
    text = render_markdown(report_for(FULL, [5.0] * 6))
    for expected in ("OLTP (PostgreSQL)", "OLAP (DuckDB)", "5,000,000 requests", "10 cores"):
        assert expected in text
    assert "1 discarded warm-up run(s), then 10 measured runs" in text


def test_write_report_creates_both_files(tmp_path):
    report = report_for(QUICK, [5.0] * 6)
    json_path, markdown_path = write_report(report, tmp_path / "results")
    assert json_path.name == "benchmark_quick.json"
    assert markdown_path.name == "benchmark_quick.md"
    assert json.loads(json_path.read_text()) == report
    assert markdown_path.read_text().startswith("# Benchmark results: quick profile")


def test_transactional_operations_get_their_own_section_and_can_favor_oltp():
    results = [result(i, 5.0) for i in range(1, 7)]
    results.append(result(9, 0.02, group="transactional"))
    report = build_report(FULL, results, DATASET, ENVIRONMENT, 1, 10)
    text = render_markdown(report)
    assert "## Transactional operations" in text
    assert "Not counted in the verdict above." in text
    assert "OLTP, 50.0x faster" in text
    assert report["significance"]["analytical_queries"] == 6


def test_no_transactional_section_when_the_group_was_not_measured():
    text = render_markdown(report_for(FULL, [5.0] * 6))
    assert "## Transactional operations" not in text
