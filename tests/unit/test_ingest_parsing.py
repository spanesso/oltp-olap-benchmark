from datetime import datetime

import pytest

from nyc311_bench.ingest import IngestSummary as Summary
from nyc311_bench.ingest import Rejection, format_summary, parse_row

FULL_ROW = {
    "unique_key": "59894610",
    "created_date": "2024-01-01T00:00:00.000",
    "closed_date": "2024-01-03T10:30:00.000",
    "agency": "NYPD",
    "agency_name": "New York City Police Department",
    "complaint_type": "Noise - Residential",
    "descriptor": "Loud Music/Party",
    "borough": "BROOKLYN",
    "incident_zip": "11201",
    "community_board": "02 BROOKLYN",
    "open_data_channel_type": "MOBILE",
    "status": "Closed",
}


def without(*keys):
    return {k: v for k, v in FULL_ROW.items() if k not in keys}


def test_a_full_row_becomes_a_staging_tuple_in_column_order():
    assert parse_row(FULL_ROW) == (
        "59894610",
        datetime(2024, 1, 1),
        datetime(2024, 1, 3, 10, 30),
        "NYPD",
        "New York City Police Department",
        "Noise - Residential",
        "Loud Music/Party",
        "BROOKLYN",
        "11201",
        "02 BROOKLYN",
        "MOBILE",
        "Closed",
    )


def test_keys_omitted_by_the_api_become_nulls():
    row = parse_row(without("closed_date", "borough", "incident_zip", "open_data_channel_type"))
    assert row[2] is None
    assert row[7] is None
    assert row[8] is None
    assert row[10] is None


def test_blank_text_is_treated_as_missing():
    row = parse_row({**FULL_ROW, "borough": "   ", "descriptor": ""})
    assert row[7] is None
    assert row[6] is None


def test_text_is_trimmed():
    assert parse_row({**FULL_ROW, "agency": " DOT "})[3] == "DOT"


@pytest.mark.parametrize(
    ("raw", "reason", "key"),
    [
        (without("unique_key"), "missing unique_key", None),
        ({**FULL_ROW, "unique_key": "ABC-123"}, "non-numeric unique_key", "ABC-123"),
        (without("created_date"), "missing created_date", "59894610"),
        ({**FULL_ROW, "created_date": "not-a-date"}, "unparseable created_date", "59894610"),
        ({**FULL_ROW, "closed_date": "soon"}, "unparseable closed_date", "59894610"),
    ],
)
def test_unloadable_rows_are_rejected_with_a_reason(raw, reason, key):
    result = parse_row(raw)
    assert isinstance(result, Rejection)
    assert result.reason == reason
    assert result.unique_key == key
    assert result.raw == raw


def test_a_row_closed_before_it_was_created_is_still_loaded():
    row = parse_row({**FULL_ROW, "closed_date": "2023-12-31T00:00:00.000"})
    assert not isinstance(row, Rejection)
    assert row[2] < row[1]


def test_summary_reports_rows_rejections_and_duration():
    summary = Summary(
        target_rows=1000,
        rows_staged=1000,
        rows_loaded_now=1000,
        rows_rejected_now=3,
        pages_fetched=2,
        duration_seconds=12.34,
        rejection_reasons={"missing unique_key": 1, "non-numeric unique_key": 2},
    )
    text = format_summary(summary)
    assert "1,000 rows loaded in 12.3s over 2 page(s)" in text
    assert "Rows rejected: 3" in text
    assert "non-numeric unique_key: 2" in text
    assert "WARNING" not in text


def test_summary_warns_when_the_cut_is_smaller_than_the_target():
    summary = Summary(target_rows=5000, rows_staged=2000, cut_exhausted=True)
    assert "holds only 2,000 loadable rows" in format_summary(summary)
