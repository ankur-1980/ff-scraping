from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup as BS

from src.config import league_id, league_end_year, league_start_year
from src.secrets import cookie_string
from src.scrapeSeason import scrape_season


def dump_debug_html(*, debug_dir: Path, season: int, week: int, team_id: int, soup: BS) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    out = debug_dir / f"gamecenter_{season}_w{week}_team{team_id}.html"
    out.write_text(str(soup), encoding="utf-8")

def main() -> None:
    # Adjust these to your full range
    start_season = league_start_year
    end_season = league_end_year

    base_output_dir = Path("output")

    for season in range(start_season, end_season + 1):
        try:
            scrape_season(
                league_id=league_id,
                season=season,
                base_output_dir=base_output_dir,
                cookie_string=cookie_string,
            )
        except Exception as e:
            # Stop on first failure so you can inspect debug HTML & fix parsing
            print(f"\nFAILED season {season}: {e}")
            raise

    print("\nAll done")


if __name__ == "__main__":
    main()
