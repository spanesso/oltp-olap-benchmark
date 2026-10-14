from decimal import Decimal

import pytest

from nyc311_bench import experiments as ex
from nyc311_bench.queries import ANALYTICAL, Query

QUERY = Query("q1_volume_by_type_month_borough", ANALYTICAL, "How many?")


class FakeConnection:
    """Answers any statement with canned rows; EXPLAIN gets a two-column plan row."""

    def __init__(self, rows):
        self.rows = rows
        self.statements = []

    def execute(self, sql):
        self.statements.append(sql)
        self._current = [("analyzed_plan", "PLAN")] if "EXPLAIN" in sql else self.rows
        return self

    def fetchall(self):
        return self._current


def test_the_four_cells_cover_every_schema_and_engine_combination():
    assert {(cell.schema, cell.engine) for cell in ex.CELLS} == {
        ("normalized", "postgres"),
        ("normalized", "duckdb"),
        ("star", "postgres"),
        ("star", "duckdb"),
    }


@pytest.mark.parametrize("cell", ex.CELLS, ids=lambda cell: cell.key)
def test_every_cell_has_a_sql_file_for_every_query(cell):
    from nyc311_bench.queries import QUERIES

    for query in QUERIES:
        assert cell.sql(query).strip(), f"{cell.key} has no SQL for {query.id}"


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (1, 1, True),
        (1, 2, False),
        ("a", "a", True),
        ("a", "b", False),
        (None, None, True),
        (None, 0, False),
        (0.1 + 0.2, 0.3, True),
        (Decimal("2.5"), 2.5, True),
        (100.0, 100.00001, False),
        (3, 3.0, True),
    ],
)
def test_value_comparison_rules(left, right, expected):
    assert ex.values_match(left, right) is expected


def test_different_row_counts_are_reported():
    with pytest.raises(ex.EquivalenceError, match="returns 2 rows, B returns 1"):
        ex.check_equivalent("q", "A", [("x",), ("y",)], "B", [("x",)])


def test_the_first_differing_row_is_reported():
    with pytest.raises(ex.EquivalenceError, match="row 1 differs between A and B"):
        ex.check_equivalent("q", "A", [("x", 1), ("y", 2)], "B", [("x", 1), ("y", 3)])


def test_identical_results_pass():
    ex.check_equivalent("q", "A", [("x", 1.0)], "B", [("x", Decimal("1.0"))])


def test_spread_of_a_single_repetition_has_no_variation():
    summary = ex.spread([120.0])
    assert summary["median_ms"] == 120.0
    assert summary["cv_percent"] == 0.0


def test_spread_reports_median_range_and_variation():
    summary = ex.spread([100.0, 110.0, 120.0])
    assert summary["median_ms"] == 110.0
    assert (summary["min_ms"], summary["max_ms"]) == (100.0, 120.0)
    assert summary["cv_percent"] == pytest.approx(9.1, abs=0.1)


def test_ratio_summary_is_computed_repetition_by_repetition():
    summary = ex.ratio_summary([100.0, 300.0, 200.0], [10.0, 10.0, 10.0])
    assert summary == {"median": 20.0, "min": 10.0, "max": 30.0}


def test_effects_separate_engine_from_schema():
    medians = {
        "normalized_postgres": [1000.0],
        "star_postgres": [500.0],
        "normalized_duckdb": [20.0],
        "star_duckdb": [10.0],
    }
    result = ex.effects(medians)
    assert result["engine_on_normalized"]["median"] == 50.0
    assert result["engine_on_star"]["median"] == 50.0
    assert result["schema_on_postgres"]["median"] == 2.0
    assert result["schema_on_duckdb"]["median"] == 2.0
    assert result["combined"]["median"] == 100.0


def test_a_grid_needs_at_least_two_repeats():
    connection = FakeConnection([("a", 1)])
    with pytest.raises(ValueError, match="at least 2 repeats"):
        ex.run_grid(connection, connection, connection, [QUERY], repeats=1, report=lambda _m: None)


def test_models_that_disagree_are_never_measured():
    agreeing = FakeConnection([("a", 1)])
    different = FakeConnection([("a", 2)])
    with pytest.raises(ex.EquivalenceError):
        ex.run_grid(agreeing, agreeing, different, [QUERY], repeats=2, report=lambda _m: None)
    assert not any("EXPLAIN" in sql for sql in agreeing.statements)


def test_the_grid_measures_every_cell_on_every_repeat():
    connection = FakeConnection([("a", 1)])
    raw = ex.run_grid(
        connection, connection, connection, [QUERY], repeats=2, report=lambda _m: None
    )
    per_cell = raw["medians"][QUERY.id]
    assert set(per_cell) == {cell.key for cell in ex.CELLS}
    assert all(len(values) == 2 for values in per_cell.values())
    assert raw["result_rows"][QUERY.id] == 1
    # PostgreSQL plans are in the first column, DuckDB plans in the second.
    assert raw["plans"][QUERY.id]["star_postgres"] == "analyzed_plan"
    assert raw["plans"][QUERY.id]["normalized_duckdb"] == "PLAN"


def test_markdown_lists_every_model_and_the_effects():
    connection = FakeConnection([("a", 1)])
    raw = ex.run_grid(
        connection, connection, connection, [QUERY], repeats=2, report=lambda _m: None
    )

    class Profile:
        name = "quick"

    report = ex.build_report(Profile, raw, {"rows": 10}, {})
    text = ex.render_markdown(report)
    for cell in ex.CELLS:
        assert cell.label in text
    assert "What explains the speedup" in text
    assert report["method"]["repeats"] == 2


def test_spread_reports_the_range_over_the_median():
    assert ex.spread([100.0, 110.0, 120.0])["range_percent"] == pytest.approx(18.2, abs=0.1)


def test_repeatability_counts_series_within_the_limit():
    queries = [
        {
            "id": "q1",
            "cells": {
                "a": {"range_percent": 5.0},
                "b": {"range_percent": 19.9},
                "c": {"range_percent": 20.0},
                "d": {"range_percent": 63.0},
            },
        }
    ]
    stability = ex.repeatability(queries)
    assert stability["series"] == 4
    assert stability["within_limit"] == 2
    assert stability["worst"] == 63.0
