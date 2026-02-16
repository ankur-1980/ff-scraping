from __future__ import annotations

import csv
from pathlib import Path

from src.config import league_id


def main() -> None:
    base_dir = Path("output")
    gamecenter_root = base_dir / f"{league_id}-history-teamgamecenter"

    combined_rows: list[list[str]] = []
    header_written = False
    final_header: list[str] = []

    for season_dir in sorted(gamecenter_root.iterdir()):
        if not season_dir.is_dir():
            continue

        season = season_dir.name

        for csv_file in sorted(season_dir.glob("*.csv")):
            # filename format: 2025-1.csv
            name = csv_file.stem  # "2025-1"
            try:
                file_season, week = name.split("-")
            except ValueError:
                continue

            with csv_file.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            if not rows:
                continue

            file_header = rows[0]
            data_rows = rows[1:]

            # Write header once, adding Season + Week
            if not header_written:
                final_header = ["Season", "Week"] + file_header
                combined_rows.append(final_header)
                header_written = True

            for row in data_rows:
                combined_rows.append([file_season, week] + row)

    # Write combined CSV
    out_file = gamecenter_root / "all_seasons_combined.csv"

    with out_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(combined_rows)

    print(f"Wrote combined file: {out_file}")


if __name__ == "__main__":
    main()
