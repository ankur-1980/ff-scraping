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


def apply_owners(soup: BeautifulSoup, rows_by_team: Dict[str, TeamSeasonRow]) -> None:
    """
    Enrich rows_by_team with manager + moves + trades from the owners page.
    Match by team_id if possible, otherwise fallback to normalized team name key.
    """
    owner_rows = soup.select("tr[class*='team']")

    applied = 0

    for row in owner_rows:
        team_link = row.find("a", class_="teamName")
        manager_tag = row.find("span", class_="userName")
        moves_tag = row.find("td", class_="teamTransactionCount")
        trades_tag = row.find("td", class_="teamTradeCount")

        if not (team_link and manager_tag and moves_tag and trades_tag):
            continue

        team_name = team_link.get_text(strip=True)
        team_id = _extract_team_id(team_link)

        key = team_id if team_id and team_id in rows_by_team else team_name.strip().casefold()
        row_obj = rows_by_team.get(key)
        if not row_obj:
            continue

        row_obj.manager_name = manager_tag.get_text(strip=True)
        row_obj.moves = moves_tag.get_text(strip=True)
        row_obj.trades = trades_tag.get_text(strip=True)
        applied += 1

    if applied == 0:
        snippet = soup.get_text(" ", strip=True)[:300]
        raise RuntimeError(f"Applied 0 owner rows. Page snippet: {snippet}")
