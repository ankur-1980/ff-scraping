from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TeamSeasonRow:
    team_id: str
    team_name: str
    regular_season_rank: str

    wins: int
    losses: int
    ties: int

    points_for: str
    points_against: str

    playoff_rank: str = ""
    manager_name: str = ""
    moves: str = ""
    trades: str = ""
