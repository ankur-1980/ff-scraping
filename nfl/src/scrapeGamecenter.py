from src.config import league_id
from src.http_client import get_soup
from src.secrets import cookie_string

URL = f"https://fantasy.nfl.com/league/{league_id}/history/2025/teamgamecenter?teamId=10&week=1"

def main() -> None:
    soup = get_soup(URL, cookie_string, must_contain=["teamMatchupBoxScore", "userName"])

    title = soup.title.get_text(strip=True) if soup.title else "(no title)"
    print(f"<title>: {title}")

    html = str(soup)
    lower = html.lower()
    if any(x in lower for x in ("sign in", "log in", "captcha", "verify you are human", "access denied")):
        print("WARNING: page looks like login/block content")

    print(f"HTML length: {len(html)}")

if __name__ == "__main__":
    main()
