import csv
import re
from pathlib import Path

from bs4 import BeautifulSoup

from src.config import league_id
from pathlib import Path
from src.output_paths import ensure_output_paths
from src.http_client import get_soup
from src.secrets import cookie_string
from src.parsers.get_owners_count import get_number_of_owners
from src.parsers.parse_gamecenter import parse_owner, parse_bench_len


def gamecenter_url(season: int, team_id: int, week: int) -> str:
    return (
        f"https://fantasy.nfl.com/league/{league_id}/history/{season}/teamgamecenter"
        f"?teamId={team_id}&week={week}"
    )


def parse_rank(soup: BeautifulSoup) -> str:
    # rank_text looks like "... (3) ..." -> extract inside parentheses
    rank_span = soup.find("span", class_=re.compile(r"teamRank\s+teamId-"))
    rank_text = rank_span.get_text(strip=True) if rank_span else ""
    m = re.search(r"\((\d+)\)", rank_text)
    return m.group(1) if m else "-"


def parse_team_total(soup: BeautifulSoup) -> str:
    team_totals = soup.find_all("div", class_=re.compile(r"teamTotal\s+teamId-"))
    return team_totals[0].get_text(strip=True) if len(team_totals) >= 1 else "-"


def parse_opponent_owner(soup: BeautifulSoup) -> str:
    matchup = soup.find("div", id="teamMatchupBoxScore")
    if not matchup:
        return "-"
    team_wrap_2 = matchup.find("div", class_=re.compile(r"\bteamWrap\b.*\bteamWrap-2\b"))
    if not team_wrap_2:
        return "-"
    opp_owner_span = team_wrap_2.find("span", class_=re.compile(r"userName\s+userId"))
    return opp_owner_span.get_text(strip=True) if opp_owner_span else "-"


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


def build_header(starter_slots: list[str], longest_bench_len: int) -> list[str]:
    header: list[str] = ["Owner", "Rank"]
    for slot in starter_slots:
        header.append(slot)
        header.append("Points")

    for i in range(1, longest_bench_len + 1):
        header.append(f"BN{i}")
        header.append("Points")

    header += ["Total", "Opponent", "Opponent Total"]
    return header


def build_row(soup: BeautifulSoup, starter_slots: list[str], longest_bench_len: int) -> list[str]:
    owner = parse_owner(soup)
    rank = parse_rank(soup)

    roster = get_roster_names(soup, longest_bench_len)
    points = get_roster_points(soup)

    roster_and_points: list[str] = []
    for idx, name in enumerate(roster):
        roster_and_points.append(name)
        roster_and_points.append(points[idx] if idx < len(points) else "-")

    total = parse_team_total(soup)
    opp_owner = parse_opponent_owner(soup)
    opp_total = parse_opponent_total(soup)

    return [owner, rank] + roster_and_points + [total, opp_owner, opp_total]


def main() -> None:
    season = 2025
    week = 1
    
    paths = ensure_output_paths(
    league_id=league_id,
    season=season,
    base_output_dir=Path("output"),  # or from config
)

    number_of_owners = get_number_of_owners(league_id, season, cookie_string)
    print(f"Season={season} Week={week} Owners={number_of_owners}")

    # 1) Fetch and cache soups once
    soups: dict[int, BeautifulSoup] = {}
    for team_id in range(1, number_of_owners + 1):
        url = gamecenter_url(season, team_id, week)
        soups[team_id] = get_soup(url, cookie_string, must_contain=["teamMatchupBoxScore", "userName"])

    # 2) Find longest bench
    longest_bench_len = -1
    longest_bench_team_id = -1
    for team_id, soup in soups.items():
        bench_len = parse_bench_len(soup)
        if bench_len > longest_bench_len:
            longest_bench_len = bench_len
            longest_bench_team_id = team_id

    if longest_bench_team_id == -1:
        raise RuntimeError("Could not determine longest bench team")

    print(f"Longest bench: team_id={longest_bench_team_id} len={longest_bench_len}")

    # 3) Build header from a “representative” soup (use longest bench team)
    starter_slots = get_starter_slots(soups[longest_bench_team_id])
    header = build_header(starter_slots, longest_bench_len)

    # 4) Write CSV
    out_path = paths.gamecenter_dir / f"{week}.csv"


    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for team_id in range(1, number_of_owners + 1):
            row = build_row(soups[team_id], starter_slots, longest_bench_len)
            if len(row) != len(header):
                raise RuntimeError(
                    f"Row/header length mismatch for team_id={team_id}: "
                    f"row={len(row)} header={len(header)}"
                )
            writer.writerow(row)

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
