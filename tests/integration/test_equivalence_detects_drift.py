"""If one model drifts from the other, the equivalence check says which query differs."""

from nyc311_bench.db import connect_duckdb
from nyc311_bench.queries import QUERIES
from tests.integration.equivalence import assert_equivalent, run_on_both


def failing_queries(pg, duck) -> dict[str, str]:
    failures = {}
    for query in QUERIES:
        try:
            assert_equivalent(query.id, *run_on_both(pg, duck, query))
        except AssertionError as error:
            failures[query.id] = str(error)
    return failures


def test_changing_one_fact_row_in_one_model_is_detected(built_models):
    pg, olap_path = built_models
    duck = connect_duckdb(olap_path)
    try:
        assert failing_queries(pg, duck) == {}

        # Move one request to another channel in the analytical model only.
        duck.execute(
            "UPDATE fact_service_request SET channel_key = ("
            "  SELECT min(channel_key) FROM dim_channel WHERE channel_key <> ("
            "    SELECT channel_key FROM fact_service_request ORDER BY request_id LIMIT 1)) "
            "WHERE request_id = (SELECT min(request_id) FROM fact_service_request)"
        )
        failures = failing_queries(pg, duck)
    finally:
        duck.close()

    # Only the two queries that group by channel can see the change.
    assert set(failures) == {"q3_closure_rate_agency_channel", "q6_channel_share_by_quarter"}
    for query_id, message in failures.items():
        assert message.startswith(f"{query_id}: row ")
        assert "differs" in message


def test_a_changed_measure_is_detected(built_models):
    pg, olap_path = built_models
    duck = connect_duckdb(olap_path)
    try:
        duck.execute(
            "UPDATE fact_service_request SET resolution_hours = resolution_hours + 1000 "
            "WHERE request_id = (SELECT min(request_id) FROM fact_service_request "
            "WHERE has_valid_resolution)"
        )
        failures = failing_queries(pg, duck)
    finally:
        duck.close()
    assert "q2_top_types_per_zip" in failures
