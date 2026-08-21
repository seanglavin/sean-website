from __future__ import annotations

from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[2]
DATA_DIR: Final = ROOT / "public" / "riftbound-data"
PRICES_DIR: Final = DATA_DIR / "prices"
CARDS_FILE: Final = DATA_DIR / "cards.json"
MANIFEST_FILE: Final = DATA_DIR / "manifest.json"
REPORT_FILE: Final = ROOT / "riftbound-coverage.json"
