import pytest

from nyc311_bench import cli


def test_load_without_a_token_fails_before_any_request(capsys):
    code = cli.main(["load", "--profile", "quick"], env={})
    assert code == cli.EXIT_USAGE
    assert "SOCRATA_APP_TOKEN is not set" in capsys.readouterr().err


def test_an_empty_token_counts_as_missing(capsys):
    assert cli.main(["load"], env={"SOCRATA_APP_TOKEN": ""}) == cli.EXIT_USAGE


def test_invalid_configuration_is_a_usage_error(capsys):
    code = cli.main(["build"], env={"POSTGRES_PORT": "abc"})
    assert code == cli.EXIT_USAGE
    assert "POSTGRES_PORT" in capsys.readouterr().err


def test_an_unreachable_database_is_reported_with_a_hint(capsys):
    env = {"POSTGRES_HOST": "127.0.0.1", "POSTGRES_PORT": "1", "SOCRATA_APP_TOKEN": "t0ken"}
    code = cli.main(["load"], env=env)
    captured = capsys.readouterr().err
    assert code == cli.EXIT_ERROR
    assert "make up" in captured
    assert "t0ken" not in captured


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["unknown-command"],
        ["load", "--profile", "huge"],
        ["load", "--page-size", "0"],
        ["load", "--page-size", "50001"],
        ["load", "--page-size", "many"],
        ["build", "--page-size", "10"],
    ],
)
def test_invalid_arguments_exit_with_code_2(argv, capsys):
    with pytest.raises(SystemExit) as raised:
        cli.main(argv, env={})
    assert raised.value.code == cli.EXIT_USAGE


def test_profile_defaults_to_quick():
    args = cli.build_parser().parse_args(["load"])
    assert args.profile == "quick"
    assert args.page_size == 50_000


def test_exit_codes_match_the_contract():
    assert (
        cli.EXIT_OK,
        cli.EXIT_ERROR,
        cli.EXIT_USAGE,
        cli.EXIT_SOURCE_UNAVAILABLE,
        cli.EXIT_PARITY,
    ) == (0, 1, 2, 3, 4)


@pytest.mark.parametrize(
    "argv",
    [
        ["run", "--warmup", "0"],
        ["run", "--repetitions", "9"],
        ["run", "--repetitions", "ten"],
        ["all", "--repetitions", "1"],
    ],
)
def test_too_few_measurement_runs_exit_with_code_2(argv, capsys):
    with pytest.raises(SystemExit) as raised:
        cli.main(argv, env={})
    assert raised.value.code == cli.EXIT_USAGE


def test_measurement_defaults_match_the_spec():
    args = cli.build_parser().parse_args(["run"])
    assert (args.warmup, args.repetitions, args.profile) == (1, 10, "quick")


def test_all_stops_at_the_first_failing_step(capsys):
    assert cli.main(["all"], env={}) == cli.EXIT_USAGE
    assert "SOCRATA_APP_TOKEN" in capsys.readouterr().err


def test_experiments_accepts_a_profile_and_repeats():
    args = cli.build_parser().parse_args(["experiments", "--profile", "full", "--repeats", "4"])
    assert (args.command, args.profile, args.repeats) == ("experiments", "full", 4)


def test_experiments_needs_at_least_two_repeats():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["experiments", "--repeats", "1"])


def test_include_transactional_is_available_on_run_and_all():
    parser = cli.build_parser()
    assert parser.parse_args(["run", "--include-transactional"]).include_transactional is True
    assert parser.parse_args(["all", "--include-transactional"]).include_transactional is True
    assert parser.parse_args(["run"]).include_transactional is False
