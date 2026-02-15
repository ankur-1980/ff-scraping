from src.config import (
    BASE_OUTPUT_DIR,
    league_id,
    league_start_year,
    league_end_year,
)
from src.http_client import get_soup
from src.output_paths import ensure_output_paths
from src.utils.owners import apply_owners
from src.utils.playoffs import apply_playoffs
from src.utils.regular_standings import parse_regular_standings
from src.secrets import cookie_string
from src.writer import write_standings_csv
import time


def main() -> None:
    for season in range(league_start_year, league_end_year + 1):
        print(f"\nProcessing season {season}...")

        try:
            regular_url = (
                f"https://fantasy.nfl.com/league/{league_id}/history/{season}/standings"
                f"?historyStandingsType=regular"
            )
            playoffs_url = (
                f"https://fantasy.nfl.com/league/{league_id}/history/{season}/standings"
                f"?historyStandingsType=final"
            )
            owners_url = (
                f"https://fantasy.nfl.com/league/{league_id}/history/{season}/owners"
            )

            # --- Regular standings ---
            regular_soup = get_soup(
                regular_url,
                cookie_string,
                must_contain=["teamName", "teamPts"],
            )
            rows_by_team = parse_regular_standings(regular_soup)

            # --- Playoffs ---
            playoffs_soup = get_soup(
                playoffs_url,
                cookie_string,
                must_contain=["teamName", "place"],
            )
            apply_playoffs(playoffs_soup, rows_by_team)

            # --- Owners ---
            owners_soup = get_soup(
                owners_url,
                cookie_string,
                must_contain=["teamName", "userName"],
            )
            apply_owners(owners_soup, rows_by_team)

            # --- Write CSV ---
            paths = ensure_output_paths(
                league_id=league_id,
                season=season,
                base_output_dir=BASE_OUTPUT_DIR,
            )

            write_standings_csv(paths.standings_csv, rows_by_team.values())

            print(f"✓ Wrote {len(rows_by_team)} rows -> {paths.standings_csv}")
            
            time.sleep(0.5)

        except Exception as e:
            print(f"✗ Failed season {season}: {e}")


if __name__ == "__main__":
    main()
