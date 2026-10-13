#!/usr/bin/env python3
"""OLTP vs OLAP benchmark on NYC 311 Service Requests.

Usage:
    python benchmark.py load  --profile {quick|full}
    python benchmark.py build --profile {quick|full}

Run `python benchmark.py --help` for every command and option.
"""

import sys
from pathlib import Path

# Lets the script run from a checkout even when the package is not installed.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from nyc311_bench.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
