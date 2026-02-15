from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from src.config import cutoff_playoffs, league_id, REQUIRED_COLUMNS
from collections import defaultdict


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


def safe_rank(value: str | None) -> int:
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
    toilet_bowls: int = 0


def aggregate_stats(standings_dir: Path) -> dict[str, ManagerAgg]:
    aggregated: defaultdict[str, ManagerAgg] = defaultdict(ManagerAgg)

    season_files = sorted(standings_dir.glob("*.csv"))
    if not season_files:
        raise RuntimeError(f"No CSV files found in {standings_dir}")

    for season_path in season_files:
        managers_seen_this_season: set[str] = set()

        with season_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise RuntimeError(f"{season_path.name} missing columns: {sorted(missing)}")

            season_rows = list(reader)

        num_owners = len(season_rows)
        playoff_cutoff = cutoff_playoffs
        bottom_four_cutoff = max(1, num_owners - 3)

        for row in season_rows:
            manager = (row.get("ManagerName") or "").strip()
            if not manager:
                continue

            managers_seen_this_season.add(manager)
            agg = aggregated[manager]

            agg.wins += safe_int(row.get("Wins"))
            agg.losses += safe_int(row.get("Losses"))
            agg.ties += safe_int(row.get("Ties"))
            agg.points_for += safe_float(row.get("PointsFor"))
            agg.points_against += safe_float(row.get("PointsAgainst"))
            agg.moves += safe_int(row.get("Moves"))
            agg.trades += safe_int(row.get("Trades"))

            rank_playoff = safe_rank(row.get("PlayoffRank"))
            if rank_playoff == 1:
                agg.playoffs += 1
                agg.championships += 1
            elif 0 < rank_playoff <= playoff_cutoff:
                agg.playoffs += 1

            reg_rank = safe_rank(row.get("RegularSeasonRank"))
            if reg_rank and reg_rank >= bottom_four_cutoff:
                agg.toilet_bowls += 1

        for manager in managers_seen_this_season:
            aggregated[manager].seasons += 1

    return dict(aggregated)


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
                    a.toilet_bowls
                ]
            )


def main() -> None:
    base_output = Path("output")
    standings_dir = base_output / f"{league_id}-history-standings"
    output_csv = base_output / "aggregated_standings_data.csv"

    aggregated = aggregate_stats(standings_dir)
    write_aggregated_csv(output_csv, aggregated)

    print(f"Wrote {len(aggregated)} managers -> {output_csv}")


if __name__ == "__main__":
    main()
