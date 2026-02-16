from __future__ import annotations

import csv
from pathlib import Path

from src.config import league_id
from src.utils.normalize import normalize_manager_name


def main() -> None:
    base_dir = Path("output")
    gamecenter_root = base_dir / f"{league_id}-history-teamgamecenter"

    out_file = gamecenter_root / "all_seasons_combined.csv"

    # First pass: discover union header across all files
    union_cols: list[str] = []
    seen = set()

    files: list[Path] = []
    for season_dir in sorted(gamecenter_root.iterdir()):
        if not season_dir.is_dir():
            continue
        for csv_file in sorted(season_dir.glob("*.csv")):
            files.append(csv_file)

            with csv_file.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    continue
                for col in header:
                    if col not in seen:
                        seen.add(col)
                        union_cols.append(col)

    if not union_cols:
        raise RuntimeError(f"No CSV headers found under {gamecenter_root}")

    # We want Season/Week prefixed
    final_header = ["Season", "Week"] + union_cols

    # Determine which column holds manager name (prefer Owner)
    try:
        owner_col_name = "Owner" if "Owner" in union_cols else "ManagerName"
    except Exception:
        owner_col_name = "Owner"

    with out_file.open("w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=final_header)
        writer.writeheader()

        # Second pass: write aligned rows
        for csv_file in files:
            # filename format: 2017-11.csv
            name = csv_file.stem
            try:
                file_season, week = name.split("-")
            except ValueError:
                continue

            with csv_file.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    continue

                for row in reader:
                    # normalize manager/owner if present
                    if owner_col_name in row:
                        row[owner_col_name] = normalize_manager_name(row.get(owner_col_name) or "")

                    # Build output dict with blanks for missing cols
                    out_row = {col: "" for col in final_header}
                    out_row["Season"] = file_season
                    out_row["Week"] = week
                    for k, v in row.items():
                        if k in union_cols:
                            out_row[k] = v if v is not None else ""
                    writer.writerow(out_row)

    print(f"Wrote combined file: {out_file}")


if __name__ == "__main__":
    main()
