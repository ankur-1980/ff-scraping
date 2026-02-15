import re
from src.http_client import get_soup


def get_season_length(*, league_id: str, season: int, cookie_string: str) -> int:
    """
    Determine number of weeks in a season by counting week selector items.
    """
    url = (
        f"https://fantasy.nfl.com/league/879846/history/2025/teamgamecenter"
        f"?teamId=1&week=1"
    )
    soup = get_soup(url, cookie_string, must_contain=["teamMatchupBoxScore", "ww ww-"])

    # Same approach you used before: count week selector <li class="ww ww-x">
    weeks = soup.find_all("li", class_=re.compile(r"\bww\b.*\bww-\d+\b"))
    print(len(weeks))
    return len(weeks)
