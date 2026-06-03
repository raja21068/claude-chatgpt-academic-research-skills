from __future__ import annotations

import sys
import zipfile
from pathlib import Path


EXCLUDE_NAMES = {".DS_Store", "__pycache__"}
EXCLUDE_SUFFIXES = {".pyc", ".log"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDE_NAMES for part in path.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return path.is_file()


def build_zip(batch_dir: Path) -> Path:
    batch_dir = batch_dir.resolve()
    if not batch_dir.exists() or not batch_dir.is_dir():
        raise FileNotFoundError(f"Batch folder not found: {batch_dir}")

    zip_path = batch_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(batch_dir.rglob("*")):
            if should_include(path):
                z.write(path, path.relative_to(batch_dir.parent))

    return zip_path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python local_tools/build_batch_zip.py path/to/batch_folder")
        raise SystemExit(2)

    zip_path = build_zip(Path(sys.argv[1]))
    print(f"Created ZIP: {zip_path}")


if __name__ == "__main__":
    main()
