from __future__ import annotations

import re
from typing import Dict, Optional

from bs4 import BeautifulSoup, Tag

from src.models import TeamSeasonRow


_TEAM_ID_PATTERNS = [
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


def _extract_place_number(text: str) -> str:
    """
    Examples:
      "1st Place" -> "1"
      "3rd" -> "3"
    """
    token = (text or "").strip().split()[0] if text else ""
    digits = "".join(ch for ch in token if ch.isdigit())
    return digits


def apply_playoffs(soup: BeautifulSoup, rows_by_team: Dict[str, TeamSeasonRow]) -> None:
    """
    Enrich rows_by_team with playoff ranks from the 'final' standings page.

    rows_by_team keys are either team_id (preferred) or normalized team_name fallback.
    We try to match by team_id first; fallback to normalized team_name.
    """
    playoff_rows = soup.select("li[class*='place']")

    applied = 0

    for row in playoff_rows:
        place_div = row.find("div", class_="place")
        value_div = row.find("div", class_="value")
        team_link = value_div.find("a", class_="teamName") if value_div else None

        if not (place_div and team_link):
            continue

        place_text = place_div.get_text(" ", strip=True)
        place_number = _extract_place_number(place_text)

        team_name = team_link.get_text(strip=True)
        team_id = _extract_team_id(team_link)

        key = team_id if team_id and team_id in rows_by_team else team_name.strip().casefold()
        row_obj = rows_by_team.get(key)

        if row_obj:
            row_obj.playoff_rank = place_number
            applied += 1

    if applied == 0:
        # If the HTML changed, better to fail loudly than silently produce empty data
        snippet = soup.get_text(" ", strip=True)[:300]
        raise RuntimeError(f"Applied 0 playoff ranks. Page snippet: {snippet}")
