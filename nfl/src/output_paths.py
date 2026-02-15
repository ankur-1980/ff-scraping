from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OutputPaths:
    """All filesystem locations the scraper writes to for a given league + season."""
    base_dir: Path
    standings_dir: Path
    gamecenter_dir: Path
    standings_csv: Path


def ensure_output_paths(*, league_id: str, season: int, base_output_dir: Path) -> OutputPaths:
    """
    Create output directories (if missing) and return structured paths
    for the given league + season.
    """
    base_dir = base_output_dir
    standings_dir = base_dir / f"{league_id}-history-standings"
    gamecenter_dir = base_dir / f"{league_id}-history-teamgamecenter" / str(season)

    # Ensure dirs exist
    base_dir.mkdir(parents=True, exist_ok=True)
    standings_dir.mkdir(parents=True, exist_ok=True)
    gamecenter_dir.mkdir(parents=True, exist_ok=True)

    standings_csv = standings_dir / f"{season}.csv"

    return OutputPaths(
        base_dir=base_dir,
        standings_dir=standings_dir,
        gamecenter_dir=gamecenter_dir,
        standings_csv=standings_csv,
    )
