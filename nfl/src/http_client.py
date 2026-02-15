from __future__ import annotations

from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup as BS


DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Referer": "https://fantasy.nfl.com/",
    "Upgrade-Insecure-Requests": "1",
}

SESSION = requests.Session()


class ScrapeBlockedError(RuntimeError):
    pass


def looks_like_login_or_block(html: str) -> bool:
    t = html.lower()
    return any(
        s in t
        for s in (
            "sign in",
            "log in",
            "login",
            "access denied",
            "forbidden",
            "blocked",
            "captcha",
            "consent",
            "verify you are human",
        )
    )


def get_soup(url: str, cookie_string: str, must_contain: Optional[Iterable[str]] = None) -> BS:
    # warmup (same as before)
    SESSION.get("https://fantasy.nfl.com/", headers=DEFAULT_HEADERS, timeout=30)

    headers = dict(DEFAULT_HEADERS)
    headers["Cookie"] = cookie_string

    resp = SESSION.get(url, headers=headers, timeout=30, allow_redirects=True)
    resp.raise_for_status()

    html = resp.text or ""
    if must_contain:
        missing = [m for m in must_contain if m not in html]
        if missing:
            snippet = html[:1200].replace("\n", " ")
            raise RuntimeError(
                f"Did not receive expected HTML for URL:\n{url}\n\n"
                f"Missing markers: {missing}\n\n"
                f"HTML snippet:\n{snippet}"
            )

    return BS(html, "html.parser")
