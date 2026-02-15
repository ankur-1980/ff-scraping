from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class ManagerAgg:
    seasons: int = 0
    # We’ll add fields one at a time in later commits:
    # wins: int = 0
    # losses: int = 0
    # ties: int = 0
    # points_for: float = 0.0
    # points_against: float = 0.0
    # moves: int = 0
    # trades: int = 0
    # playoffs: int = 0
    # championships: int = 0


def aggregate_seasons(standings_dir: Path) -> Dict[str, ManagerAgg]:
    aggregated: Dict[str, ManagerAgg] = {}

    season_files = sorted(standings_dir.glob("*.csv"))
    if not season_files:
        raise RuntimeError(f"No CSV files found in {standings_dir}")

    for season_path in season_files:
        # Count each manager once per season (not once per row)
        managers_seen_this_season: set[str] = set()

        with season_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                manager = (row.get("ManagerName") or "").strip()
                if not manager:
                    # If you ever see blanks, that means owners parsing failed for that season.
                    continue
                managers_seen_this_season.add(manager)

        for manager in managers_seen_this_season:
            aggregated.setdefault(manager, ManagerAgg()).seasons += 1

    return aggregated


def write_aggregated_csv(output_path: Path, aggregated: Dict[str, ManagerAgg]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ManagerName", "Seasons"])

        for manager_name in sorted(aggregated.keys(), key=str.casefold):
            writer.writerow([manager_name, aggregated[manager_name].seasons])


def main() -> None:
    # Adjust these paths if needed
    league_id = "879846"
    base_output = Path("output")
    standings_dir = base_output / f"{league_id}-history-standings"
    output_csv = base_output / "aggregated_standings_data.csv"

    aggregated = aggregate_seasons(standings_dir)
    write_aggregated_csv(output_csv, aggregated)

    print(f"Wrote {len(aggregated)} managers -> {output_csv}")


if __name__ == "__main__":
    main()
