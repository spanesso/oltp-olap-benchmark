"""Transactional operations (User Story 4): same answer on both models, no side effects."""

import pytest

from nyc311_bench.db import connect_duckdb
from nyc311_bench.queries import TRANSACTIONAL_QUERIES
from nyc311_bench.runner import fill, pick_identifiers, run_transactional
from tests.integration.equivalence import assert_equivalent


@pytest.fixture
def writable(built_models):
    pg, olap_path = built_models
    duck = connect_duckdb(olap_path)
    yield pg, duck
    duck.close()


def test_the_identifier_list_is_fixed_and_spread_over_the_data(writable):
    pg, _ = writable
    identifiers = pick_identifiers(pg, 20)
    assert identifiers == pick_identifiers(pg, 20)
    assert len(identifiers) == 20
    assert identifiers == sorted(identifiers)


def test_identifiers_cover_the_whole_key_range_even_for_a_small_table(writable):
    pg, _ = writable
    identifiers = pick_identifiers(pg, 11)
    first, last = pg.execute(
        "SELECT min(request_id), max(request_id) FROM oltp.service_request"
    ).fetchone()
    assert len(identifiers) == 11
    assert identifiers[0] == first
    # The last identifier sits in the final tenth of the ranks, not among the first few rows.
    ranks = pg.execute(
        "SELECT count(*) FROM oltp.service_request WHERE request_id <= %s", (identifiers[-1],)
    ).fetchone()[0]
    assert ranks > 1800
    assert last >= identifiers[-1]


def test_lookup_returns_the_same_request_on_both_models(writable):
    pg, duck = writable
    lookup = TRANSACTIONAL_QUERIES[0]
    for request_id in pick_identifiers(pg, 20):
        values = {"request_id": request_id}
        oltp_rows = pg.execute(fill(lookup.sql("oltp"), values)).fetchall()
        olap_rows = duck.execute(fill(lookup.sql("olap"), values)).fetchall()
        assert len(oltp_rows) == 1
        assert_equivalent(f"t1 id {request_id}", oltp_rows, olap_rows)


def test_the_insert_leaves_both_models_unchanged(writable):
    pg, duck = writable
    results = run_transactional(
        pg,
        duck,
        TRANSACTIONAL_QUERIES,
        warmup=1,
        repetitions=10,
        report=lambda _message: None,
    )
    assert [r.query.id for r in results] == ["t1_lookup_by_id", "t2_insert_request"]
    assert pg.execute("SELECT count(*) FROM oltp.service_request").fetchone()[0] == 2000
    assert duck.execute("SELECT count(*) FROM fact_service_request").fetchone()[0] == 2000


def test_results_report_one_row_for_lookup_and_none_for_insert(writable):
    pg, duck = writable
    lookup, insert = run_transactional(
        pg,
        duck,
        TRANSACTIONAL_QUERIES,
        warmup=1,
        repetitions=10,
        report=lambda _message: None,
    )
    assert lookup.result_rows == 1
    assert insert.result_rows == 0
    assert lookup.oltp_plan and lookup.olap_plan
    assert insert.oltp_plan == ""
