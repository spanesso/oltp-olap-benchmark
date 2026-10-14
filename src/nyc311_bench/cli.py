"""Command-line interface: argument parsing, command dispatch and exit codes."""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

from nyc311_bench.config import (
    DEFAULT_PAGE_SIZE,
    PROFILES,
    ConfigError,
    Settings,
    get_profile,
    load_dotenv,
)
from nyc311_bench.runner import (
    DEFAULT_MEASURED_RUNS,
    DEFAULT_WARMUP_RUNS,
    MIN_MEASURED_RUNS,
    MIN_WARMUP_RUNS,
)

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_SOURCE_UNAVAILABLE = 3
EXIT_PARITY = 4

RESULTS_DIR = Path("results")


def _page_size(value: str) -> int:
    try:
        size = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an integer: {value!r}") from None
    if not 1 <= size <= DEFAULT_PAGE_SIZE:
        raise argparse.ArgumentTypeError(f"must be between 1 and {DEFAULT_PAGE_SIZE}")
    return size


def _at_least(minimum: int):
    def parse(value: str) -> int:
        try:
            number = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"not an integer: {value!r}") from None
        if number < minimum:
            raise argparse.ArgumentTypeError(f"must be at least {minimum}")
        return number

    return parse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="benchmark.py",
        description="OLTP vs OLAP benchmark on NYC 311 Service Requests.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    def add_profile(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--profile",
            choices=sorted(PROFILES),
            default="quick",
            help="data volume: quick = 200,000 requests, full = 5,000,000 (default: quick)",
        )

    load = commands.add_parser("load", help="download the data cut from the API into staging")
    add_profile(load)
    load.add_argument(
        "--page-size",
        type=_page_size,
        default=DEFAULT_PAGE_SIZE,
        help=f"rows per API request (default: {DEFAULT_PAGE_SIZE})",
    )

    build = commands.add_parser("build", help="rebuild the OLTP and OLAP models from staging")
    add_profile(build)

    def add_measurement(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--warmup",
            type=_at_least(MIN_WARMUP_RUNS),
            default=DEFAULT_WARMUP_RUNS,
            help=f"discarded runs per query and model (default: {DEFAULT_WARMUP_RUNS})",
        )
        command.add_argument(
            "--repetitions",
            type=_at_least(MIN_MEASURED_RUNS),
            default=DEFAULT_MEASURED_RUNS,
            help=f"measured runs per query and model (default: {DEFAULT_MEASURED_RUNS})",
        )

    def add_transactional(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--include-transactional",
            action="store_true",
            help="also measure the transactional operations (lookup by id, insert), reported "
            "apart from the analytical queries",
        )

    run = commands.add_parser("run", help="measure every query on both models")
    add_profile(run)
    add_measurement(run)
    add_transactional(run)

    experiments = commands.add_parser(
        "experiments",
        help="measure the schema and engine grid several times (does not change the "
        "benchmark_*.json/md result files)",
    )
    add_profile(experiments)
    add_measurement(experiments)
    experiments.add_argument(
        "--repeats",
        type=_at_least(2),
        default=3,
        help="times the whole grid is measured (default: 3)",
    )

    everything = commands.add_parser("all", help="load, build and run")
    add_profile(everything)
    add_measurement(everything)
    add_transactional(everything)
    everything.add_argument("--page-size", type=_page_size, default=DEFAULT_PAGE_SIZE)
    return parser


def _fail(message: str, code: int) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def _connect(settings: Settings):
    import psycopg

    try:
        return psycopg.connect(settings.postgres_conninfo(), autocommit=True, connect_timeout=10)
    except psycopg.OperationalError as error:
        raise ConnectionError(
            f"cannot connect to PostgreSQL at {settings.postgres_host}:{settings.postgres_port}. "
            f"Start it with `make up`. ({str(error).strip()})"
        ) from None


