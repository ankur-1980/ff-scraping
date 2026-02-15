from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from src.models import TeamSeasonRow


CSV_HEADER: list[str] = [
    "TeamID",
    "TeamName",
    "RegularSeasonRank",
    "Record",
    "PointsFor",
    "PointsAgainst",
    "PlayoffRank",
    "ManagerName",
    "Moves",
    "Trades",
]


def write_standings_csv(path: Path, rows: Iterable[TeamSeasonRow]) -> None:
    # Stable sort by rank if possible
    def sort_key(r: TeamSeasonRow) -> tuple[int, str]:
        try:
            return (int(r.regular_season_rank), r.team_name)
        except ValueError:
            return (9999, r.team_name)

    rows_sorted = sorted(rows, key=sort_key)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

        for r in rows_sorted:
            writer.writerow(
                [
                    r.team_id,
                    r.team_name,
                    r.regular_season_rank,
                    r.record,
                    r.points_for,
                    r.points_against,
                    r.playoff_rank,
                    r.manager_name,
                    r.moves,
                    r.trades,
                ]
            )
