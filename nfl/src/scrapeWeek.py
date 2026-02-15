import csv
from pathlib import Path

from bs4 import BeautifulSoup

from src.config import league_id
from src.output_paths import ensure_output_paths
from src.http_client import get_soup
from src.secrets import cookie_string
from src.utils.parse_gamecenter import parse_bench_len
from src.utils.getterGamecenter import get_starter_slots
from src.utils.gamecenterCsvUtils import build_header, build_row
from src.utils.getOwnersCount import get_number_of_owners

def gamecenter_url(season: int, team_id: int, week: int) -> str:
    return (
        f"https://fantasy.nfl.com/league/{league_id}/history/{season}/teamgamecenter"
        f"?teamId={team_id}&week={week}"
    )
    
def main() -> None:
    season = 2025
    week = 2
    
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
