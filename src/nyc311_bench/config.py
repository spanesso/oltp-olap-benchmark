"""Settings, volume profiles and the fixed data cut."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

DATASET_ID = "erm2-nwe9"
DATASET_NAME = "NYC 311 Service Requests (erm2-nwe9)"
API_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"

# Creation-date range the benchmark reads, in ascending (created_date, unique_key) order.
# It ended months ago, so its rows no longer change between two loads (FR-003).
CUT_START = datetime(2024, 1, 1)
CUT_END = datetime(2026, 1, 1)

DEFAULT_PAGE_SIZE = 50_000
MIN_TARGET_ROWS = 100_000

SOURCE_FIELDS = (
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "borough",
    "incident_zip",
    "community_board",
    "open_data_channel_type",
    "status",
)


class ConfigError(Exception):
    """Invalid or missing configuration."""


@dataclass(frozen=True)
class Profile:
    name: str
    target_rows: int
    official: bool


PROFILES: dict[str, Profile] = {
    "quick": Profile(name="quick", target_rows=200_000, official=False),
    "full": Profile(name="full", target_rows=5_000_000, official=True),
}


def get_profile(name: str) -> Profile:
    try:
        return PROFILES[name]
    except KeyError:
        valid = ", ".join(sorted(PROFILES))
        raise ConfigError(f"Unknown profile {name!r}. Valid profiles: {valid}.") from None


@dataclass(frozen=True)
class Settings:
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_user: str = "bench"
    postgres_password: str = field(default="bench", repr=False)
    postgres_db: str = "bench"
    olap_path: Path = Path("data/olap.duckdb")
    app_token: str | None = field(default=None, repr=False)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        env = os.environ if env is None else env
        port = env.get("POSTGRES_PORT", "5433")
        try:
            postgres_port = int(port)
        except ValueError:
            raise ConfigError(f"POSTGRES_PORT must be an integer, got {port!r}.") from None
        return cls(
            postgres_host=env.get("POSTGRES_HOST", "localhost"),
            postgres_port=postgres_port,
            postgres_user=env.get("POSTGRES_USER", "bench"),
            postgres_password=env.get("POSTGRES_PASSWORD", "bench"),
            postgres_db=env.get("POSTGRES_DB", "bench"),
            olap_path=Path(env.get("OLAP_PATH", "data/olap.duckdb")),
            app_token=env.get("SOCRATA_APP_TOKEN") or None,
        )

    def require_app_token(self) -> str:
        if not self.app_token:
            raise ConfigError(
                "SOCRATA_APP_TOKEN is not set. Create a free app token at "
                "https://data.cityofnewyork.us (Developer Settings) and export it or put it "
                "in .env before running `load`."
            )
        return self.app_token

    def postgres_conninfo(self, dbname: str | None = None) -> str:
        return (
            f"host={self.postgres_host} port={self.postgres_port} "
            f"user={self.postgres_user} password={self.postgres_password} "
            f"dbname={dbname or self.postgres_db}"
        )


def load_dotenv(path: Path = Path(".env"), env: dict[str, str] | None = None) -> None:
    """Read KEY=VALUE lines from a .env file without overriding existing variables."""
    target = os.environ if env is None else env
    if not path.is_file():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        target.setdefault(key.strip(), value.strip().strip("'\""))