def command_load(args: argparse.Namespace, settings: Settings) -> int:
    from nyc311_bench.db import run_sql_file
    from nyc311_bench.ingest import format_summary, ingest
    from nyc311_bench.socrata import SocrataClient, SocrataError, SocrataUnavailable

    profile = get_profile(args.profile)
    # Checked before anything is requested from the API (FR-007).
    token = settings.require_app_token()
    client = SocrataClient(token, page_size=args.page_size)

    with _connect(settings) as connection:
        run_sql_file(connection, "staging/schema.sql")
        print(f"Loading profile '{profile.name}': target {profile.target_rows:,} requests.")
        try:
            summary = ingest(
                connection, client.fetch_page, profile.target_rows, page_size=args.page_size
            )
        except SocrataUnavailable as error:
            return _fail(
                f"{error}\nProgress is saved; run the same command again to resume.",
                EXIT_SOURCE_UNAVAILABLE,
            )
        except SocrataError as error:
            return _fail(str(error), EXIT_ERROR)
    print(format_summary(summary))
    if not summary.complete:
        return _fail(
            f"the data cut cannot provide {profile.target_rows:,} requests; "
            f"only {summary.rows_staged:,} are available.",
            EXIT_USAGE,
        )
    return EXIT_OK


def command_build(args: argparse.Namespace, settings: Settings) -> int:
    from nyc311_bench.olap import build_olap
    from nyc311_bench.oltp import build_oltp

    profile = get_profile(args.profile)
    with _connect(settings) as connection:
        staged = connection.execute(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'staging' AND table_name = 'service_request_raw'"
        ).fetchone()[0]
        if staged:
            staged = connection.execute(
                "SELECT count(*) FROM staging.service_request_raw"
            ).fetchone()[0]
        if staged < profile.target_rows:
            return _fail(
                f"staging holds {staged:,} requests but profile '{profile.name}' needs "
                f"{profile.target_rows:,}. Run `load --profile {profile.name}` first.",
                EXIT_USAGE,
            )

        print(f"Building both models for profile '{profile.name}'.")
        started = time.perf_counter()
        oltp_counts = build_oltp(connection, profile.target_rows)
        oltp_seconds = time.perf_counter() - started
        print(
            f"  OLTP (PostgreSQL): {oltp_counts['service_request']:,} requests "
            f"in {oltp_seconds:.1f}s"
        )

        started = time.perf_counter()
        olap_counts, method = build_olap(
            settings.olap_path, connection, settings.postgres_conninfo()
        )
        olap_seconds = time.perf_counter() - started
        print(
            f"  OLAP (DuckDB):     {olap_counts['fact_service_request']:,} requests "
            f"in {olap_seconds:.1f}s, copied via {method}"
        )

    if oltp_counts["service_request"] != olap_counts["fact_service_request"]:
        return _fail("the two models hold a different number of requests.", EXIT_PARITY)
    print("Both models hold the same number of requests.")
    return EXIT_OK


def command_run(args: argparse.Namespace, settings: Settings) -> int:
    from nyc311_bench.db import connect_duckdb
    from nyc311_bench.queries import QUERIES, TRANSACTIONAL_QUERIES
    from nyc311_bench.report import build_report, write_report
    from nyc311_bench.runner import (
        ParityError,
        check_parity,
        dataset_info,
        environment_info,
        run_queries,
        run_transactional,
    )

    profile = get_profile(args.profile)
    if not settings.olap_path.is_file():
        return _fail(
            f"the OLAP model file {settings.olap_path} does not exist. "
            f"Run `build --profile {profile.name}` first.",
            EXIT_PARITY,
        )

    with _connect(settings) as connection:
        duck = connect_duckdb(settings.olap_path, read_only=True)
        try:
            rows = check_parity(connection, duck, expected_rows=profile.target_rows)
            print(
                f"Measuring {len(QUERIES)} queries on {rows:,} requests "
                f"({args.warmup} warm-up, {args.repetitions} measured runs each)."
            )
            results = run_queries(
                connection, duck, QUERIES, warmup=args.warmup, repetitions=args.repetitions
            )
            report = build_report(
                profile,
                results,
                dataset_info(connection),
                environment_info(connection, duck),
                args.warmup,
                args.repetitions,
            )
        except ParityError as error:
            return _fail(f"{error}. Nothing was measured.", EXIT_PARITY)
        finally:
            duck.close()

        if args.include_transactional:
            # Analytical queries ran on a read-only handle. The T2 insert needs a writable one;
            # it opens only now, and every insert is rolled back.
            print("Measuring the transactional operations.")
            writable = connect_duckdb(settings.olap_path)
            try:
                transactional = run_transactional(
                    connection,
                    writable,
                    TRANSACTIONAL_QUERIES,
                    warmup=args.warmup,
                    repetitions=args.repetitions,
                )
            except ParityError as error:
                return _fail(f"{error}. Nothing was written.", EXIT_PARITY)
            finally:
                writable.close()
            report = build_report(
                profile,
                results + transactional,
                dataset_info(connection),
                report["environment"],
                args.warmup,
                args.repetitions,
            )

    json_path, markdown_path = write_report(report, RESULTS_DIR)
    verdict = report["significance"]
    print(f"Results written to {json_path} and {markdown_path}.")
    print(
        f"{verdict['queries_meeting_3x']} of {verdict['analytical_queries']} analytical queries "
        "are at least 3x faster on the OLAP model."
    )
    if not verdict["evaluated"]:
        print("Quick profile: these are not the official timings.")
    elif verdict["reached"]:
        print("Significance threshold reached.")
    else:
        print("Significance threshold NOT reached. Nothing was changed to reach it.")
    return EXIT_OK


