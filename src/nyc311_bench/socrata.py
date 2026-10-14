"""Paginated client for the NYC 311 dataset on the Socrata (SODA 2.x) API.

Pages are read with keyset pagination on `(created_date, unique_key)` inside the fixed data
cut. Every page costs the same regardless of how far into the cut it is, and the position of
the last row read is a natural checkpoint for resuming.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from nyc311_bench.config import API_URL, CUT_END, CUT_START, DEFAULT_PAGE_SIZE, SOURCE_FIELDS

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_RETRIES = 5
BACKOFF_SECONDS = 2.0
TIMEOUT_SECONDS = 180.0
BODY_EXCERPT_CHARS = 300


class SocrataError(Exception):
    """The API rejected the request; retrying would not help."""


class SocrataUnavailable(SocrataError):
    """The API kept failing after every retry."""


@dataclass
class TransportError(Exception):
    """A failed HTTP exchange. `status` is None when no response was received."""

    status: int | None
    body: str = ""
    retry_after: float | None = None


@dataclass(frozen=True)
class Cursor:
    """Keyset position: the `(created_date, unique_key)` of the last row already read."""

    created_date: str
    unique_key: str

    def __post_init__(self) -> None:
        # Both values are interpolated into a SoQL predicate, so they are validated first.
        datetime.fromisoformat(self.created_date)
        if not self.unique_key.isdigit():
            raise ValueError(f"unique_key must be numeric, got {self.unique_key!r}")

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Cursor:
        return cls(created_date=row["created_date"], unique_key=row["unique_key"])


Transport = Callable[[str, dict[str, str], float], bytes]


def urllib_transport(url: str, headers: dict[str, str], timeout: float) -> bytes:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        retry_after = error.headers.get("Retry-After") if error.headers else None
        raise TransportError(
            status=error.code,
            body=error.read().decode("utf-8", errors="replace"),
            retry_after=float(retry_after) if retry_after and retry_after.isdigit() else None,
        ) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise TransportError(status=None, body=str(error)) from None


class SocrataClient:
    def __init__(
        self,
        app_token: str,
        *,
        url: str = API_URL,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_retries: int = MAX_RETRIES,
        backoff_seconds: float = BACKOFF_SECONDS,
        timeout: float = TIMEOUT_SECONDS,
        transport: Transport = urllib_transport,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if page_size < 1:
            raise ValueError("page_size must be at least 1")
        self._app_token = app_token
        self._url = url
        self.page_size = page_size
        self._max_retries = max_retries
        self._backoff_seconds = backoff_seconds
        self._timeout = timeout
        self._transport = transport
        self._sleep = sleep

    def build_url(self, cursor: Cursor | None, limit: int) -> str:
        where = (
            f"created_date >= '{CUT_START.isoformat()}' AND created_date < '{CUT_END.isoformat()}'"
        )
        if cursor is not None:
            where += (
                f" AND (created_date > '{cursor.created_date}'"
                f" OR (created_date = '{cursor.created_date}'"
                f" AND unique_key > '{cursor.unique_key}'))"
            )
        params = {
            "$select": ",".join(SOURCE_FIELDS),
            "$where": where,
            "$order": "created_date, unique_key",
            "$limit": str(limit),
        }
        return f"{self._url}?{urllib.parse.urlencode(params)}"

    def fetch_page(self, cursor: Cursor | None, limit: int | None = None) -> list[dict[str, str]]:
        """Return the rows that follow `cursor`, at most `limit` (default: the page size)."""
        url = self.build_url(cursor, min(limit or self.page_size, self.page_size))
        headers = {"X-App-Token": self._app_token, "Accept": "application/json"}

        for attempt in range(self._max_retries + 1):
            try:
                return json.loads(self._transport(url, headers, self._timeout))
            except TransportError as error:
                retryable = error.status is None or error.status in RETRYABLE_STATUSES
                if not retryable:
                    raise SocrataError(
                        f"The API rejected the request with HTTP {error.status}: "
                        f"{self._excerpt(error.body)}"
                    ) from None
                if attempt == self._max_retries:
                    reason = "no response" if error.status is None else f"HTTP {error.status}"
                    raise SocrataUnavailable(
                        f"The API still fails after {self._max_retries} retries ({reason}): "
                        f"{self._excerpt(error.body)}"
                    ) from None
                delay = self._backoff_seconds * 2**attempt
                self._sleep(max(delay, error.retry_after or 0.0))
        raise AssertionError("unreachable")

    def _excerpt(self, body: str) -> str:
        return body.replace(self._app_token, "***")[:BODY_EXCERPT_CHARS]
