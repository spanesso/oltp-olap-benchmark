# Quickstart: OLTP vs OLAP Benchmark on NYC 311

How to validate the feature end to end once it is implemented. Commands are defined in
[contracts/cli.md](./contracts/cli.md).

## Prerequisites

- Docker Desktop running.
- Python 3.12 or later.
- A free Socrata app token from NYC Open Data, exported as `SOCRATA_APP_TOKEN` (or placed in
  `.env`, copied from `.env.example`).

## Read the official results without running anything (SC-009)

Open `results/benchmark_full.md`.

## Quick profile: verify everything works (SC-001, SC-008)

```bash
make up                      # start PostgreSQL 17 on port 5433
make install                 # create .venv and install dependencies
make bench PROFILE=quick     # load 200,000 requests, build both models, measure
make test                    # unit and integration tests
```

Expected:

- `make bench` ends with exit code 0 and prints equal row counts for both models.
- `results/benchmark_quick.md` exists and warns that its timings are not official.
- `make test` passes.
- The whole sequence takes under 10 minutes.

## Full profile: reproduce the official numbers (SC-002, SC-003)

```bash
make bench PROFILE=full
```

Expected: download and load of 5,000,000 requests in under 1 hour, then
`results/benchmark_full.md` with the significance verdict.

## Checks for specific requirements

| Check | How | Expected |
|---|---|---|
| Idempotent load (FR-004, SC-005) | run `make bench PROFILE=quick` twice | second run downloads nothing; row counts unchanged |
| Resumable load (FR-005) | interrupt `python benchmark.py load --profile full` with Ctrl-C, run it again | it continues from the checkpoint, not from zero |
| Missing credential (FR-007) | unset `SOCRATA_APP_TOKEN`, run `load` | exit code 2 and a clear message, no request sent |
| Parity guard (FR-018) | delete one row from the OLAP fact table, run `run` | exit code 4, nothing measured |
| Equivalence (FR-022, SC-004) | `pytest tests/integration` | every query returns the same rows on both models |
| Repeatability (SC-006) | run `python benchmark.py run --profile full` twice | medians differ by less than 20% per query and model |
