from __future__ import annotations

import csv
from pathlib import Path

from src.config import league_id


def main() -> None:
    base_dir = Path("output")
    standings_dir = base_dir / f"{league_id}-history-standings"

    # Assumes files are like: <season>.csv (e.g., 2023.csv)
    out_file = standings_dir / "all_seasons_standings.csv"

    header_written = False
    expected_header: list[str] | None = None

    with out_file.open("w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)

        for csv_file in sorted(standings_dir.glob("*.csv")):
            if csv_file.name == out_file.name:
                continue

            season = csv_file.stem  # "2025"

            with csv_file.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            if not rows:
                continue

            header = rows[0]
            data_rows = rows[1:]

            # Write header once, adding Season column
            if not header_written:
                expected_header = header
                writer.writerow(["Season"] + header)
                header_written = True
            else:
                # Safety: if header differs, fail fast so you don't silently corrupt the combined file
                if expected_header != header:
                    raise RuntimeError(
                        f"Header mismatch in {csv_file.name}.\n"
                        f"Expected: {expected_header}\n"
                        f"Got:      {header}"
                    )

            for row in data_rows:
                writer.writerow([season] + row)

    print(f"Wrote combined standings file: {out_file}")


if __name__ == "__main__":
    main()
