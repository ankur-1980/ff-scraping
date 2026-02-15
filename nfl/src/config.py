from pathlib import Path

# League config
league_id: str = "879846"
league_start_year: int = 2012
league_end_year: int = 2026  # inclusive


# -----------------------------
# Output paths
# -----------------------------

# Base output directory
BASE_OUTPUT_DIR: Path = Path("output")

# Derived directories (no season yet)
STANDINGS_DIR: Path = BASE_OUTPUT_DIR / f"{league_id}-history-standings"
GAMECENTER_DIR: Path = BASE_OUTPUT_DIR / f"{league_id}-history-teamgamecenter"
