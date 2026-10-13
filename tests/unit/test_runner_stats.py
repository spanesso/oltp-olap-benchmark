import pytest

from nyc311_bench.queries import ANALYTICAL, Query
from nyc311_bench.runner import (
    QueryResult,
    percentile,
    summarize,
    time_query,
    validate_runs,
)


class FakeClock:
    """Each measured run reads the clock twice; durations are given in milliseconds."""

    def __init__(self, durations_ms):
        self.ticks = []
        now = 0.0
        for duration in durations_ms:
            self.ticks += [now, now + duration / 1000.0]
            now += 1.0

    def __call__(self):
        return self.ticks.pop(0)


def test_summary_statistics_on_known_values():
    timing = summarize([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    assert timing.median_ms == 55.0
    assert timing.min_ms == 10.0
    assert timing.max_ms == 100.0
    assert timing.p95_ms == pytest.approx(95.5)
    assert len(timing.runs_ms) == 10


def test_median_resists_an_outlier():
    assert summarize([10.0] * 9 + [5000.0]).median_ms == 10.0


@pytest.mark.parametrize(
    ("values", "percent", "expected"),
    [([1.0, 2.0, 3.0, 4.0, 5.0], 50, 3.0), ([1.0, 2.0], 50, 1.5), ([7.0], 95, 7.0)],
)
def test_percentile_interpolates_linearly(values, percent, expected):
    assert percentile(values, percent) == pytest.approx(expected)


def test_percentile_needs_values():
    with pytest.raises(ValueError):
        percentile([], 95)


def test_warmup_runs_are_executed_but_not_measured():
    calls = []
    durations = [float(n) for n in range(1, 11)]
    timing, rows = time_query(
        lambda: calls.append(1) or [("row",)] * 3, 2, 10, clock=FakeClock(durations)
    )
    assert len(calls) == 12
    assert rows == 3
    assert timing.runs_ms == pytest.approx(durations)


@pytest.mark.parametrize(("warmup", "repetitions"), [(0, 10), (1, 9), (-1, 10), (1, 0)])
def test_too_few_runs_are_rejected(warmup, repetitions):
    with pytest.raises(ValueError):
        validate_runs(warmup, repetitions)
    with pytest.raises(ValueError):
        time_query(lambda: [], warmup, repetitions)


def test_minimum_runs_are_accepted():
    validate_runs(1, 10)


def test_speedup_is_oltp_median_over_olap_median():
    query = Query("q", ANALYTICAL, "question?")
    result = QueryResult(query, 1, summarize([300.0] * 10), summarize([100.0] * 10))
    assert result.speedup == 3.0
