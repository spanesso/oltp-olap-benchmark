"""Staging load: idempotent, resumable, and explicit about rejected rows."""

import psycopg
import pytest

from nyc311_bench.ingest import ingest
from nyc311_bench.socrata import SocrataUnavailable
from tests.integration.sources import FixtureSource

VALID_ROWS = 2000


def silent(_message):
    pass


def staged_count(pg) -> int:
    return pg.execute("SELECT count(*) FROM staging.service_request_raw").fetchone()[0]


def test_loads_the_requested_number_of_rows(pg, sample_rows):
    summary = ingest(pg, FixtureSource(sample_rows), 1500, page_size=400, report=silent)
    assert summary.complete
    assert summary.rows_staged == staged_count(pg) == 1500
    assert summary.pages_fetched == 4


def test_running_again_downloads_nothing_and_changes_nothing(pg, sample_rows):
    ingest(pg, FixtureSource(sample_rows), 1500, page_size=400, report=silent)
    source = FixtureSource(sample_rows)
    summary = ingest(pg, source, 1500, page_size=400, report=silent)
    assert source.calls == 0
    assert summary.rows_loaded_now == 0
    assert staged_count(pg) == 1500


def test_a_larger_target_continues_where_the_smaller_one_stopped(pg, sample_rows):
    ingest(pg, FixtureSource(sample_rows), 500, page_size=500, report=silent)
    summary = ingest(pg, FixtureSource(sample_rows), 1200, page_size=500, report=silent)
    assert summary.rows_loaded_now == 700
    assert staged_count(pg) == 1200


def test_an_interrupted_load_resumes_from_the_checkpoint(pg, sample_rows):
    with pytest.raises(SocrataUnavailable):
        ingest(pg, FixtureSource(sample_rows, fail_on_call=3), 1500, page_size=400, report=silent)
    assert staged_count(pg) == 800

    source = FixtureSource(sample_rows)
    summary = ingest(pg, source, 1500, page_size=400, report=silent)
    assert summary.rows_loaded_now == 700
    assert source.calls == 2
    assert staged_count(pg) == 1500


def test_staged_rows_are_the_first_rows_of_the_cut_in_order(pg, sample_rows):
    ingest(pg, FixtureSource(sample_rows), 300, page_size=100, report=silent)
    staged = pg.execute(
        "SELECT unique_key FROM staging.service_request_raw ORDER BY created_date, unique_key"
    ).fetchall()
    expected = [r["unique_key"] for r in sample_rows if r.get("unique_key", "x").isdigit()][:300]
    assert [row[0] for row in staged] == expected


def test_rejected_rows_are_recorded_with_their_reason(pg, sample_rows):
    summary = ingest(pg, FixtureSource(sample_rows), 5000, page_size=700, report=silent)
    assert summary.cut_exhausted and not summary.complete
    assert staged_count(pg) == VALID_ROWS
    reasons = dict(
        pg.execute("SELECT reason, count(*) FROM staging.rejected_row GROUP BY reason").fetchall()
    )
    assert reasons == {
        "missing unique_key": 1,
        "non-numeric unique_key": 1,
        "missing created_date": 1,
        "unparseable created_date": 1,
    }
    assert summary.rejection_reasons == reasons


def test_missing_values_are_stored_as_nulls(pg, sample_rows):
    ingest(pg, FixtureSource(sample_rows), 5000, page_size=700, report=silent)
    nulls = pg.execute(
        "SELECT count(*) FILTER (WHERE closed_date IS NULL), "
        "count(*) FILTER (WHERE borough IS NULL), "
        "count(*) FILTER (WHERE incident_zip IS NULL) FROM staging.service_request_raw"
    ).fetchone()
    assert nulls == (120, 31, 55)


def test_refuses_a_connection_that_is_not_in_autocommit_mode(postgres_test_database, sample_rows):
    with (
        psycopg.connect(postgres_test_database) as connection,
        pytest.raises(ValueError, match="autocommit"),
    ):
        ingest(connection, FixtureSource(sample_rows), 10, report=silent)
