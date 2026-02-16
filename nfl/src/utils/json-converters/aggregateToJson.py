from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def parse_int(s: str) -> int:
    s = (s or "").strip()
    if not s:
        return 0
    try:
        return int(s)
    except ValueError:
        return 0


def parse_float(s: str) -> float:
    s = (s or "").strip()
    if not s:
        return 0.0
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return 0.0


def main() -> None:
    in_path = Path("output") / "aggregated_standings_data.csv"
    out_path = Path("output") / "aggregated_standings_data.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path.resolve()}")

    data: dict[str, Any] = {}

    with in_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise RuntimeError("CSV has no header row.")

        if "ManagerName" not in reader.fieldnames:
            raise RuntimeError(f"CSV missing 'ManagerName' column. Found: {reader.fieldnames}")

        for row in reader:
            manager = (row.get("ManagerName") or "").strip()
            if not manager:
                continue

            # Keep the schema explicit and typed
            data[manager] = {
                "ManagerName": manager,
                "Seasons": parse_int(row.get("Seasons", "")),
                "Wins": parse_int(row.get("Wins", "")),
                "Losses": parse_int(row.get("Losses", "")),
                "Ties": parse_int(row.get("Ties", "")),
                "PointsFor": parse_float(row.get("PointsFor", "")),
                "PointsAgainst": parse_float(row.get("PointsAgainst", "")),
                "Moves": parse_int(row.get("Moves", "")),
                "Trades": parse_int(row.get("Trades", "")),
                "Playoffs": parse_int(row.get("Playoffs", "")),
                "Championships": parse_int(row.get("Championships", "")),
                # Your CSV header is "Toilet Bowl" (with space)
                "ToiletBowls": parse_int(row.get("Toilet Bowl", "")),
            }

    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(data)} managers -> {out_path}")


if __name__ == "__main__":
    main()
