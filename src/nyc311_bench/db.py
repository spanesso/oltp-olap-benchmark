"""Connections to both engines and access to the SQL files under `sql/`."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from nyc311_bench.config import Settings

if TYPE_CHECKING:
    import duckdb
    import psycopg

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def read_sql(relative_path: str, sql_dir: Path = SQL_DIR) -> str:
    """Return the text of a SQL file, addressed relative to the `sql/` directory."""
    path = (sql_dir / relative_path).resolve()
    if not path.is_relative_to(sql_dir.resolve()):
        raise ValueError(f"SQL path escapes the sql directory: {relative_path!r}")
    if not path.is_file():
        raise FileNotFoundError(f"SQL file not found: {relative_path!r} (looked in {sql_dir})")
    return path.read_text()


def run_sql_file(connection: Any, relative_path: str, sql_dir: Path = SQL_DIR) -> None:
    """Execute every statement of a SQL file on a PostgreSQL or DuckDB connection."""
    connection.execute(read_sql(relative_path, sql_dir))


def connect_postgres(settings: Settings, dbname: str | None = None) -> psycopg.Connection:
    import psycopg

    return psycopg.connect(settings.postgres_conninfo(dbname))


def connect_duckdb(path: Path, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    import duckdb

    if not read_only:
        path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path), read_only=read_only)
