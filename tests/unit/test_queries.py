import pytest

from nyc311_bench.queries import ANALYTICAL, MODELS, QUERIES, analytical_queries


def test_there_are_at_least_six_analytical_queries():
    assert len(analytical_queries()) >= 6
    assert all(query.group == ANALYTICAL for query in analytical_queries())


def test_query_ids_are_unique():
    ids = [query.id for query in QUERIES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("query", QUERIES, ids=lambda query: query.id)
@pytest.mark.parametrize("model", MODELS)
def test_every_query_has_documented_sql_with_a_total_order(query, model):
    sql = query.sql(model)
    assert sql.startswith("-- Q"), "the business question must be the header comment"
    assert "ORDER BY" in sql.upper()
    assert query.question.split(",")[0].split("?")[0][:25] in sql.replace("\n-- ", " ")


def test_unknown_model_is_rejected():
    with pytest.raises(ValueError, match="Unknown model"):
        QUERIES[0].sql("mongodb")


def test_transactional_operations_are_a_separate_group_with_both_models():
    from nyc311_bench.queries import ANALYTICAL, QUERIES, TRANSACTIONAL, TRANSACTIONAL_QUERIES

    assert [query.id for query in TRANSACTIONAL_QUERIES] == ["t1_lookup_by_id", "t2_insert_request"]
    assert all(query.group == TRANSACTIONAL for query in TRANSACTIONAL_QUERIES)
    assert all(query.group == ANALYTICAL for query in QUERIES)
    for query in TRANSACTIONAL_QUERIES:
        for model in ("oltp", "olap"):
            assert query.sql(model).strip()
