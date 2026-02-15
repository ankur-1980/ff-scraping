from dataclasses import dataclass
import re
from bs4 import BeautifulSoup as BS

@dataclass(frozen=True)
class PlayerRow:
    slot: str
    name: str
    points: str

def parse_owner(soup: BS) -> str:
    owner_span = soup.find("span", class_=re.compile(r"userName\s+userId"))
    return owner_span.get_text(strip=True) if owner_span else "-"

def parse_team_total(soup: BS) -> str:
    totals = soup.find_all("div", class_=re.compile(r"teamTotal\s+teamId-"))
    return totals[0].get_text(strip=True) if totals else "-"

def parse_players(soup: BS) -> list[PlayerRow]:
    matchup = soup.find("div", id="teamMatchupBoxScore")
    if not matchup:
        return []

    team_wrap_1 = matchup.find("div", class_=re.compile(r"\bteamWrap\b.*\bteamWrap-1\b"))
    if not team_wrap_1:
        return []

    rows: list[PlayerRow] = []
    for tr in team_wrap_1.find_all("tr", class_=re.compile(r"player-")):
        # slot label (usually a <span> at start of row)
        slot_span = tr.find("span")
        slot = slot_span.get_text(strip=True) if slot_span else ""

        name_td = tr.find("td", class_="playerNameAndInfo")
        name = name_td.get_text(" ", strip=True) if name_td else "-"

        points_td = tr.find("td", class_=re.compile(r"\bstatTotal\b"))
        points = points_td.get_text(strip=True) if points_td else "-"

        if slot or name != "-":
            rows.append(PlayerRow(slot=slot, name=name, points=points))

    return rows