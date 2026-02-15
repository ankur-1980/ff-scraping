import re
from bs4 import BeautifulSoup as BS
from src.utils.parse_gamecenter import parse_owner, parse_opponent_owner, parse_opponent_total, parse_rank, parse_team_total, parse_team_projected_total
from src.utils.getterGamecenter import get_roster_names, get_roster_points

_NUM = re.compile(r"[-+]?\d*\.?\d+")

def build_header(starter_slots: list[str], longest_bench_len: int) -> list[str]:
    header = ["Owner", "Rank", "Result", "Diff"]
    header += ["Top Starter", "Top Starter Points", "Low Starter", "Low Starter Points"]

    for slot in starter_slots:
        header.append(slot)
        header.append("Points")

    for i in range(1, longest_bench_len + 1):
        header.append(f"BN{i}")
        header.append("Points")

    header += ["Total", "Projected Total", "Opponent", "Opponent Total"]

    return header

def _pad_to(items: list[str], target_len: int, fill: str = "-") -> list[str]:
    if len(items) < target_len:
        items.extend([fill] * (target_len - len(items)))
    return items[:target_len]


def build_row(soup: BS, starter_slots: list[str], longest_bench_len: int) -> list[str]:
    owner = parse_owner(soup)
    rank = parse_rank(soup)

    expected_starters = len(starter_slots)
    expected_roster_len = expected_starters + longest_bench_len

    roster = get_roster_names(soup, longest_bench_len)

    # ✅ Critical: ensure roster matches header expectation (starters + bench)
    roster = _pad_to(roster, expected_roster_len)

    points = get_roster_points(soup)
    # ✅ Also pad points so we always have one per roster slot
    points = _pad_to(points, expected_roster_len)
    
    top_name, top_pts, low_name, low_pts = compute_starter_extremes(
    roster=roster,
    points=points,
    starter_count=expected_starters,
)

    roster_and_points: list[str] = []
    for idx, name in enumerate(roster):
        roster_and_points.append(name)
        roster_and_points.append(points[idx] if idx < len(points) else "-")

    total = parse_team_total(soup)
    projected = parse_team_projected_total(soup)
    opp_owner = parse_opponent_owner(soup)
    opp_total = parse_opponent_total(soup)

    result = compute_result(total, opp_total, opp_owner)
    diff = compute_diff(total, opp_total)

    if result != "BYE" and diff != "-":
        d = float(diff)
        assert (
            (result == "W" and d > 0)
            or (result == "L" and d < 0)
            or (result == "T" and d == 0)
        ), f"Inconsistent result/diff: result={result}, diff={diff}, total={total}, opp_total={opp_total}"

    return (
        [owner, rank, result, diff, top_name, top_pts, low_name, low_pts]
        + roster_and_points
        + [total, projected, opp_owner, opp_total]
    )


def _to_float(value: str) -> float | None:
    m = _NUM.search(value or "")
    return float(m.group(0)) if m else None

def compute_result(team_total: str, opp_total: str, opponent: str) -> str:
    # If there’s clearly no opponent, treat as BYE
    if opponent in ("-", "", None):
        return "BYE"

    a = _to_float(team_total)
    b = _to_float(opp_total)
    if a is None or b is None:
        return "-"

    if a > b:
        return "W"
    if a < b:
        return "L"
    return "T"

def compute_diff(team_total: str, opp_total: str) -> str:
    a = _to_float(team_total)
    b = _to_float(opp_total)

    if a is None or b is None:
        return "-"

    diff = a - b
    return f"{diff:.2f}"


def compute_starter_extremes(
    roster: list[str],
    points: list[str],
    starter_count: int,
) -> tuple[str, str, str, str]:
    """
    Returns (top_name, top_points, low_name, low_points) for starters only.
    If we can't compute, returns "-" placeholders.
    """
    top: tuple[float, str] | None = None   # (pts, name)
    low: tuple[float, str] | None = None

    for i in range(min(starter_count, len(roster), len(points))):
        name = roster[i] if roster[i] else "-"
        pts = _to_float(points[i])

        # Skip empty slots / missing points
        if name == "-" or pts is None:
            continue

        if top is None or pts > top[0]:
            top = (pts, name)
        if low is None or pts < low[0]:
            low = (pts, name)

    if top is None or low is None:
        return "-", "-", "-", "-"

    return top[1], f"{top[0]:.2f}", low[1], f"{low[0]:.2f}"
