from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def parse_int(value: str | None) -> int:
    value = (value or "").strip()
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0


def parse_float(value: str | None) -> float:
    value = (value or "").strip()
    if not value:
        return 0.0
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return 0.0


def main() -> None:
    in_path = Path("output") / "all_seasons_standings.csv"
    out_path = Path("output") / "all_seasons_standings_by_season_team.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path.resolve()}")

    result: dict[str, dict[str, Any]] = {}

    with in_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise RuntimeError("CSV has no header row.")

        required = {"Season", "TeamName"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise RuntimeError(f"Missing required columns: {missing}")

        for row in reader:
            season = (row.get("Season") or "").strip()
            team = (row.get("TeamName") or "").strip()

            if not season or not team:
                continue

            if season not in result:
                result[season] = {}

            # Build clean typed object
            result[season][team] = {
                "TeamName": team,
                "ManagerName": (row.get("ManagerName") or "").strip(),
                "Wins": parse_int(row.get("Wins")),
                "Losses": parse_int(row.get("Losses")),
                "Ties": parse_int(row.get("Ties")),
                "PointsFor": parse_float(row.get("PointsFor")),
                "PointsAgainst": parse_float(row.get("PointsAgainst")),
                "RegularSeasonRank": parse_int(row.get("RegularSeasonRank")),
                "PlayoffRank": parse_int(row.get("PlayoffRank")),
                "Moves": parse_int(row.get("Moves")),
                "Trades": parse_int(row.get("Trades")),
            }

    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote JSON to {out_path}")


if __name__ == "__main__":
    main()
