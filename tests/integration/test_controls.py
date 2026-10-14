"""The control models return the same rows as the official ones (schema x engine grid)."""

import pytest

from nyc311_bench import experiments as ex
from nyc311_bench.controls import build_3nf_in_duckdb, build_star_in_postgres
from nyc311_bench.db import connect_duckdb
from nyc311_bench.queries import QUERIES


@pytest.fixture
def grid(built_models, postgres_test_database, tmp_path):
    pg, olap_path = built_models
    build_star_in_postgres(pg)
    normalized_path = tmp_path / "normalized_test.duckdb"
    build_3nf_in_duckdb(normalized_path, pg, postgres_test_database)
    star = connect_duckdb(olap_path, read_only=True)
    normalized = connect_duckdb(normalized_path, read_only=True)
    yield pg, star, normalized
    star.close()
    normalized.close()


def test_control_models_hold_the_same_requests(grid):
    pg, star, normalized = grid
    assert pg.execute("SELECT count(*) FROM star_pg.fact_service_request").fetchone()[0] == 2000
    assert normalized.execute("SELECT count(*) FROM oltp.service_request").fetchone()[0] == 2000
    assert star.execute("SELECT count(*) FROM fact_service_request").fetchone()[0] == 2000


@pytest.mark.parametrize("query", QUERIES, ids=lambda query: query.id)
def test_every_model_returns_the_same_rows(grid, query):
    pg, star, normalized = grid
    connections = {
        "normalized_postgres": pg,
        "star_postgres": pg,
        "normalized_duckdb": normalized,
        "star_duckdb": star,
    }
    reference = pg.execute(ex.NORMALIZED_POSTGRES.sql(query)).fetchall()
    assert reference, f"{query.id} returns no rows on the fixture"
    for cell in ex.CELLS[1:]:
        rows = connections[cell.key].execute(cell.sql(query)).fetchall()
        ex.check_equivalent(query.id, ex.NORMALIZED_POSTGRES.label, reference, cell.label, rows)


def test_rebuilding_the_star_schema_in_postgres_is_idempotent(grid):
    pg, _, _ = grid
    counts = build_star_in_postgres(pg)
    assert counts["fact_service_request"] == 2000
    assert counts["dim_agency"] == pg.execute("SELECT count(*) FROM oltp.agency").fetchone()[0]


def test_the_whole_grid_runs_end_to_end(grid, tmp_path):
    pg, star, normalized = grid
    raw = ex.run_grid(pg, star, normalized, QUERIES, repeats=2, report=lambda _message: None)

    class Profile:
        name = "quick"

    report = ex.build_report(Profile, raw, {"rows": 2000}, {})
    json_path, markdown_path = ex.write_report(report, tmp_path)
    assert json_path.name == "experiments_quick.json"
    assert "Normalized on DuckDB" in markdown_path.read_text()
    assert len(report["queries"]) == len(QUERIES)


def test_the_csv_fallback_builds_the_same_normalized_model(grid, tmp_path):
    from nyc311_bench.controls import _copy_normalized_tables_with_csv
    from nyc311_bench.oltp import OLTP_TABLES

    pg, _, normalized = grid
    fallback = connect_duckdb(tmp_path / "fallback.duckdb")
    try:
        fallback.execute("CREATE SCHEMA oltp")
        _copy_normalized_tables_with_csv(fallback, pg)
        for table in OLTP_TABLES:
            expected = normalized.execute(f"SELECT count(*) FROM oltp.{table}").fetchone()[0]
            assert fallback.execute(f"SELECT count(*) FROM oltp.{table}").fetchone()[0] == expected
    finally:
        fallback.close()
