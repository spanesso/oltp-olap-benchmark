"""Compare the result of one query on both models, row by row (contracts/queries.md)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from nyc311_bench.queries import Query

RELATIVE_TOLERANCE = 1e-9
ABSOLUTE_TOLERANCE = 1e-12


def values_match(oltp_value: Any, olap_value: Any) -> bool:
    """Exact match for text and integers; relative tolerance for floating point."""
    if oltp_value is None or olap_value is None:
        return oltp_value is None and olap_value is None
    if isinstance(oltp_value, bool) or isinstance(olap_value, bool):
        return oltp_value is olap_value
    if isinstance(oltp_value, float) or isinstance(olap_value, float):
        if not isinstance(oltp_value, int | float) or not isinstance(olap_value, int | float):
            return False
        return math.isclose(
            oltp_value, olap_value, rel_tol=RELATIVE_TOLERANCE, abs_tol=ABSOLUTE_TOLERANCE
        )
    return type(oltp_value) is type(olap_value) and oltp_value == olap_value


def assert_equivalent(
    query_id: str, oltp_rows: Sequence[Sequence[Any]], olap_rows: Sequence[Sequence[Any]]
) -> None:
    """Fail with the query, the first differing row and the column that differs."""
    if len(oltp_rows) != len(olap_rows):
        raise AssertionError(
            f"{query_id}: OLTP returns {len(oltp_rows)} rows and OLAP returns {len(olap_rows)}"
        )
    for index, (oltp_row, olap_row) in enumerate(zip(oltp_rows, olap_rows, strict=True)):
        if len(oltp_row) != len(olap_row):
            raise AssertionError(
                f"{query_id}: row {index} has {len(oltp_row)} columns on OLTP "
                f"and {len(olap_row)} on OLAP"
            )
        for column, (oltp_value, olap_value) in enumerate(zip(oltp_row, olap_row, strict=True)):
            if not values_match(oltp_value, olap_value):
                raise AssertionError(
                    f"{query_id}: row {index}, column {column} differs: "
                    f"OLTP {oltp_value!r} ({type(oltp_value).__name__}) vs "
                    f"OLAP {olap_value!r} ({type(olap_value).__name__})\n"
                    f"  OLTP row: {tuple(oltp_row)!r}\n  OLAP row: {tuple(olap_row)!r}"
                )


def run_on_both(postgres, duck, query: Query) -> tuple[list[tuple], list[tuple]]:
    oltp_rows = postgres.execute(query.sql("oltp")).fetchall()
    olap_rows = duck.execute(query.sql("olap")).fetchall()
    return oltp_rows, olap_rows
