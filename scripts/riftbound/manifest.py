"""Reads and merges manifest.json.

The manifest is the only thing the frontend knows about; it never hardcodes a
retailer id or filename. Merging preserves the previous entry for a retailer
whose scrape failed, so one broken store degrades to a staleness badge instead
of removing its data.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .jsonio import read_json, write_json
from .paths import MANIFEST_FILE

SCHEMA_VERSION = 1


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load() -> dict[str, Any]:
    existing = read_json(MANIFEST_FILE)
    if not existing:
        return {"schema_version": SCHEMA_VERSION, "catalog": None, "retailers": []}
    return existing


def merge_retailer(manifest: dict[str, Any], entry: dict[str, Any]) -> None:
    retailers: list[dict[str, Any]] = manifest.setdefault("retailers", [])
    for index, existing in enumerate(retailers):
        if existing["id"] == entry["id"]:
            retailers[index] = entry
            break
    else:
        retailers.append(entry)
    retailers.sort(key=lambda item: item["id"])


def mark_failed(manifest: dict[str, Any], retailer_id: str, name: str, error: str) -> None:
    """Keep the previous data file and generated_at; only the status changes."""
    for existing in manifest.get("retailers", []):
        if existing["id"] == retailer_id:
            existing["status"] = "error"
            existing["error"] = error
            return
    merge_retailer(
        manifest,
        {
            "id": retailer_id,
            "name": name,
            "file": None,
            "generated_at": None,
            "listing_count": 0,
            "status": "error",
            "error": error,
        },
    )


def save(manifest: dict[str, Any]) -> None:
    manifest["schema_version"] = SCHEMA_VERSION
    manifest["generated_at"] = now_iso()
    write_json(MANIFEST_FILE, manifest)
