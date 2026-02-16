from dataclasses import dataclass
import re
from bs4 import BeautifulSoup

_TEAM_WRAP_1 = re.compile(r"\bteamWrap\b.*\bteamWrap-1\b")

@dataclass(frozen=True)
class PlayerRow:
    slot: str
    name: str
    points: str
    
_BLOCKY = re.compile(r"\bteamWrap\b.*\bteamWrap-2\b")
_USERNAME = re.compile(r"\buserName\b")

def parse_owner(soup: BeautifulSoup) -> str:
    owner_span = soup.find("span", class_=re.compile(r"userName\s+userId"))
    return owner_span.get_text(strip=True) if owner_span else "-"

def parse_team_total(soup: BeautifulSoup) -> str:
    totals = soup.find_all("div", class_=re.compile(r"teamTotal\s+teamId-"))
    return totals[0].get_text(strip=True) if totals else "-"

def parse_players(soup: BeautifulSoup) -> list[PlayerRow]:
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

def parse_bench_len(soup: BeautifulSoup) -> int:
    bench_wrap = soup.find("div", id="tableWrapBN-1")
    if not bench_wrap:
        return 0
    return len(bench_wrap.find_all("td", class_="playerNameAndInfo"))

def parse_rank(soup: BeautifulSoup) -> str:
    # rank_text looks like "... (3) ..." -> extract inside parentheses
    rank_span = soup.find("span", class_=re.compile(r"teamRank\s+teamId-"))
    rank_text = rank_span.get_text(strip=True) if rank_span else ""
    m = re.search(r"\((\d+)\)", rank_text)
    return m.group(1) if m else "-"


def parse_opponent_owner(soup: BeautifulSoup) -> str:
    matchup = soup.find("div", id="teamMatchupBoxScore")
    if not matchup:
        return "-"

    teamWrap2 = re.compile(r"\bteamWrap\b.*\bteamWrap-2\b")
    team_wrap_2 = matchup.find("div", class_=teamWrap2)
    if not team_wrap_2:
        return "-"

    # Primary: opponent team name appears in <h4>...</h4>
    h4 = team_wrap_2.find("h4")
    if h4:
        text = h4.get_text(" ", strip=True)
        return text or "-"

    # Fallback: some pages might show a username element
    tag = team_wrap_2.select_one(".userName")
    if tag:
        text = tag.get_text(" ", strip=True)
        return text or "-"

    return "-"

def parse_opponent_total(soup: BeautifulSoup) -> str:
    team_totals = soup.find_all("div", class_=re.compile(r"teamTotal\s+teamId-"))
    return team_totals[1].get_text(strip=True) if len(team_totals) >= 2 else "-"



def get_starter_slots(soup: BeautifulSoup) -> list[str]:
    """
    Pull slot labels (QB/RB/WR/...) from player rows.
    We'll treat non-BN slots as starters.
    """
    matchup = soup.find("div", id="teamMatchupBoxScore")
    if not matchup:
        return []

    team_wrap_1 = matchup.find("div", class_=re.compile(r"\bteamWrap\b.*\bteamWrap-1\b"))
    if not team_wrap_1:
        return []

    slots: list[str] = []
    for tr in team_wrap_1.find_all("tr", class_=re.compile(r"player-")):
        span = tr.find("span")
        slot = span.get_text(strip=True) if span else ""
        if not slot:
            continue
        # Stop when we hit bench (or skip bench)
        if slot == "BN":
            continue
        slots.append(slot)
    return slots


def get_roster_names(soup: BeautifulSoup, longest_bench_len: int) -> list[str]:
    """
    Roster = starters (tableWrap-1) + bench (tableWrapBN-1), padded to longest_bench_len.
    """
    starters_wrap = soup.find("div", id="tableWrap-1")
    starters = []
    if starters_wrap:
        starters = [
            td.get_text(" ", strip=True)
            for td in starters_wrap.find_all("td", class_="playerNameAndInfo")
        ]

    bench_wrap = soup.find("div", id="tableWrapBN-1")
    bench = []
    if bench_wrap:
        bench = [
            td.get_text(" ", strip=True)
            for td in bench_wrap.find_all("td", class_="playerNameAndInfo")
        ]

    while len(bench) < longest_bench_len:
        bench.append("-")

    return starters + bench


def get_roster_points(soup: BeautifulSoup) -> list[str]:
    """
    Pull points cells. This is the “old approach” and can misalign in edge cases,
    but it's enough for the first CSV commit. We'll harden later.
    """
    matchup = soup.find("div", id="teamMatchupBoxScore")
    if not matchup:
        return []

    team_wrap_1 = matchup.find("div", class_=re.compile(r"\bteamWrap\b.*\bteamWrap-1\b"))
    if not team_wrap_1:
        return []

    totals_tds = team_wrap_1.find_all("td", class_=re.compile(r"\bstatTotal\b"))
    return [td.get_text(strip=True) for td in totals_tds]

def parse_team_projected_total(soup: BeautifulSoup) -> str:
    matchup = soup.find("div", id="teamMatchupBoxScore")
    if not matchup:
        return "-"   

    team_wrap_1 = matchup.find("div", class_=re.compile(r"\bteamWrap\b.*\bteamWrap-1\b"))
    scope = team_wrap_1 or matchup

    projected_div = scope.find(class_="teamTotalProjected")
    if not projected_div:
        return "-"

    text = projected_div.get_text(" ", strip=True)  # e.g. "Proj 111.65"
    m = re.search(r"([\d.]+)", text)
    return m.group(1) if m else "-"

def parse_team_name(soup: BeautifulSoup) -> str:
    """Team name for the current team (teamWrap-1)."""
    matchup = soup.find("div", id="teamMatchupBoxScore")
    if not matchup:
        return "-"

    team_wrap_1 = matchup.find("div", class_=_TEAM_WRAP_1)
    if not team_wrap_1:
        return "-"

    h4 = team_wrap_1.find("h4")
    return h4.get_text(" ", strip=True) if h4 else "-"


