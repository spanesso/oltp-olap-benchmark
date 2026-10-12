from pathlib import Path

import pytest

from nyc311_bench.config import (
    CUT_END,
    CUT_START,
    MIN_TARGET_ROWS,
    PROFILES,
    SOURCE_FIELDS,
    ConfigError,
    Settings,
    get_profile,
    load_dotenv,
)


def test_profiles_match_the_spec():
    assert get_profile("quick").target_rows == 200_000
    assert get_profile("full").target_rows == 5_000_000
    assert get_profile("full").official is True
    assert get_profile("quick").official is False
    assert all(p.target_rows >= MIN_TARGET_ROWS for p in PROFILES.values())


def test_unknown_profile_is_rejected():
    with pytest.raises(ConfigError, match="Unknown profile"):
        get_profile("huge")


def test_cut_is_a_closed_past_range():
    assert CUT_START < CUT_END
    assert (CUT_START.year, CUT_END.year) == (2024, 2026)


def test_source_fields_are_the_twelve_used_columns():
    assert len(SOURCE_FIELDS) == 12
    assert SOURCE_FIELDS[0] == "unique_key"


def test_defaults_match_docker_compose():
    settings = Settings.from_env({})
    assert settings.postgres_port == 5433
    assert settings.postgres_user == "bench"
    assert settings.postgres_db == "bench"
    assert settings.olap_path == Path("data/olap.duckdb")
    assert settings.app_token is None


def test_environment_overrides_defaults():
    settings = Settings.from_env(
        {"POSTGRES_PORT": "6000", "OLAP_PATH": "/tmp/x.duckdb", "SOCRATA_APP_TOKEN": "abc"}
    )
    assert settings.postgres_port == 6000
    assert settings.olap_path == Path("/tmp/x.duckdb")
    assert settings.app_token == "abc"


def test_invalid_port_is_rejected():
    with pytest.raises(ConfigError, match="POSTGRES_PORT"):
        Settings.from_env({"POSTGRES_PORT": "not-a-number"})


def test_missing_token_raises_a_clear_error():
    with pytest.raises(ConfigError, match="SOCRATA_APP_TOKEN"):
        Settings.from_env({}).require_app_token()


def test_empty_token_counts_as_missing():
    assert Settings.from_env({"SOCRATA_APP_TOKEN": ""}).app_token is None


def test_secrets_never_appear_in_repr():
    settings = Settings.from_env({"SOCRATA_APP_TOKEN": "s3cret-token", "POSTGRES_PASSWORD": "pw"})
    assert "s3cret-token" not in repr(settings)
    assert "pw" not in repr(settings)


def test_conninfo_targets_the_requested_database():
    settings = Settings.from_env({})
    assert "dbname=bench" in settings.postgres_conninfo()
    assert "dbname=other" in settings.postgres_conninfo("other")


def test_load_dotenv_reads_values_without_overriding(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nSOCRATA_APP_TOKEN='from-file'\nPOSTGRES_PORT=7000\n\nnoise\n")
    env = {"POSTGRES_PORT": "5433"}
    load_dotenv(env_file, env)
    assert env == {"POSTGRES_PORT": "5433", "SOCRATA_APP_TOKEN": "from-file"}


def test_load_dotenv_ignores_a_missing_file(tmp_path):
    env: dict[str, str] = {}
    load_dotenv(tmp_path / "absent.env", env)
    assert env == {}
