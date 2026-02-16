from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def main() -> None:
    in_path = Path("output") / "all_seasons_combined.csv"
    out_path = Path("output") / "all_seasons_combined_by_season_week_owner.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path.resolve()}")

    result: dict[str, dict[str, dict[str, Any]]] = {}

    with in_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise RuntimeError("CSV has no header row.")

        required = {"Season", "Week", "Owner"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise RuntimeError(f"Missing required columns: {sorted(missing)}")

        for row in reader:
            season = (row.get("Season") or "").strip()
            week = (row.get("Week") or "").strip()
            owner = (row.get("Owner") or "").strip()

            if not season or not week or not owner:
                continue

            # Keep full row (including Season/Week/Owner)
            payload = dict(row)

            season_bucket = result.setdefault(season, {})
            week_bucket = season_bucket.setdefault(week, {})

            existing = week_bucket.get(owner)

            if existing is None:
                week_bucket[owner] = payload
            else:
                # If duplicates exist, convert to list
                if isinstance(existing, list):
                    existing.append(payload)
                else:
                    week_bucket[owner] = [existing, payload]

    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote JSON to {out_path}")


if __name__ == "__main__":
    main()
