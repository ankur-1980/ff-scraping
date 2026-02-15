from src.config import league_id
from src.http_client import get_soup
from src.secrets import cookie_string


def main() -> None:
    url = f"https://fantasy.nfl.com/league/{league_id}/history/2025/standings?historyStandingsType=regular"
    soup = get_soup(url, cookie_string, must_contain=["teamName", "teamPts"]) 

    title = soup.title.get_text(strip=True) if soup.title else "(no title)"
    print(f"<title>: {title}")

    text_sample = soup.get_text(" ", strip=True)[:200]
    print(f"Text sample: {text_sample}")


if __name__ == "__main__":
    main()
