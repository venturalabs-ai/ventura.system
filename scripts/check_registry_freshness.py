#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "config" / "model-registry.json")
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    payload = json.loads(args.registry.read_text(encoding="utf-8"))
    verified = date.fromisoformat(payload["verified_at"])
    age = (args.today - verified).days
    if age < 0:
        print(f"registry verified_at is in the future: {verified.isoformat()}")
        return 2
    if age > args.max_age_days:
        print(f"MODEL REGISTRY STALE: age={age}d max={args.max_age_days}d verified_at={verified.isoformat()}")
        return 1
    print(f"MODEL REGISTRY FRESH: age={age}d verified_at={verified.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
