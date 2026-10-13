"""Stand-in for the API in integration tests: serves the fixture with keyset semantics."""

from __future__ import annotations

from nyc311_bench.socrata import Cursor, SocrataUnavailable


class FixtureSource:
    """Serves rows in file order. A cursor resumes after the row it points to."""

    def __init__(self, rows: list[dict[str, str]], fail_on_call: int | None = None) -> None:
        self.rows = rows
        self.fail_on_call = fail_on_call
        self.calls = 0

    def __call__(self, cursor: Cursor | None, limit: int) -> list[dict[str, str]]:
        self.calls += 1
        if self.calls == self.fail_on_call:
            raise SocrataUnavailable("simulated outage")
        start = 0
        if cursor is not None:
            start = 1 + next(
                index
                for index, row in enumerate(self.rows)
                if row.get("unique_key") == cursor.unique_key
                and row.get("created_date") == cursor.created_date
            )
        return self.rows[start : start + limit]
