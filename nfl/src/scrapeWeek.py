import re
from bs4 import BeautifulSoup

from src.config import league_id
from src.http_client import get_soup
from src.secrets import cookie_string
from src.parsers.get_owners_count import get_number_of_owners


def gamecenter_url(season: str, team_id: int, week: int) -> str:
    return (
        f"https://fantasy.nfl.com/league/{league_id}/history/{season}/teamgamecenter"
        f"?teamId={team_id}&week={week}"
    )


def parse_owner(soup: BeautifulSoup) -> str:
    owner_span = soup.find("span", class_=re.compile(r"userName\s+userId"))
    return owner_span.get_text(strip=True) if owner_span else "-"


def parse_bench_len(soup: BeautifulSoup) -> int:
    bench_wrap = soup.find("div", id="tableWrapBN-1")
    if not bench_wrap:
        return 0
    return len(bench_wrap.find_all("td", class_="playerNameAndInfo"))


def main() -> None:
    season = "2025"
    week = 1

    number_of_owners = get_number_of_owners(league_id, season, cookie_string)
    print(f"Season={season} Week={week} Owners={number_of_owners}")

    # ✅ Cache soups here
    soups: dict[int, BeautifulSoup] = {}

    for team_id in range(1, number_of_owners + 1):
        url = gamecenter_url(season, team_id, week)
        soup = get_soup(url, cookie_string, must_contain=["teamMatchupBoxScore", "userName"])
        soups[team_id] = soup

    print("Finished fetching all teams.\n")

    longest_bench_len = -1
    longest_bench_team_id = -1
    longest_bench_owner = "-"

    for team_id, soup in soups.items():
        owner = parse_owner(soup)
        bench_len = parse_bench_len(soup)

        print(f"team_id={team_id:>2} owner={owner} bench={bench_len}")

        if bench_len > longest_bench_len:
            longest_bench_len = bench_len
            longest_bench_team_id = team_id
            longest_bench_owner = owner

    print(
        f"\nLongest bench: team_id={longest_bench_team_id} "
        f"owner={longest_bench_owner} bench={longest_bench_len}"
    )


if __name__ == "__main__":
    main()
