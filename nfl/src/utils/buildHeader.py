from bs4 import BeautifulSoup as BS
from src.utils.parse_gamecenter import parse_owner, parse_opponent_owner, parse_opponent_total, parse_rank, parse_team_total, parse_team_projected_total
from src.utils.getterGamecenter import get_roster_names, get_roster_points

def build_header(starter_slots: list[str], longest_bench_len: int) -> list[str]:
    header: list[str] = ["Owner", "Rank"]
    for slot in starter_slots:
        header.append(slot)
        header.append("Points")

    for i in range(1, longest_bench_len + 1):
        header.append(f"BN{i}")
        header.append("Points")

    header += ["Total", "Projected Total", "Opponent", "Opponent Total"]

    return header

def build_row(soup: BS, starter_slots: list[str], longest_bench_len: int) -> list[str]:
    owner = parse_owner(soup)
    rank = parse_rank(soup)

    roster = get_roster_names(soup, longest_bench_len)
    points = get_roster_points(soup)

    roster_and_points: list[str] = []
    for idx, name in enumerate(roster):
        roster_and_points.append(name)
        roster_and_points.append(points[idx] if idx < len(points) else "-")

    total = parse_team_total(soup)
    projected = parse_team_projected_total(soup)
    opp_owner = parse_opponent_owner(soup)
    opp_total = parse_opponent_total(soup)

    return (
    [owner, rank]
    + roster_and_points
    + [total, projected, opp_owner, opp_total]
)