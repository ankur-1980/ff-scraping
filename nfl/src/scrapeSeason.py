from pathlib import Path

from src.config import league_id
from src.output_paths import ensure_output_paths
from src.secrets import cookie_string

from src.utils.getOwnersCount import get_number_of_owners
from src.utils.getSeasonLength import get_season_length
from src.scrapeWeek import scrape_week


def main() -> None:
    season = 2025

    paths = ensure_output_paths(
        league_id=league_id,
        season=season,
        base_output_dir=Path("output"),
    )

    number_of_owners = get_number_of_owners(league_id, season, cookie_string)
    season_length = get_season_length(league_id=league_id, season=season, cookie_string=cookie_string)

    print(f"Season {season}: owners={number_of_owners}, weeks={season_length}")

    for week in range(1, season_length + 1):
        out_csv = paths.gamecenter_dir / f"{season}-{week}.csv"

        # Skip if already scraped (super useful when rerunning)
        if out_csv.exists():
            print(f"Week {week}: already exists, skipping -> {out_csv}")
            continue

        print(f"Week {week}: scraping...")
        scrape_week(
            league_id=league_id,
            season=season,
            week=week,
            number_of_owners=number_of_owners,
            cookie_string=cookie_string,
            out_csv_path=out_csv,
        )
        print(f"Week {week}: wrote {out_csv}")

    print("Done")


if __name__ == "__main__":
    main()
