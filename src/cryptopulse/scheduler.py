"""Simple local scheduler entry point; production schedulers should invoke the pipeline command."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from .operations import run_pipeline
from .storage import PipelineBusyError


def run_once(project_root: Path, database_path: Path) -> str | None:
    try:
        return run_pipeline(project_root, database_path)
    except PipelineBusyError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Schedule repeated local CryptoPulse pipeline runs")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--database", type=Path, default=Path("var/cryptopulse.db"))
    parser.add_argument("--interval-minutes", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.interval_minutes < 1:
        parser.error("--interval-minutes must be at least 1")
    while True:
        run_once(args.project_root, args.database)
        if args.once:
            return
        time.sleep(args.interval_minutes * 60)


if __name__ == "__main__":
    main()
