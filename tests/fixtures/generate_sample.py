"""Generate the synthetic test fixture `sample_311.json`.

The rows imitate the shape of the NYC 311 API response (every value is a string and keys
with no value are omitted) but none of them is real data. The output is deterministic:
running this script again reproduces the committed file byte for byte.

Usage: python tests/fixtures/generate_sample.py
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 311
VALID_ROWS = 2000
START = datetime(2024, 1, 1)
SPAN_DAYS = 540  # about 18 months, so period queries have several groups

AGENCIES = {
    "NYPD": ["New York City Police Department"],
    "HPD": ["Department of Housing Preservation and Development"],
    "DSNY": ["Department of Sanitation"],
    "DOT": ["Department of Transportation"],
    # Two names for one code, to exercise the (code, name) key of the agency table.
    "DOHMH": ["Department of Health and Mental Hygiene", "Dept of Health and Mental Hygiene"],
}

COMPLAINTS = {
    "NYPD": {
        "Noise - Residential": ["Loud Music/Party", "Banging/Pounding", "Loud Talking"],
        "Noise - Street/Sidewalk": ["Loud Music/Party", "Loud Talking"],
        "Illegal Parking": ["Blocked Hydrant", "Double Parked", "Posted Parking Sign Violation"],
        "Blocked Driveway": ["No Access", "Partial Access"],
    },
    "HPD": {
        "HEAT/HOT WATER": ["ENTIRE BUILDING", "APARTMENT ONLY"],
        "PLUMBING": ["WATER SUPPLY", "TOILET"],
        "PAINT/PLASTER": ["CEILING", "WALL"],
    },
    "DSNY": {
        "Dirty Condition": ["Trash", "Litter"],
        "Missed Collection": ["Trash", "Recycling"],
        "Illegal Dumping": ["Chronic Dumping", "Removal Request"],
    },
    "DOT": {
        "Street Condition": ["Pothole", "Cave-in"],
        "Street Light Condition": ["Street Light Out", "Street Light Cycling"],
        "Traffic Signal Condition": ["Controller", "Pedestrian Signal"],
    },
    "DOHMH": {
        "Rodent": ["Rat Sighting", "Mouse Sighting"],
        "Food Establishment": ["Rodents/Insects/Garbage", "Food Temperature"],
    },
}

LOCATIONS = {
    "BROOKLYN": (["11201", "11206", "11215", "11226"], ["01 BROOKLYN", "06 BROOKLYN"]),
    "QUEENS": (["11354", "11377", "11432"], ["02 QUEENS", "07 QUEENS"]),
    "MANHATTAN": (["10001", "10025", "10032"], ["04 MANHATTAN", "12 MANHATTAN"]),
    "BRONX": (["10451", "10467"], ["01 BRONX", "07 BRONX"]),
    "STATEN ISLAND": (["10301", "10314"], ["01 STATEN ISLAND"]),
    "Unspecified": (["10000"], ["0 Unspecified"]),
}
BOROUGH_WEIGHTS = [30, 24, 20, 20, 5, 1]

CHANNELS = ["ONLINE", "PHONE", "MOBILE", "UNKNOWN", "OTHER"]
CHANNEL_WEIGHTS = [42, 30, 20, 7, 1]


def timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.000")


def build_row(rng: random.Random, key: int) -> dict[str, str]:
    agency = rng.choice(list(AGENCIES))
    complaint_type = rng.choice(list(COMPLAINTS[agency]))
    borough = rng.choices(list(LOCATIONS), weights=BOROUGH_WEIGHTS)[0]
    zips, boards = LOCATIONS[borough]
    created = START + timedelta(
        days=rng.randrange(SPAN_DAYS), hours=rng.randrange(24), minutes=rng.randrange(60)
    )
    row = {
        "unique_key": str(key),
        "created_date": timestamp(created),
        "agency": agency,
        "agency_name": rng.choice(AGENCIES[agency]),
        "complaint_type": complaint_type,
        "descriptor": rng.choice(COMPLAINTS[agency][complaint_type]),
        "borough": borough,
        "incident_zip": rng.choice(zips),
        "community_board": rng.choice(boards),
        "open_data_channel_type": rng.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0],
        "status": "Closed",
    }

    # Resolution: most requests close within days, some take longer than 30 days.
    roll = rng.random()
    if roll < 0.06:
        row["status"] = rng.choice(["Open", "In Progress", "Pending", "Assigned"])
    elif roll < 0.08:
        # Data-quality edge case present in the source: closed before created.
        row["closed_date"] = timestamp(created - timedelta(hours=rng.randrange(1, 72)))
    elif roll < 0.20:
        row["closed_date"] = timestamp(created + timedelta(days=rng.randrange(31, 120)))
    else:
        row["closed_date"] = timestamp(created + timedelta(minutes=rng.randrange(5, 20 * 1440)))

    # Missing dimension values: the API omits the key entirely.
    if rng.random() < 0.02:
        del row["borough"]
    if rng.random() < 0.03:
        del row["incident_zip"]
    if rng.random() < 0.02:
        del row["open_data_channel_type"]
    if rng.random() < 0.01:
        del row["descriptor"]
    return row


def main() -> None:
    rng = random.Random(SEED)
    keys = rng.sample(range(60_000_000, 61_000_000), VALID_ROWS)
    rows = [build_row(rng, key) for key in keys]

    # Rows the loader must reject, each for a different reason.
    template = dict(rows[0])
    missing_key = {k: v for k, v in template.items() if k != "unique_key"}
    non_numeric_key = {**template, "unique_key": "ABC-123"}
    missing_created = {k: v for k, v in template.items() if k != "created_date"}
    missing_created["unique_key"] = "61000001"
    bad_created = {**template, "unique_key": "61000002", "created_date": "not-a-date"}
    rows.extend([non_numeric_key, missing_created, bad_created])

    # Same order the API is read in. Rows without a sortable key go last.
    rows.sort(key=lambda r: (r.get("created_date", "~"), r.get("unique_key", "~")))
    rows.append(missing_key)

    output = Path(__file__).with_name("sample_311.json")
    output.write_text(json.dumps(rows, indent=0, sort_keys=True) + "\n")
    print(f"Wrote {len(rows)} rows ({VALID_ROWS} valid, 4 to reject) to {output.name}")


if __name__ == "__main__":
    main()
