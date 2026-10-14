"""Registry of benchmark queries: each one is a business question with a SQL file per model."""

from __future__ import annotations

from dataclasses import dataclass

from nyc311_bench.db import read_sql

ANALYTICAL = "analytical"
TRANSACTIONAL = "transactional"
MODELS = ("oltp", "olap")


@dataclass(frozen=True)
class Query:
    id: str
    group: str
    question: str

    def sql(self, model: str) -> str:
        if model not in MODELS:
            raise ValueError(f"Unknown model {model!r}. Valid models: {', '.join(MODELS)}.")
        return read_sql(f"{model}/{self.id}.sql")


QUERIES: tuple[Query, ...] = (
    Query(
        "q1_volume_by_type_month_borough",
        ANALYTICAL,
        "How many requests of each complaint type were created per month in each borough?",
    ),
    Query(
        "q2_top_types_per_zip",
        ANALYTICAL,
        "For each ZIP code, which are the 10 most frequent complaint types and how long do "
        "they take to resolve on average?",
    ),
    Query(
        "q3_closure_rate_agency_channel",
        ANALYTICAL,
        "What share of requests does each agency close within 30 days, by channel?",
    ),
    Query(
        "q4_resolution_p90_agency_quarter",
        ANALYTICAL,
        "What is the 90th percentile of resolution time per agency and quarter?",
    ),
    Query(
        "q5_noise_by_weekday_hour",
        ANALYTICAL,
        "In Brooklyn, when do noise complaints concentrate, by day of week and hour?",
    ),
    Query(
        "q6_channel_share_by_quarter",
        ANALYTICAL,
        "How is each quarter's volume split across channels?",
    ),
)


# Optional group (User Story 4): measured only with --include-transactional and never counted
# in the significance verdict. They show the side of the trade-off where OLTP wins.
TRANSACTIONAL_QUERIES: tuple[Query, ...] = (
    Query(
        "t1_lookup_by_id",
        TRANSACTIONAL,
        "Read one request by its identifier, with all its descriptive attributes.",
    ),
    Query(
        "t2_insert_request",
        TRANSACTIONAL,
        "Register one new request (insert inside a transaction that is rolled back, so the "
        "commit itself is not measured).",
    ),
)


def analytical_queries() -> tuple[Query, ...]:
    return tuple(query for query in QUERIES if query.group == ANALYTICAL)
