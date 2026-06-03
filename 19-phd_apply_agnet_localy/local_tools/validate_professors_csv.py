from __future__ import annotations

import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = [
    "rank",
    "professor_name",
    "email",
    "profile_url",
    "research_areas",
    "match_score",
    "match_reason",
    "email_file",
    "cv_file",
    "status",
]


def validate(path: Path) -> int:
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return 1

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in columns]

        if missing:
            print("ERROR: Missing required columns:")
            for col in missing:
                print(f"  - {col}")
            return 1

        rows = list(reader)

    if not rows:
        print("ERROR: CSV has no professor rows.")
        return 1

    warnings = 0
    for idx, row in enumerate(rows, start=1):
        if not row.get("professor_name", "").strip():
            print(f"WARNING row {idx}: missing professor_name")
            warnings += 1
        if not row.get("profile_url", "").strip():
            print(f"WARNING row {idx}: missing profile_url")
            warnings += 1
        if not row.get("email", "").strip() or row.get("email", "").strip().lower() == "not found":
            print(f"NOTICE row {idx}: email not found for {row.get('professor_name', 'Unknown')}")
        try:
            score = float(row.get("match_score", "0") or 0)
            if score < 60:
                print(f"NOTICE row {idx}: weak match score {score} for {row.get('professor_name', 'Unknown')}")
        except ValueError:
            print(f"WARNING row {idx}: invalid match_score")
            warnings += 1

    print(f"OK: {len(rows)} rows checked. Warnings/notices: {warnings}")
    return 0


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python validate_professors_csv.py path/to/professors.csv")
        raise SystemExit(2)

    raise SystemExit(validate(Path(sys.argv[1])))


if __name__ == "__main__":
    main()
