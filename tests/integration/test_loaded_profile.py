"""The same parity and equivalence checks, against the profile currently loaded.

Skipped by default. Run with `pytest -m loaded` after `benchmark.py build`.
"""

import pytest

from nyc311_bench.queries import QUERIES
from tests.integration.equivalence import assert_equivalent, run_on_both
from tests.integration.test_model_parity import DIMENSION_TOTALS

pytestmark = pytest.mark.loaded


def test_both_models_hold_the_same_requests(loaded_models):
    pg, duck = loaded_models
    oltp = pg.execute(
        "SELECT count(*), sum(request_id), min(request_id), max(request_id) "
        "FROM oltp.service_request"
    ).fetchone()
    olap = duck.execute(
        "SELECT count(*), sum(request_id), min(request_id), max(request_id) "
        "FROM fact_service_request"
    ).fetchone()
    assert tuple(int(value) for value in oltp) == tuple(int(value) for value in olap)
    assert oltp[0] > 0


@pytest.mark.parametrize("dimension", sorted(DIMENSION_TOTALS))
def test_totals_per_dimension_member_match(loaded_models, dimension):
    pg, duck = loaded_models
    oltp_sql, olap_sql = DIMENSION_TOTALS[dimension]
    assert dict(pg.execute(oltp_sql).fetchall()) == dict(duck.execute(olap_sql).fetchall())


@pytest.mark.parametrize("query", QUERIES, ids=lambda query: query.id)
def test_query_is_equivalent_on_both_models(loaded_models, query):
    pg, duck = loaded_models
    oltp_rows, olap_rows = run_on_both(pg, duck, query)
    assert len(oltp_rows) > 0
    assert_equivalent(query.id, oltp_rows, olap_rows)
