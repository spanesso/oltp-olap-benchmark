"""The three schemas apply cleanly on the real engines and match data-model.md."""

from nyc311_bench.db import run_sql_file

STAGING_TABLES = {"service_request_raw", "ingest_checkpoint", "rejected_row"}
OLTP_TABLES = {
    "agency",
    "complaint_type",
    "complaint_descriptor",
    "borough",
    "location",
    "channel",
    "status",
    "service_request",
}
OLAP_TABLES = {
    "dim_date",
    "dim_agency",
    "dim_complaint",
    "dim_location",
    "dim_channel",
    "dim_status",
    "fact_service_request",
}


def tables_in(pg, schema: str) -> set[str]:
    rows = pg.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = %s", (schema,)
    ).fetchall()
    return {row[0] for row in rows}


def test_staging_schema_has_the_expected_tables(pg):
    assert tables_in(pg, "staging") == STAGING_TABLES


def test_oltp_schema_has_the_expected_tables(pg):
    assert tables_in(pg, "oltp") == OLTP_TABLES


def test_staging_schema_can_be_applied_again_without_losing_rows(pg):
    pg.execute(
        "INSERT INTO staging.service_request_raw (unique_key, created_date) "
        "VALUES ('1', '2024-01-01')"
    )
    run_sql_file(pg, "staging/schema.sql")
    assert pg.execute("SELECT count(*) FROM staging.service_request_raw").fetchone()[0] == 1


def test_service_request_requires_every_dimension(pg):
    columns = pg.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'oltp' AND table_name = 'service_request' AND is_nullable = 'NO'"
    ).fetchall()
    assert {row[0] for row in columns} == {
        "request_id",
        "created_at",
        "agency_id",
        "descriptor_id",
        "location_id",
        "channel_id",
        "status_id",
    }


def test_olap_schema_has_the_expected_tables(olap):
    rows = olap.execute("SELECT table_name FROM information_schema.tables").fetchall()
    assert {row[0] for row in rows} == OLAP_TABLES


def test_olap_schema_can_be_applied_again(olap):
    run_sql_file(olap, "olap/schema.sql")
    assert olap.execute("SELECT count(*) FROM fact_service_request").fetchone()[0] == 0


def test_sample_fixture_has_valid_and_rejectable_rows(sample_rows):
    assert len(sample_rows) == 2004
    assert sum("unique_key" not in row for row in sample_rows) == 1
