"""Integration test harness: real PostgreSQL and DuckDB, isolated from loaded data.

Tests under this directory use a dedicated PostgreSQL database (`bench_test`) and a
temporary DuckDB file, so they never touch the data loaded by the benchmark. They are
skipped with a clear reason when the docker PostgreSQL service is not reachable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nyc311_bench.config import Settings, load_dotenv
from nyc311_bench.db import connect_duckdb, run_sql_file

TEST_DATABASE = "bench_test"
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "sample_311.json"


def pytest_collection_modifyitems(items):
    for item in items:
        if "tests/integration" in item.path.as_posix():
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def settings() -> Settings:
    load_dotenv()
    return Settings.from_env()


@pytest.fixture(scope="session")
def postgres_test_database(settings) -> str:
    """Create an empty `bench_test` database and return its connection string."""
    psycopg = pytest.importorskip("psycopg", reason="psycopg is not installed: run `make install`")
    try:
        admin = psycopg.connect(settings.postgres_conninfo(), autocommit=True, connect_timeout=5)
    except psycopg.OperationalError as error:
        pytest.skip(f"PostgreSQL is not reachable: run `make up` ({error})")

    with admin:
        admin.execute(f'DROP DATABASE IF EXISTS "{TEST_DATABASE}" WITH (FORCE)')
        admin.execute(f'CREATE DATABASE "{TEST_DATABASE}"')
    yield settings.postgres_conninfo(TEST_DATABASE)

    with psycopg.connect(settings.postgres_conninfo(), autocommit=True) as admin:
        admin.execute(f'DROP DATABASE IF EXISTS "{TEST_DATABASE}" WITH (FORCE)')


@pytest.fixture
def pg(postgres_test_database):
    """A connection to the test database with fresh, empty staging and OLTP schemas."""
    import psycopg

    with psycopg.connect(postgres_test_database, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS staging CASCADE")
        run_sql_file(connection, "staging/schema.sql")
        run_sql_file(connection, "oltp/schema.sql")
        yield connection


@pytest.fixture
def olap_path(tmp_path) -> Path:
    return tmp_path / "olap_test.duckdb"


@pytest.fixture
def olap(olap_path):
    """A connection to a temporary DuckDB file with the empty star schema."""
    pytest.importorskip("duckdb", reason="duckdb is not installed: run `make install`")
    connection = connect_duckdb(olap_path)
    run_sql_file(connection, "olap/schema.sql")
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def sample_rows() -> list[dict[str, str]]:
    """The synthetic source rows, in the order the API would return them."""
    return json.loads(FIXTURE_PATH.read_text())
