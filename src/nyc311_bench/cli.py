"""Command-line interface: argument parsing, command dispatch and exit codes."""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections.abc import Mapping, Sequence

from nyc311_bench.config import (
    DEFAULT_PAGE_SIZE,
    PROFILES,
    ConfigError,
    Settings,
    get_profile,
    load_dotenv,
)

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_SOURCE_UNAVAILABLE = 3
EXIT_PARITY = 4


def _page_size(value: str) -> int:
    try:
        size = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an integer: {value!r}") from None
    if not 1 <= size <= DEFAULT_PAGE_SIZE:
        raise argparse.ArgumentTypeError(f"must be between 1 and {DEFAULT_PAGE_SIZE}")
    return size


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


COMMANDS = {"load": command_load, "build": command_build}


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
