"""Load API pages into the staging area, idempotently and resumably.

Each page is inserted and the checkpoint advanced in the same transaction, so an
interruption leaves staging and checkpoint consistent and the next run continues from the
last committed page.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from nyc311_bench.config import CUT_END, CUT_START, DEFAULT_PAGE_SIZE
from nyc311_bench.socrata import Cursor

STAGING_COLUMNS = (
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "borough",
    "incident_zip",
    "community_board",
    "open_data_channel_type",
    "status",
)
TEXT_COLUMNS = STAGING_COLUMNS[3:]

FetchPage = Callable[[Cursor | None, int], list[dict[str, str]]]
Reporter = Callable[[str], None]


@dataclass(frozen=True)
class Rejection:
    unique_key: str | None
    reason: str
    raw: dict[str, Any]


@dataclass
class IngestSummary:
    target_rows: int
    rows_staged: int
    rows_loaded_now: int = 0
    rows_rejected_now: int = 0
    pages_fetched: int = 0
    duration_seconds: float = 0.0
    cut_exhausted: bool = False
    rejection_reasons: dict[str, int] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        return self.rows_staged >= self.target_rows


def _text(value: Any) -> str | None:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped or None


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def parse_row(raw: dict[str, Any]) -> tuple[Any, ...] | Rejection:
    """Turn one API row into a staging tuple, or say why it cannot be loaded.

    The API omits keys whose value is null, so every field is read with a default.
    """
    unique_key = _text(raw.get("unique_key"))
    if unique_key is None:
        return Rejection(None, "missing unique_key", raw)
    if not unique_key.isdigit():
        return Rejection(unique_key, "non-numeric unique_key", raw)

    created_text = _text(raw.get("created_date"))
    if created_text is None:
        return Rejection(unique_key, "missing created_date", raw)
    try:
        created_date = _timestamp(created_text)
    except ValueError:
        return Rejection(unique_key, "unparseable created_date", raw)

    closed_text = _text(raw.get("closed_date"))
    try:
        closed_date = _timestamp(closed_text) if closed_text else None
    except ValueError:
        return Rejection(unique_key, "unparseable closed_date", raw)

    return (unique_key, created_date, closed_date, *(_text(raw.get(c)) for c in TEXT_COLUMNS))


def _last_cursor(page: list[dict[str, str]]) -> Cursor:
    """Keyset position after a page: its last row that carries both key fields."""
    for row in reversed(page):
        try:
            return Cursor.from_row(row)
        except (KeyError, ValueError):
            continue
    raise ValueError("The page has no row with a usable created_date and unique_key.")


def _read_checkpoint(connection) -> tuple[Cursor | None, int]:
    connection.execute(
        "INSERT INTO staging.ingest_checkpoint (cut_start, cut_end) VALUES (%s, %s) "
        "ON CONFLICT DO NOTHING",
        (CUT_START, CUT_END),
    )
    last_created, last_key, rows_loaded = connection.execute(
        "SELECT last_created_date, last_unique_key, rows_loaded "
        "FROM staging.ingest_checkpoint WHERE cut_start = %s AND cut_end = %s",
        (CUT_START, CUT_END),
    ).fetchone()
    if last_created is None:
        return None, rows_loaded
    return Cursor(last_created.isoformat(timespec="milliseconds"), last_key), rows_loaded


def _store_page(connection, rows, rejections, cursor: Cursor) -> int:
    """Insert one page and advance the checkpoint atomically. Returns the rows added."""
    columns = ", ".join(STAGING_COLUMNS)
    with connection.transaction(), connection.cursor() as cur:
        # psycopg 3: `cursor.copy()` streams rows through COPY, far faster than INSERTs.
        cur.execute(
            "CREATE TEMP TABLE IF NOT EXISTS page_buffer "
            "(LIKE staging.service_request_raw) ON COMMIT DELETE ROWS"
        )
        with cur.copy(f"COPY page_buffer ({columns}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)
        cur.execute(
            f"INSERT INTO staging.service_request_raw ({columns}) "
            f"SELECT {columns} FROM page_buffer ON CONFLICT (unique_key) DO NOTHING"
        )
        inserted = cur.rowcount
        if rejections:
            cur.executemany(
                "INSERT INTO staging.rejected_row (unique_key, reason, raw) VALUES (%s, %s, %s)",
                [(r.unique_key, r.reason, json.dumps(r.raw)) for r in rejections],
            )
        cur.execute(
            "UPDATE staging.ingest_checkpoint SET last_created_date = %s, last_unique_key = %s, "
            "rows_loaded = rows_loaded + %s, updated_at = now() "
            "WHERE cut_start = %s AND cut_end = %s",
            (_timestamp(cursor.created_date), cursor.unique_key, inserted, CUT_START, CUT_END),
        )
    return inserted


def ingest(
    connection,
    fetch_page: FetchPage,
    target_rows: int,
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    report: Reporter = print,
) -> IngestSummary:
    """Stage rows of the cut until `target_rows` are present, resuming from the checkpoint."""
    if not connection.autocommit:
        # Each page must commit on its own; an enclosing transaction would defeat resuming.
        raise ValueError("ingest() needs a connection in autocommit mode")
    started = time.perf_counter()
    cursor, staged = _read_checkpoint(connection)
    summary = IngestSummary(target_rows=target_rows, rows_staged=staged)

    if staged >= target_rows:
        report(f"Staging already holds {staged:,} rows (target {target_rows:,}); nothing to do.")
    elif staged:
        report(f"Resuming from row {staged:,} of {target_rows:,}.")

    while summary.rows_staged < target_rows:
        limit = min(page_size, target_rows - summary.rows_staged)
        page = fetch_page(cursor, limit)
        summary.pages_fetched += 1
        if not page:
            summary.cut_exhausted = True
            break

        parsed = [parse_row(raw) for raw in page]
        rows = [p for p in parsed if not isinstance(p, Rejection)]
        rejections = [p for p in parsed if isinstance(p, Rejection)]
        cursor = _last_cursor(page)
        inserted = _store_page(connection, rows, rejections, cursor)

        summary.rows_staged += inserted
        summary.rows_loaded_now += inserted
        summary.rows_rejected_now += len(rejections)
        for rejection in rejections:
            summary.rejection_reasons[rejection.reason] = (
                summary.rejection_reasons.get(rejection.reason, 0) + 1
            )
        report(
            f"  page {summary.pages_fetched}: {inserted:,} rows "
            f"({summary.rows_staged:,} of {target_rows:,} staged)"
        )
        if len(page) < limit:
            summary.cut_exhausted = True
            break

    summary.duration_seconds = time.perf_counter() - started
    return summary


def format_summary(summary: IngestSummary) -> str:
    lines = [
        f"Load summary: {summary.rows_loaded_now:,} rows loaded in "
        f"{summary.duration_seconds:.1f}s over {summary.pages_fetched} page(s); "
        f"{summary.rows_staged:,} of {summary.target_rows:,} staged.",
        f"Rows rejected: {summary.rows_rejected_now:,}",
    ]
    lines += [
        f"  {reason}: {count:,}" for reason, count in sorted(summary.rejection_reasons.items())
    ]
    if summary.cut_exhausted and not summary.complete:
        lines.append(
            f"WARNING: the data cut holds only {summary.rows_staged:,} loadable rows, "
            f"fewer than the target of {summary.target_rows:,}."
        )
    return "\n".join(lines)
