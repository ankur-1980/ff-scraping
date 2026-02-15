from src.config import league_id
from src.http_client import get_soup
from src.regular_standings import parse_regular_standings
from src.secrets import cookie_string


def main() -> None:
    season = 2025
    url = f"https://fantasy.nfl.com/league/{league_id}/history/{season}/standings?historyStandingsType=regular"
    soup = get_soup(url, cookie_string, must_contain=["teamName", "teamPts"])

    rows_by_team = parse_regular_standings(soup)

    print(f"Parsed {len(rows_by_team)} teams for {season}")
    for i, row in enumerate(rows_by_team.values()):
        if i >= 2:
            break
        print(row)


if __name__ == "__main__":
    main()
