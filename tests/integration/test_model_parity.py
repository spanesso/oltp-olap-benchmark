"""Both models hold the same requests (data-model.md section 4, FR-011, FR-012, FR-021)."""

import pytest

from nyc311_bench.db import connect_duckdb
from nyc311_bench.ingest import ingest
from nyc311_bench.olap import build_olap
from nyc311_bench.oltp import build_oltp
from tests.integration.sources import FixtureSource

VALID_ROWS = 2000

# For each dimension: the query giving (member, requests) on each model.
DIMENSION_TOTALS = {
    "agency": (
        "SELECT a.code || ' / ' || a.name, count(*) FROM oltp.service_request r "
        "JOIN oltp.agency a USING (agency_id) GROUP BY 1",
        "SELECT a.code || ' / ' || a.name, count(*) FROM fact_service_request f "
        "JOIN dim_agency a USING (agency_key) GROUP BY 1",
    ),
    "complaint": (
        "SELECT t.name || ' / ' || d.name, count(*) FROM oltp.service_request r "
        "JOIN oltp.complaint_descriptor d USING (descriptor_id) "
        "JOIN oltp.complaint_type t USING (complaint_type_id) GROUP BY 1",
        "SELECT c.complaint_type || ' / ' || c.descriptor, count(*) FROM fact_service_request f "
        "JOIN dim_complaint c USING (complaint_key) GROUP BY 1",
    ),
    "location": (
        "SELECT b.name || ' / ' || l.zip_code || ' / ' || l.community_board, count(*) "
        "FROM oltp.service_request r JOIN oltp.location l USING (location_id) "
        "JOIN oltp.borough b USING (borough_id) GROUP BY 1",
        "SELECT l.borough || ' / ' || l.zip_code || ' / ' || l.community_board, count(*) "
        "FROM fact_service_request f JOIN dim_location l USING (location_key) GROUP BY 1",
    ),
    "channel": (
        "SELECT c.name, count(*) FROM oltp.service_request r "
        "JOIN oltp.channel c USING (channel_id) GROUP BY 1",
        "SELECT c.name, count(*) FROM fact_service_request f "
        "JOIN dim_channel c USING (channel_key) GROUP BY 1",
    ),
    "status": (
        "SELECT s.name, count(*) FROM oltp.service_request r "
        "JOIN oltp.status s USING (status_id) GROUP BY 1",
        "SELECT s.name, count(*) FROM fact_service_request f "
        "JOIN dim_status s USING (status_key) GROUP BY 1",
    ),
    "month": (
        "SELECT to_char(created_at, 'YYYY-MM'), count(*) FROM oltp.service_request GROUP BY 1",
        "SELECT d.year || '-' || lpad(CAST(d.month AS VARCHAR), 2, '0'), count(*) "
        "FROM fact_service_request f JOIN dim_date d USING (date_key) GROUP BY 1",
    ),
}


@pytest.fixture(params=[True, False], ids=["postgres-extension", "copy-fallback"])
def models(request, pg, olap_path, postgres_test_database, sample_rows):
    """Both models built from the fixture, once per way of copying OLTP into DuckDB."""
    ingest(pg, FixtureSource(sample_rows), 5000, page_size=700, report=lambda _m: None)
    oltp_counts = build_oltp(pg, VALID_ROWS)
    olap_counts, method = build_olap(
        olap_path, pg, postgres_test_database, use_extension=request.param
    )
    duck = connect_duckdb(olap_path, read_only=True)
    yield pg, duck, oltp_counts, olap_counts, method
    duck.close()


def test_both_models_hold_the_target_number_of_requests(models):
    _pg, _duck, oltp_counts, olap_counts, _method = models
    assert oltp_counts["service_request"] == olap_counts["fact_service_request"] == VALID_ROWS


def test_the_set_of_request_identifiers_is_identical(models):
    pg, duck, *_ = models
    oltp_ids = {r[0] for r in pg.execute("SELECT request_id FROM oltp.service_request").fetchall()}
    olap_ids = {
        r[0] for r in duck.execute("SELECT request_id FROM fact_service_request").fetchall()
    }
    assert oltp_ids == olap_ids
    assert len(oltp_ids) == VALID_ROWS


@pytest.mark.parametrize("dimension", sorted(DIMENSION_TOTALS))
def test_totals_per_dimension_member_match(models, dimension):
    pg, duck, *_ = models
    oltp_sql, olap_sql = DIMENSION_TOTALS[dimension]
    oltp_totals = dict(pg.execute(oltp_sql).fetchall())
    olap_totals = dict(duck.execute(olap_sql).fetchall())
    assert oltp_totals == olap_totals
    assert sum(oltp_totals.values()) == VALID_ROWS


