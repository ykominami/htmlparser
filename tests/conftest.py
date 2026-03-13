import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
YKLIBPY_SRC_DIR = ROOT_DIR.parent / "yklibpy" / "src"

for path in (SRC_DIR, YKLIBPY_SRC_DIR):
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)
