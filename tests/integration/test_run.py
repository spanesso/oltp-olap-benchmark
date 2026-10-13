"""Measuring on real engines: results are produced, and unequal models are refused."""

import json

import pytest

from nyc311_bench import cli
from nyc311_bench.config import Profile
from nyc311_bench.db import connect_duckdb
from nyc311_bench.ingest import ingest
from nyc311_bench.olap import build_olap
from nyc311_bench.oltp import build_oltp
from nyc311_bench.queries import QUERIES
from nyc311_bench.report import build_report, write_report
from nyc311_bench.runner import (
    ParityError,
    check_parity,
    dataset_info,
    environment_info,
    run_queries,
)
from tests.integration.sources import FixtureSource

VALID_ROWS = 2000
FIXTURE = Profile("fixture", VALID_ROWS, False)


@pytest.fixture
def built(pg, olap_path, postgres_test_database, sample_rows):
    ingest(pg, FixtureSource(sample_rows), 5000, page_size=700, report=lambda _m: None)
    build_oltp(pg, VALID_ROWS)
    build_olap(olap_path, pg, postgres_test_database)
    return pg, olap_path


def test_run_measures_every_query_and_writes_both_files(built, tmp_path):
    pg, olap_path = built
    duck = connect_duckdb(olap_path, read_only=True)
    try:
        assert check_parity(pg, duck, expected_rows=VALID_ROWS) == VALID_ROWS
        results = run_queries(pg, duck, QUERIES, warmup=1, repetitions=10, report=lambda _m: None)
        report = build_report(FIXTURE, results, dataset_info(pg), environment_info(pg, duck), 1, 10)
    finally:
        duck.close()
    json_path, markdown_path = write_report(report, tmp_path)

    stored = json.loads(json_path.read_text())
    assert [q["id"] for q in stored["queries"]] == [q.id for q in QUERIES]
    assert stored["dataset"]["rows"] == VALID_ROWS
    assert stored["environment"]["postgresql"].startswith("17")
    assert stored["environment"]["duckdb_settings"]["threads"].isdigit()
    for query in stored["queries"]:
        assert query["result_rows"] > 0
        assert len(query["oltp"]["runs_ms"]) == len(query["olap"]["runs_ms"]) == 10
        assert query["speedup"] > 0
    assert "## Analytical queries" in markdown_path.read_text()


def test_parity_guard_refuses_models_with_different_rows(built):
    pg, olap_path = built
    duck = connect_duckdb(olap_path)
    try:
        duck.execute(
            "DELETE FROM fact_service_request WHERE request_id = "
            "(SELECT min(request_id) FROM fact_service_request)"
        )
        with pytest.raises(ParityError, match="different data"):
            check_parity(pg, duck)
    finally:
        duck.close()


def test_parity_guard_refuses_an_empty_model(pg, olap):
    with pytest.raises(ParityError, match="empty"):
        check_parity(pg, olap)


def test_parity_guard_refuses_a_volume_that_is_not_the_profile(built):
    pg, olap_path = built
    duck = connect_duckdb(olap_path, read_only=True)
    try:
        with pytest.raises(ParityError, match="profile expects 200,000"):
            check_parity(pg, duck, expected_rows=200_000)
    finally:
        duck.close()


def test_run_command_exits_with_code_4_and_measures_nothing(
    built, settings, monkeypatch, tmp_path, capsys
):
    _pg, olap_path = built
    monkeypatch.setattr(cli, "RESULTS_DIR", tmp_path / "results")
    env = {
        "POSTGRES_HOST": settings.postgres_host,
        "POSTGRES_PORT": str(settings.postgres_port),
        "POSTGRES_USER": settings.postgres_user,
        "POSTGRES_PASSWORD": settings.postgres_password,
        "POSTGRES_DB": "bench_test",
        "OLAP_PATH": str(olap_path),
    }
    assert cli.main(["run", "--profile", "quick"], env=env) == cli.EXIT_PARITY
    assert "Nothing was measured" in capsys.readouterr().err
    assert not (tmp_path / "results").exists()


def test_run_command_reports_a_missing_olap_file(settings, tmp_path, capsys):
    env = {"POSTGRES_PORT": str(settings.postgres_port), "OLAP_PATH": str(tmp_path / "no.duckdb")}
    assert cli.main(["run"], env=env) == cli.EXIT_PARITY
    assert "does not exist" in capsys.readouterr().err
