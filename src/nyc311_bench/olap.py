"""Build the star schema in DuckDB from the OLTP model.

The OLTP tables are first copied into temporary `src_*` tables, then `sql/olap/load.sql`
shapes them into dimensions and facts. The copy uses DuckDB's `postgres` extension; if the
extension cannot be installed (no network), the tables are streamed out of PostgreSQL with
COPY instead. Both paths produce identical `src_*` tables.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from nyc311_bench.db import connect_duckdb, read_sql
from nyc311_bench.oltp import OLTP_TABLES

OLAP_TABLES = (
    "dim_date",
    "dim_agency",
    "dim_complaint",
    "dim_location",
    "dim_channel",
    "dim_status",
    "fact_service_request",
)

# Explicit column types for the COPY path, where DuckDB would otherwise have to guess them.
SOURCE_COLUMNS: dict[str, dict[str, str]] = {
    "agency": {"agency_id": "INTEGER", "code": "VARCHAR", "name": "VARCHAR"},
    "complaint_type": {"complaint_type_id": "INTEGER", "name": "VARCHAR"},
    "complaint_descriptor": {
        "descriptor_id": "INTEGER",
        "complaint_type_id": "INTEGER",
        "name": "VARCHAR",
    },
    "borough": {"borough_id": "INTEGER", "name": "VARCHAR"},
    "location": {
        "location_id": "INTEGER",
        "borough_id": "INTEGER",
        "zip_code": "VARCHAR",
        "community_board": "VARCHAR",
    },
    "channel": {"channel_id": "INTEGER", "name": "VARCHAR"},
    "status": {"status_id": "INTEGER", "name": "VARCHAR"},
    "service_request": {
        "request_id": "BIGINT",
        "created_at": "TIMESTAMP",
        "closed_at": "TIMESTAMP",
        "agency_id": "INTEGER",
        "descriptor_id": "INTEGER",
        "location_id": "INTEGER",
        "channel_id": "INTEGER",
        "status_id": "INTEGER",
    },
}


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _copy_with_extension(duck, postgres_conninfo: str) -> None:
    duck.execute("INSTALL postgres")
    duck.execute("LOAD postgres")
    duck.execute(f"ATTACH {_quote(postgres_conninfo)} AS oltp_source (TYPE postgres, READ_ONLY)")
    try:
        for table, columns in SOURCE_COLUMNS.items():
            duck.execute(
                f"CREATE OR REPLACE TEMP TABLE src_{table} AS "
                f"SELECT {', '.join(columns)} FROM oltp_source.oltp.{table}"
            )
    finally:
        duck.execute("DETACH oltp_source")


def _copy_with_csv(duck, postgres_connection) -> None:
    with tempfile.TemporaryDirectory(prefix="nyc311_olap_") as directory:
        for table, columns in SOURCE_COLUMNS.items():
            path = Path(directory) / f"{table}.csv"
            query = f"COPY (SELECT {', '.join(columns)} FROM oltp.{table}) TO STDOUT (FORMAT csv)"
            with (
                path.open("wb") as file,
                postgres_connection.cursor() as cursor,
                cursor.copy(query) as copy,
            ):
                for chunk in copy:
                    file.write(chunk)
            types = ", ".join(f"{_quote(name)}: {_quote(kind)}" for name, kind in columns.items())
            duck.execute(
                f"CREATE OR REPLACE TEMP TABLE src_{table} AS SELECT * FROM read_csv("
                f"{_quote(str(path))}, header = false, columns = {{{types}}})"
            )


def build_olap(
    olap_path: Path,
    postgres_connection,
    postgres_conninfo: str,
    *,
    use_extension: bool = True,
) -> tuple[dict[str, int], str]:
    """Rebuild the star schema file. Returns the row counts and the copy method used."""
    assert set(SOURCE_COLUMNS) == set(OLTP_TABLES)
    duck = connect_duckdb(olap_path)
    try:
        method = "postgres extension"
        if use_extension:
            try:
                _copy_with_extension(duck, postgres_conninfo)
            except Exception as error:  # noqa: BLE001 - any failure falls back to COPY
                method = f"COPY fallback (postgres extension unavailable: {type(error).__name__})"
                use_extension = False
        if not use_extension:
            if method == "postgres extension":
                method = "COPY"
            _copy_with_csv(duck, postgres_connection)

        duck.execute("BEGIN")
        duck.execute(read_sql("olap/schema.sql"))
        duck.execute(read_sql("olap/load.sql"))
        duck.execute("COMMIT")
        duck.execute("ANALYZE")
        return table_counts(duck), method
    finally:
        duck.close()


def table_counts(duck) -> dict[str, int]:
    return {
        table: duck.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in OLAP_TABLES
    }