def test_dimension_sizes_match_the_lookup_tables(models):
    _pg, _duck, oltp_counts, olap_counts, _method = models
    assert olap_counts["dim_agency"] == oltp_counts["agency"]
    assert olap_counts["dim_complaint"] == oltp_counts["complaint_descriptor"]
    assert olap_counts["dim_location"] == oltp_counts["location"]
    assert olap_counts["dim_channel"] == oltp_counts["channel"]
    assert olap_counts["dim_status"] == oltp_counts["status"]


def test_resolution_measures_match(models):
    pg, duck, *_ = models
    valid = "closed_at IS NOT NULL AND closed_at >= created_at"
    oltp = pg.execute(
        f"SELECT count(*) FILTER (WHERE {valid}), "
        f"sum(extract(epoch FROM closed_at - created_at) / 3600.0) FILTER (WHERE {valid}), "
        f"count(*) FILTER (WHERE {valid} AND closed_at - created_at <= interval '30 days'), "
        "count(*) FILTER (WHERE closed_at IS NULL), "
        "count(*) FILTER (WHERE closed_at < created_at) FROM oltp.service_request"
    ).fetchone()
    olap = duck.execute(
        "SELECT count(*) FILTER (WHERE has_valid_resolution), sum(resolution_hours), "
        "count(*) FILTER (WHERE closed_within_30d), count(*) FILTER (WHERE NOT is_closed), "
        "count(*) FILTER (WHERE is_closed AND NOT has_valid_resolution) FROM fact_service_request"
    ).fetchone()
    assert (oltp[0], oltp[2], oltp[3], oltp[4]) == (olap[0], olap[2], olap[3], olap[4])
    assert float(oltp[1]) == pytest.approx(olap[1], rel=1e-9)
    assert oltp[3] == 120
    assert oltp[4] == 33


def test_missing_values_map_to_unknown_in_both_models(models):
    pg, duck, *_ = models
    oltp = pg.execute(
        "SELECT count(*) FILTER (WHERE b.name = 'Unknown'), "
        "count(*) FILTER (WHERE l.zip_code = 'Unknown'), "
        "count(*) FILTER (WHERE c.name = 'Unknown') FROM oltp.service_request r "
        "JOIN oltp.location l USING (location_id) JOIN oltp.borough b USING (borough_id) "
        "JOIN oltp.channel c USING (channel_id)"
    ).fetchone()
    olap = duck.execute(
        "SELECT count(*) FILTER (WHERE l.borough = 'Unknown'), "
        "count(*) FILTER (WHERE l.zip_code = 'Unknown'), "
        "count(*) FILTER (WHERE c.name = 'Unknown') FROM fact_service_request f "
        "JOIN dim_location l USING (location_key) JOIN dim_channel c USING (channel_key)"
    ).fetchone()
    assert oltp == olap == (31, 55, 37)


def test_an_agency_code_with_two_names_keeps_both(models):
    pg, *_ = models
    names = pg.execute("SELECT count(*) FROM oltp.agency WHERE code = 'DOHMH'").fetchone()[0]
    assert names == 2


def test_date_dimension_covers_every_day_loaded(models):
    _pg, duck, *_ = models
    days, first, last, orphans = duck.execute(
        "SELECT count(*), min(date), max(date), "
        "(SELECT count(*) FROM fact_service_request f ANTI JOIN dim_date d USING (date_key)) "
        "FROM dim_date"
    ).fetchone()
    assert orphans == 0
    assert days == (last - first).days + 1


def test_a_smaller_target_takes_a_prefix_of_the_staged_rows(
    pg, olap_path, postgres_test_database, sample_rows
):
    ingest(pg, FixtureSource(sample_rows), 5000, page_size=700, report=lambda _m: None)
    assert build_oltp(pg, 500)["service_request"] == 500
    olap_counts, _ = build_olap(olap_path, pg, postgres_test_database)
    assert olap_counts["fact_service_request"] == 500
    newest_loaded = pg.execute("SELECT max(created_at) FROM oltp.service_request").fetchone()[0]
    oldest_left_out = pg.execute(
        "SELECT min(created_date) FROM (SELECT created_date FROM staging.service_request_raw "
        "ORDER BY created_date, unique_key OFFSET 500) AS rest"
    ).fetchone()[0]
    assert newest_loaded <= oldest_left_out


def test_rebuilding_gives_the_same_models(pg, olap_path, postgres_test_database, sample_rows):
    ingest(pg, FixtureSource(sample_rows), 5000, page_size=700, report=lambda _m: None)
    first_oltp = build_oltp(pg, VALID_ROWS)
    first_olap, _ = build_olap(olap_path, pg, postgres_test_database)
    assert build_oltp(pg, VALID_ROWS) == first_oltp
    assert build_olap(olap_path, pg, postgres_test_database)[0] == first_olap
