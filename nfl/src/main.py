from config import (
    league_start_year,
    league_end_year,
    BASE_OUTPUT_DIR,
    STANDINGS_DIR,
    GAMECENTER_DIR,
)


def main():
    # Ensure base directories exist
    BASE_OUTPUT_DIR.mkdir(exist_ok=True)
    STANDINGS_DIR.mkdir(parents=True, exist_ok=True)
    GAMECENTER_DIR.mkdir(parents=True, exist_ok=True)

    print("Directories created successfully.")


if __name__ == "__main__":
    main()
