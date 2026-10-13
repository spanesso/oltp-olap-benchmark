"""Every benchmark query returns the same rows on both models (FR-022, SC-004)."""

import pytest

from nyc311_bench.db import connect_duckdb
from nyc311_bench.queries import QUERIES
from tests.integration.equivalence import assert_equivalent, run_on_both, values_match


@pytest.mark.parametrize("query", QUERIES, ids=lambda query: query.id)
def test_query_is_equivalent_on_both_models(built_models, query):
    pg, olap_path = built_models
    duck = connect_duckdb(olap_path, read_only=True)
    try:
        oltp_rows, olap_rows = run_on_both(pg, duck, query)
    finally:
        duck.close()
    assert len(oltp_rows) > 0, f"{query.id} returns no rows on the fixture"
    assert_equivalent(query.id, oltp_rows, olap_rows)


@pytest.mark.parametrize(
    ("oltp_value", "olap_value", "expected"),
    [
        ("BROOKLYN", "BROOKLYN", True),
        ("BROOKLYN", "QUEENS", False),
        (10, 10, True),
        (10, 11, False),
        (0.1 + 0.2, 0.3, True),
        (100.0, 100.00001, False),
        (None, None, True),
        (None, 0, False),
        (5, "5", False),
        (1, True, False),
    ],
)
def test_value_comparison_rules(oltp_value, olap_value, expected):
    assert values_match(oltp_value, olap_value) is expected


def test_a_different_number_of_rows_is_reported():
    with pytest.raises(AssertionError, match="q_demo: OLTP returns 2 rows and OLAP returns 1"):
        assert_equivalent("q_demo", [("a", 1), ("b", 2)], [("a", 1)])


def test_the_first_differing_row_and_column_are_reported():
    with pytest.raises(AssertionError, match="q_demo: row 1, column 1 differs"):
        assert_equivalent("q_demo", [("a", 1), ("b", 2)], [("a", 1), ("b", 3)])
