"""Control models that separate the effect of the schema from the effect of the engine.

The official comparison pits a normalized schema on PostgreSQL against a star schema on
DuckDB, so two things change at once. Two extra models complete the 2x2 grid:

- the star schema built inside PostgreSQL (`star_pg` schema), and
- the normalized schema copied into DuckDB (`oltp` schema of a separate file).

Both are rebuilt from the OLTP tables, so they hold exactly the same requests.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from nyc311_bench.db import connect_duckdb, run_sql_file
from nyc311_bench.olap import SOURCE_COLUMNS
from nyc311_bench.oltp import OLTP_TABLES

STAR_PG_TABLES = (
    "dim_date",
    "dim_agency",
    "dim_complaint",
    "dim_location",
    "dim_channel",
    "dim_status",
    "fact_service_request",
)


def build_star_in_postgres(connection) -> dict[str, int]:
    """Rebuild the `star_pg` schema from the OLTP tables. Returns the row count per table."""
    with connection.transaction():
        run_sql_file(connection, "controls/star_pg/schema.sql")
        run_sql_file(connection, "controls/star_pg/load.sql")
        run_sql_file(connection, "controls/star_pg/indexes.sql")
    # Real statistics, as for the OLTP model; otherwise the planner would be handicapped.
    connection.execute("ANALYZE")
    return {
        table: connection.execute(f"SELECT count(*) FROM star_pg.{table}").fetchone()[0]
        for table in STAR_PG_TABLES
    }


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _copy_normalized_tables(duck, postgres_conninfo: str) -> None:
    """Copy the OLTP tables with DuckDB's postgres extension.

    The fact table is stored in creation order, as the star fact table is, so both DuckDB
    models have the same physical layout and only the schema differs.
    """
    duck.execute("INSTALL postgres")
    duck.execute("LOAD postgres")
    duck.execute(f"ATTACH {_quote(postgres_conninfo)} AS pg_source (TYPE postgres, READ_ONLY)")
    try:
        for table in OLTP_TABLES:
            order = " ORDER BY created_at, request_id" if table == "service_request" else ""
            duck.execute(
                f"CREATE TABLE oltp.{table} AS SELECT * FROM pg_source.oltp.{table}{order}"
            )
    finally:
        duck.execute("DETACH pg_source")


def _copy_normalized_tables_with_csv(duck, postgres_connection) -> None:
    """The same copy, streaming each table out of PostgreSQL with COPY (no extension)."""
    with tempfile.TemporaryDirectory(prefix="nyc311_3nf_") as directory:
        for table in OLTP_TABLES:
            columns = SOURCE_COLUMNS[table]
            path = Path(directory) / f"{table}.csv"
            order = " ORDER BY created_at, request_id" if table == "service_request" else ""
            query = (
                f"COPY (SELECT {', '.join(columns)} FROM oltp.{table}{order}) "
                "TO STDOUT (FORMAT csv)"
            )
            with (
                path.open("wb") as file,
                postgres_connection.cursor() as cursor,
                cursor.copy(query) as copy,
            ):
                for chunk in copy:
                    file.write(chunk)
            types = ", ".join(f"{_quote(name)}: {_quote(kind)}" for name, kind in columns.items())
            duck.execute(
                f"CREATE TABLE oltp.{table} AS SELECT * FROM read_csv("
                f"{_quote(str(path))}, header = false, columns = {{{types}}}){order}"
            )


def build_3nf_in_duckdb(path: Path, postgres_connection, postgres_conninfo: str) -> dict[str, int]:
    """Copy the normalized tables into a DuckDB file, keeping the `oltp` schema name.

    No indexes are created: scanning columns is DuckDB's idiomatic access path, as in the
    star model. Returns the row count per table.
    """
    duck = connect_duckdb(path)
    try:
        duck.execute("DROP SCHEMA IF EXISTS oltp CASCADE")
        duck.execute("CREATE SCHEMA oltp")
        try:
            _copy_normalized_tables(duck, postgres_conninfo)
        except Exception:  # noqa: BLE001 - no network for the extension: stream with COPY
            duck.execute("DROP SCHEMA IF EXISTS oltp CASCADE")
            duck.execute("CREATE SCHEMA oltp")
            _copy_normalized_tables_with_csv(duck, postgres_connection)
        duck.execute("ANALYZE")
        return {
            table: duck.execute(f"SELECT count(*) FROM oltp.{table}").fetchone()[0]
            for table in OLTP_TABLES
        }
    finally:
        duck.close()
