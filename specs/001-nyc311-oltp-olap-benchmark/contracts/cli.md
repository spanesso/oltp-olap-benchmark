# Contract: Command-Line Interface

The project exposes one entry point, `benchmark.py` at the repository root (the "benchmark
script" deliverable), which delegates to the `nyc311_bench` package. The `Makefile` wraps
the same commands so the README stays within five commands (SC-001).

## Configuration (environment variables)

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SOCRATA_APP_TOKEN` | for `load` | none | API credential (FR-007). Never logged. |
| `POSTGRES_HOST` / `POSTGRES_PORT` | no | `localhost` / `5433` | OLTP connection |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | no | `bench` | match `docker-compose.yml` |
| `OLAP_PATH` | no | `data/olap.duckdb` | analytical model file (git-ignored) |

A `.env.example` documents them; `.env` is git-ignored.

## Commands

```text
python benchmark.py load  --profile {quick|full} [--page-size N]
python benchmark.py build --profile {quick|full}
python benchmark.py run   --profile {quick|full} [--warmup N] [--repetitions N]
                          [--include-transactional]
python benchmark.py experiments --profile {quick|full} [--repeats N] [--warmup N] [--repetitions N]
python benchmark.py all   --profile {quick|full} [--include-transactional]
```

| Command | Does | Requirements |
|---|---|---|
| `load` | Downloads the cut from the API into staging until the profile's target is staged. Resumes from the checkpoint; does nothing if the target is already staged. | FR-001 to FR-008 |
| `build` | Rebuilds the OLTP model from the first N staged rows, then the OLAP model from the OLTP model. Runs `ANALYZE`. Prints row counts for both. | FR-009 to FR-012 |
| `run` | Checks parity of row counts, measures every query on both models, writes the results files. With `--include-transactional` it also measures T1 and T2; the analytical queries use a read-only handle on the OLAP file and only T2 opens it for writing (every insert is rolled back). | FR-013 to FR-019, FR-026 |
| `experiments` | Rebuilds the two control models, verifies that the four models return the same rows, measures the grid `--repeats` times (default 3, minimum 2) and writes `results/experiments_<profile>.json` and `.md`. Does not change `benchmark_<profile>.*`. | FR-027, FR-028 |
| `all` | `load`, then `build`, then `run`. | |

Defaults: `--profile quick`, `--page-size 50000`, `--warmup 1`, `--repetitions 10`.
`--warmup` below 1 or `--repetitions` below 10 is rejected (FR-015).

## Output and exit codes

Progress and summaries go to standard output; errors go to standard error.

| Exit code | Meaning |
|---|---|
| 0 | Success. For `run`, this includes the case where the significance threshold is not reached: the report states it (FR-019). |
| 1 | Unexpected error. |
| 2 | Invalid arguments or configuration, including a missing `SOCRATA_APP_TOKEN` for `load` (reported before any request is sent), a target the data cut cannot provide, and `build` when staging holds fewer rows than the profile needs. |
| 3 | The source API kept failing after the retries were exhausted. Progress is kept; rerun to resume. |
| 4 | Parity check failed: a model is empty, the row counts differ, or they do not match the profile. Nothing is measured (FR-018). |
| 130 | Interrupted with Ctrl-C. Progress is kept; rerun to resume. |

## Retry policy for `load` (FR-006)

- HTTP 429 and 5xx, timeouts and connection errors: retry up to 5 times with exponential
  backoff starting at 2 seconds, honoring `Retry-After` when present.
- Other 4xx: no retry; stop with the response status and body excerpt (token redacted).
- An empty or short page before the target is reached ends the load with a warning stating
  how many rows the cut actually holds, and exit code 2.

## Makefile targets

| Target | Runs |
|---|---|
| `make up` | `docker compose up -d --wait` |
| `make install` | creates `.venv` and installs the package with dev dependencies |
| `make bench PROFILE=quick` | `python benchmark.py all --profile $(PROFILE)` |
| `make test` | `pytest` |
| `make lint` | `ruff check` and `ruff format --check` |
