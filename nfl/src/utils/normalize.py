from __future__ import annotations

from typing import Mapping, MutableMapping, Any

MANAGER_NAME_MAP: dict[str, str] = {
    "Chris Beth": "Chris",
    "Fancett": "Big Dog",
    "Matt": "Matt Van",
    "Matthew": "Heddle",
    "Raymond": "Ray",
}

def normalize_manager_name(name: str, mapping: Mapping[str, str] = MANAGER_NAME_MAP) -> str:
    """
    Exact-match canonicalization of manager names.
    - Trims whitespace
    - Applies exact mapping only
    """
    cleaned = (name or "").strip()
    return mapping.get(cleaned, cleaned)

def normalize_row_manager(row: MutableMapping[str, Any], field: str = "ManagerName") -> MutableMapping[str, Any]:
    if field in row:
        row[field] = normalize_manager_name(str(row[field]))
    return row
