import re
from bs4 import BeautifulSoup as BS
from src.http_client import get_soup


def get_starter_slots(soup: BS) -> list[str]:
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
  
def get_roster_points(soup: BS) -> list[str]:
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
  
def get_roster_names(soup: BS, longest_bench_len: int) -> list[str]:
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