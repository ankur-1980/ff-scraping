import re
from bs4 import BeautifulSoup
from src.http_client import get_soup


def get_number_of_owners(
    league_id: str,
    season: str,
    cookie_string: str,
) -> int:
    owners_url = (
        f"https://fantasy.nfl.com/league/{league_id}/history/{season}/owners"
    )

    soup: BeautifulSoup = get_soup(
        owners_url,
        cookie_string,
        must_contain=["team-"]  # optional safety check
    )

    number_of_owners = len(
        soup.find_all("tr", class_=re.compile(r"\bteam-"))
    )

    return number_of_owners
