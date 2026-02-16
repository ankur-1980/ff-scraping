from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence


def pick_col(fieldnames: Sequence[str], candidates: Sequence[str]) -> str:
    """
    Pick a column by exact match first, then case-insensitive match.
    Raises KeyError if none found.
    """
    # exact
    for c in candidates:
        if c in fieldnames:
            return c

    # case-insensitive
    lower_map = {f.lower(): f for f in fieldnames}
    for c in candidates:
        key = c.lower()
        if key in lower_map:
            return lower_map[key]

    raise KeyError(f"Could not find any of {candidates} in columns: {fieldnames}")


def to_int_season(value: str) -> int | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def main() -> None:
    # Input / output paths
    in_path = Path("output") / "all_seasons_standings.csv"
    out_path = Path("output") / "all_seasons_standings_by_manager.json"

    if not in_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_path.resolve()}")

    with in_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise RuntimeError("CSV has no header row.")

        # Try to locate columns (adjust candidates if your headers differ)
        manager_col = pick_col(reader.fieldnames, ["managerName", "ManagerName", "manager", "Owner", "owner"])
        team_col = pick_col(reader.fieldnames, ["teamName", "TeamName", "team", "Team"])
        season_col = pick_col(reader.fieldnames, ["Season", "season", "Year", "year"])

        # Accumulators
        name_history: dict[str, set[str]] = defaultdict(set)
        active_seasons: dict[str, set[int]] = defaultdict(set)
        # Track "current" team name as the teamName from the most recent season
        latest_team: dict[str, tuple[int, str]] = {}  # manager -> (season, teamName)

        for row in reader:
            manager = (row.get(manager_col) or "").strip()
            team = (row.get(team_col) or "").strip()
            season_raw = row.get(season_col) or ""
            season = to_int_season(season_raw)

            if not manager:
                continue  # skip broken rows

            if team:
                name_history[manager].add(team)

            if season is not None:
                active_seasons[manager].add(season)
                if team:
                    prev = latest_team.get(manager)
                    if prev is None or season > prev[0]:
                        latest_team[manager] = (season, team)

        # Build final JSON object keyed by managerName
        result: dict[str, Any] = {}
        for manager in sorted(set(name_history.keys()) | set(active_seasons.keys()) | set(latest_team.keys())):
            seasons_sorted = sorted(active_seasons.get(manager, set()))
            history_sorted = sorted(name_history.get(manager, set()))

            # teamName: most recent season's team name if available; else "-"
            team_name = latest_team.get(manager, (None, "-"))[1]

            result[manager] = {
                "managerName": manager,
                "teamName": team_name,
                "nameHistory": history_sorted,     # exact unique names
                "activeSeasons": seasons_sorted,   # ints, sorted
            }

    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