def command_experiments(args: argparse.Namespace, settings: Settings) -> int:
    from nyc311_bench import experiments
    from nyc311_bench.controls import build_3nf_in_duckdb, build_star_in_postgres
    from nyc311_bench.db import connect_duckdb
    from nyc311_bench.queries import QUERIES
    from nyc311_bench.runner import ParityError, check_parity, dataset_info, environment_info

    profile = get_profile(args.profile)
    normalized_path = settings.olap_path.with_name("control_3nf.duckdb")
    if not settings.olap_path.is_file():
        return _fail(
            f"the OLAP model file {settings.olap_path} does not exist. "
            f"Run `build --profile {profile.name}` first.",
            EXIT_PARITY,
        )

    with _connect(settings) as connection:
        duck = connect_duckdb(settings.olap_path, read_only=True)
        try:
            rows = check_parity(connection, duck, expected_rows=profile.target_rows)
            print(f"Both models hold {rows:,} requests.")
            # Rebuilt every time (about 25 s): a control model can never be stale, partial or
            # built from other data than the OLTP model it is compared with.
            print("Building the star schema in PostgreSQL ...")
            build_star_in_postgres(connection)
            print("Building the normalized schema in DuckDB ...")
            build_3nf_in_duckdb(normalized_path, connection, settings.postgres_conninfo())

            normalized = connect_duckdb(normalized_path, read_only=True)
            try:
                print(
                    f"Measuring {len(QUERIES)} queries on 4 models, {args.repeats} repetitions "
                    f"({args.warmup} warm-up, {args.repetitions} measured runs each)."
                )
                raw = experiments.run_grid(
                    connection,
                    duck,
                    normalized,
                    QUERIES,
                    repeats=args.repeats,
                    warmup=args.warmup,
                    repetitions=args.repetitions,
                )
                report = experiments.build_report(
                    profile,
                    raw,
                    dataset_info(connection),
                    environment_info(connection, duck),
                )
            finally:
                normalized.close()
        except (ParityError, experiments.EquivalenceError) as error:
            return _fail(f"{error}. Nothing was measured.", EXIT_PARITY)
        finally:
            duck.close()

    json_path, markdown_path = experiments.write_report(report, RESULTS_DIR)
    print(f"Results written to {json_path} and {markdown_path}.")
    return EXIT_OK


def command_all(args: argparse.Namespace, settings: Settings) -> int:
    for command in (command_load, command_build, command_run):
        code = command(args, settings)
        if code != EXIT_OK:
            return code
    return EXIT_OK


COMMANDS = {
    "load": command_load,
    "build": command_build,
    "run": command_run,
    "experiments": command_experiments,
    "all": command_all,
}


def main(argv: Sequence[str] | None = None, env: Mapping[str, str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if env is None:
        load_dotenv()
        env = os.environ
    try:
        settings = Settings.from_env(env)
        return COMMANDS[args.command](args, settings)
    except ConfigError as error:
        return _fail(str(error), EXIT_USAGE)
    except ConnectionError as error:
        return _fail(str(error), EXIT_ERROR)
    except KeyboardInterrupt:
        return _fail("interrupted. Progress is saved; run the same command to resume.", 130)
