"""Build the normalized OLTP model from the staging area."""

from __future__ import annotations

from nyc311_bench.db import run_sql_file

UNKNOWN = "Unknown"

# The first N staged rows in the order the API is read in, so a profile is always a prefix of
# the cut. Missing or blank dimension values become the 'Unknown' member (FR-012).
BUILD_SOURCE_SQL = f"""
CREATE TEMP TABLE build_source ON COMMIT DROP AS
SELECT
    unique_key::bigint AS request_id,
    created_date AS created_at,
    closed_date AS closed_at,
    COALESCE(NULLIF(btrim(agency), ''), '{UNKNOWN}') AS agency_code,
    COALESCE(NULLIF(btrim(agency_name), ''), '{UNKNOWN}') AS agency_name,
    COALESCE(NULLIF(btrim(complaint_type), ''), '{UNKNOWN}') AS complaint_type,
    COALESCE(NULLIF(btrim(descriptor), ''), '{UNKNOWN}') AS descriptor,
    COALESCE(NULLIF(btrim(borough), ''), '{UNKNOWN}') AS borough,
    COALESCE(NULLIF(btrim(incident_zip), ''), '{UNKNOWN}') AS zip_code,
    COALESCE(NULLIF(btrim(community_board), ''), '{UNKNOWN}') AS community_board,
    COALESCE(NULLIF(btrim(open_data_channel_type), ''), '{UNKNOWN}') AS channel,
    COALESCE(NULLIF(btrim(status), ''), '{UNKNOWN}') AS status
FROM (
    SELECT * FROM staging.service_request_raw
    ORDER BY created_date, unique_key
    LIMIT %s
) AS first_rows
"""

OLTP_TABLES = (
    "agency",
    "complaint_type",
    "complaint_descriptor",
    "borough",
    "location",
    "channel",
    "status",
    "service_request",
)


def build_oltp(connection, target_rows: int) -> dict[str, int]:
    """Rebuild the `oltp` schema from the first `target_rows` staged rows.

    The whole rebuild is one transaction: readers see either the old model or the new one.
    Returns the row count of every table.
    """
    with connection.transaction():
        run_sql_file(connection, "oltp/schema.sql")
        connection.execute(BUILD_SOURCE_SQL, (target_rows,))
        run_sql_file(connection, "oltp/load.sql")
        run_sql_file(connection, "oltp/indexes.sql")
    # ANALYZE gives the planner real statistics; without it the comparison would be unfair.
    connection.execute("ANALYZE")
    return table_counts(connection)


def table_counts(connection) -> dict[str, int]:
    return {
        table: connection.execute(f"SELECT count(*) FROM oltp.{table}").fetchone()[0]
        for table in OLTP_TABLES
    }
