import csv
from bs4 import BeautifulSoup as BS

from src.http_client import get_soup
from src.utils.parse_gamecenter import parse_bench_len
from src.utils.getterGamecenter import get_starter_slots
from src.utils.gamecenterCsvUtils import build_header, build_row


def gamecenter_url(*, league_id: str, season: int, team_id: int, week: int) -> str:
    return (
        f"https://fantasy.nfl.com/league/{league_id}/history/{season}/teamgamecenter"
        f"?teamId={team_id}&week={week}"
    )


def scrape_week(
    *,
    league_id: str,
    season: int,
    week: int,
    number_of_owners: int,
    cookie_string: str,
    out_csv_path,
) -> None:
    # 1) Fetch and cache soups once
    soups: dict[int, BS] = {}
    for team_id in range(1, number_of_owners + 1):
        url = gamecenter_url(league_id=league_id, season=season, team_id=team_id, week=week)
        soups[team_id] = get_soup(url, cookie_string, must_contain=["teamMatchupBoxScore"])

    # 2) Find longest bench
    longest_bench_len = -1
    longest_bench_team_id = -1
    for team_id, soup in soups.items():
        bench_len = parse_bench_len(soup)
        if bench_len > longest_bench_len:
            longest_bench_len = bench_len
            longest_bench_team_id = team_id

    if longest_bench_team_id == -1:
        raise RuntimeError(f"Could not determine longest bench team (season={season} week={week})")

    # 3) Header
    starter_slots = get_starter_slots(soups[longest_bench_team_id])
    header = build_header(starter_slots, longest_bench_len)

    # 4) Write CSV
    with out_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for team_id in range(1, number_of_owners + 1):
            row = build_row(soups[team_id], starter_slots, longest_bench_len)
            if len(row) != len(header):
                raise RuntimeError(
                    f"Row/header mismatch season={season} week={week} team_id={team_id} "
                    f"row={len(row)} header={len(header)}"
                )
            writer.writerow(row)
