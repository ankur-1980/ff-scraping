from __future__ import annotations

import re
from typing import Dict, Optional, Pattern

from bs4 import BeautifulSoup, Tag

from src.models import TeamSeasonRow


_TEAM_ID_PATTERNS: list[Pattern[str]] = [
    re.compile(r"/team/(\d+)\b"),
    re.compile(r"[?&]teamId=(\d+)\b"),
]


def _extract_team_id(team_link: Tag) -> Optional[str]:
    href_obj = team_link.get("href")
    href = href_obj if isinstance(href_obj, str) else ""

    for pat in _TEAM_ID_PATTERNS:
        m = pat.search(href)
        if m:
            return m.group(1)
    return None


def parse_regular_standings(soup: BeautifulSoup) -> Dict[str, TeamSeasonRow]:
    rows: Dict[str, TeamSeasonRow] = {}

    table_rows = soup.select("tr[class*='team']")

    for row in table_rows:
        rank_tag = row.find("span", class_="teamRank")
        name_tag = row.find("a", class_="teamName")
        record_tag = row.find("td", class_="teamRecord")
        pts_tags = row.find_all("td", class_="teamPts")

        if not (rank_tag and name_tag and record_tag and len(pts_tags) >= 2):
            continue

        team_name = name_tag.get_text(strip=True)
        team_id = _extract_team_id(name_tag)

        key = team_id if team_id else team_name.strip().casefold()

        rows[key] = TeamSeasonRow(
            team_id=team_id or "",
            team_name=team_name,
            regular_season_rank=rank_tag.get_text(strip=True),
            record=record_tag.get_text(strip=True),
            points_for=pts_tags[0].get_text(strip=True),
            points_against=pts_tags[1].get_text(strip=True),
        )

    if not rows:
        snippet = soup.get_text(" ", strip=True)[:300]
        raise RuntimeError(f"Parsed 0 teams from regular standings. Page snippet: {snippet}")

    return rows
