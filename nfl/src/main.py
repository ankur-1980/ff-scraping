from src.config import (
    BASE_OUTPUT_DIR,
    league_id,
    league_start_year,
    league_end_year,
)
from src.output_paths import ensure_output_paths


def main() -> None:
    for season in range(league_start_year, league_end_year + 1):
        paths = ensure_output_paths(
            league_id=league_id,
            season=season,
            base_output_dir=BASE_OUTPUT_DIR,
        )

        print(f"{season} -> {paths.standings_csv}")


if __name__ == "__main__":
    main()
