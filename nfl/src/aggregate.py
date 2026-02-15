from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from src.config import cutoff_playoffs


def safe_int(value: str | None) -> int:
    if value is None:
        return 0
    text = value.strip()
    if not text:
        return 0
    try:
        return int(text)
    except ValueError:
        return 0


def safe_float(value: str | None) -> float:
    if value is None:
        return 0.0
    text = value.strip()
    if not text:
        return 0.0
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return 0.0


def safe_playoff_rank(value: str | None) -> int:
    """
    PlayoffRank might be "", "1", or sometimes "1st" depending on source.
    Extract digits defensively.
    """
    if value is None:
        return 0
    text = value.strip()
    if not text:
        return 0
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return 0
    try:
        return int(digits)
    except ValueError:
        return 0


@dataclass
class ManagerAgg:
    seasons: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    points_for: float = 0.0
    points_against: float = 0.0
    moves: int = 0
    trades: int = 0
    playoffs: int = 0
    championships: int = 0
    bottom4: int = 0


def aggregate_stats(standings_dir: Path) -> Dict[str, ManagerAgg]:
    aggregated: Dict[str, ManagerAgg] = {}

    season_files = sorted(standings_dir.glob("*.csv"))
    if not season_files:
        raise RuntimeError(f"No CSV files found in {standings_dir}")

    for season_path in season_files:
        managers_seen_this_season: set[str] = set()

        with season_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            required = {
                "ManagerName",
                "Wins",
                "Losses",
                "Ties",
                "PointsFor",
                "PointsAgainst",
                "Moves",
                "Trades",
                "PlayoffRank",
                "RegularSeasonRank"
            }
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise RuntimeError(f"{season_path.name} missing columns: {sorted(missing)}")

            season_rows = list(reader)

        num_owners = len(season_rows)
        playoff_cutoff = cutoff_playoffs

        for row in season_rows:
            manager = (row.get("ManagerName") or "").strip()
            if not manager:
                continue

            managers_seen_this_season.add(manager)
            agg = aggregated.setdefault(manager, ManagerAgg())

            agg.wins += safe_int(row.get("Wins"))
            agg.losses += safe_int(row.get("Losses"))
            agg.ties += safe_int(row.get("Ties"))
            agg.points_for += safe_float(row.get("PointsFor"))
            agg.points_against += safe_float(row.get("PointsAgainst"))
            agg.moves += safe_int(row.get("Moves"))
            agg.trades += safe_int(row.get("Trades"))

            rank_playoff = safe_playoff_rank(row.get("PlayoffRank"))
            if rank_playoff == 1:
                agg.playoffs += 1
                agg.championships += 1
            elif rank_playoff and rank_playoff <= playoff_cutoff:
                agg.playoffs += 1
                
            rank_bottom4 = safe_playoff_rank(row.get("RegularSeasonRank"))
            num_owners = len(season_rows)
            bottom_four_cutoff = num_owners - 3
            if rank_bottom4 and rank_bottom4 >= bottom_four_cutoff:
                agg.bottom4 += 1
            

        for manager in managers_seen_this_season:
            aggregated.setdefault(manager, ManagerAgg()).seasons += 1

    return aggregated


def write_aggregated_csv(output_path: Path, aggregated: Dict[str, ManagerAgg]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "ManagerName",
                "Seasons",
                "Wins",
                "Losses",
                "Ties",
                "PointsFor",
                "PointsAgainst",
                "Moves",
                "Trades",
                "Playoffs",
                "Championships",
                "Toilet Bowl"
            ]
        )

        for manager in sorted(aggregated.keys(), key=str.casefold):
            a = aggregated[manager]
            writer.writerow(
                [
                    manager,
                    a.seasons,
                    a.wins,
                    a.losses,
                    a.ties,
                    f"{a.points_for:.2f}",
                    f"{a.points_against:.2f}",
                    a.moves,
                    a.trades,
                    a.playoffs,
                    a.championships,
                    a.bottom4
                ]
            )


def main() -> None:
    league_id = "879846"
    base_output = Path("output")
    standings_dir = base_output / f"{league_id}-history-standings"
    output_csv = base_output / "aggregated_standings_data.csv"

    aggregated = aggregate_stats(standings_dir)
    write_aggregated_csv(output_csv, aggregated)

    print(f"Wrote {len(aggregated)} managers -> {output_csv}")


if __name__ == "__main__":
    main()
