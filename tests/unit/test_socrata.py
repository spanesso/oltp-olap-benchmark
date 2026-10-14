import json
import urllib.parse

import pytest

from nyc311_bench.socrata import (
    Cursor,
    SocrataClient,
    SocrataError,
    SocrataUnavailable,
    TransportError,
)

TOKEN = "s3cret-token"
ROWS = [{"unique_key": "10000001", "created_date": "2024-01-01T00:00:00.000"}]


class FakeTransport:
    """Replays a scripted list of responses: bytes to return or TransportError to raise."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, headers, timeout):
        self.calls.append((url, headers))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def make_client(transport, **kwargs):
    sleeps = []
    client = SocrataClient(TOKEN, transport=transport, sleep=sleeps.append, **kwargs)
    return client, sleeps


def query_of(url):
    return {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(url).query).items()}


def test_first_page_filters_by_the_cut_and_orders_by_the_keyset():
    client, _ = make_client(FakeTransport())
    query = query_of(client.build_url(None, 500))
    assert query["$limit"] == "500"
    assert query["$order"] == "created_date, unique_key"
    assert query["$select"].split(",")[0] == "unique_key"
    assert len(query["$select"].split(",")) == 12
    assert query["$where"] == (
        "created_date >= '2024-01-01T00:00:00' AND created_date < '2026-01-01T00:00:00'"
    )


def test_next_page_adds_the_compound_keyset_predicate():
    client, _ = make_client(FakeTransport())
    cursor = Cursor("2024-01-01T02:03:31.000", "59897707")
    where = query_of(client.build_url(cursor, 500))["$where"]
    assert where.endswith(
        "AND (created_date > '2024-01-01T02:03:31.000' OR "
        "(created_date = '2024-01-01T02:03:31.000' AND unique_key > '59897707'))"
    )


@pytest.mark.parametrize(
    ("created_date", "unique_key"),
    [("2024-01-01T00:00:00.000", "1' OR '1'='1"), ("not-a-date", "123"), ("2024-01-01", "")],
)
def test_cursor_rejects_values_that_are_not_safe_to_interpolate(created_date, unique_key):
    with pytest.raises(ValueError):
        Cursor(created_date, unique_key)


def test_fetch_page_returns_rows_and_sends_the_token_as_a_header_only():
    transport = FakeTransport(json.dumps(ROWS).encode())
    client, sleeps = make_client(transport)
    assert client.fetch_page(None) == ROWS
    url, headers = transport.calls[0]
    assert headers["X-App-Token"] == TOKEN
    assert TOKEN not in url
    assert sleeps == []


def test_limit_never_exceeds_the_page_size():
    transport = FakeTransport(b"[]", b"[]")
    client, _ = make_client(transport, page_size=100)
    client.fetch_page(None, limit=5000)
    client.fetch_page(None, limit=40)
    assert [query_of(url)["$limit"] for url, _ in transport.calls] == ["100", "40"]


def test_an_empty_page_is_returned_as_an_empty_list():
    client, _ = make_client(FakeTransport(b"[]"))
    assert client.fetch_page(None) == []


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504, None])
def test_temporary_failures_are_retried_with_exponential_backoff(status):
    failure = TransportError(status=status, body="busy")
    transport = FakeTransport(failure, failure, json.dumps(ROWS).encode())
    client, sleeps = make_client(transport)
    assert client.fetch_page(None) == ROWS
    assert sleeps == [2.0, 4.0]
    assert len(transport.calls) == 3


def test_retry_after_is_honored_when_longer_than_the_backoff():
    transport = FakeTransport(
        TransportError(status=429, body="slow down", retry_after=30.0), json.dumps(ROWS).encode()
    )
    client, sleeps = make_client(transport)
    client.fetch_page(None)
    assert sleeps == [30.0]


def test_gives_up_after_the_configured_retries():
    failure = TransportError(status=503, body="down")
    transport = FakeTransport(*[failure] * 6)
    client, sleeps = make_client(transport)
    with pytest.raises(SocrataUnavailable, match="after 5 retries"):
        client.fetch_page(None)
    assert sleeps == [2.0, 4.0, 8.0, 16.0, 32.0]
    assert len(transport.calls) == 6


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_client_errors_are_not_retried(status):
    transport = FakeTransport(TransportError(status=status, body="bad request"))
    client, sleeps = make_client(transport)
    with pytest.raises(SocrataError, match=f"HTTP {status}") as raised:
        client.fetch_page(None)
    assert not isinstance(raised.value, SocrataUnavailable)
    assert sleeps == []
    assert len(transport.calls) == 1


def test_the_token_never_appears_in_error_messages():
    transport = FakeTransport(TransportError(status=403, body=f"invalid token {TOKEN}"))
    client, _ = make_client(transport)
    with pytest.raises(SocrataError) as raised:
        client.fetch_page(None)
    assert TOKEN not in str(raised.value)
    assert "***" in str(raised.value)


def test_page_size_must_be_positive():
    with pytest.raises(ValueError):
        SocrataClient(TOKEN, page_size=0)
