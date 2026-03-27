#!/usr/bin/env python3
"""
Generates MTG game boards from Scryfall bulk data.
Writes public/game-data/boards.json and public/game-data/stats.json.
Run via GitHub Actions or manually: python scripts/generate_boards.py
"""

import asyncio
import httpx
import ijson
import json
import logging
import os
import random
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

SCRYFALL_BULK_DATA_URL = "https://api.scryfall.com/bulk-data"
BULK_TYPE = "default_cards"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "game-data"
NUM_BOARDS = 500
BOARD_SIZE = 4
NUM_DISTRACTORS = 6

_EXCLUDED_LAYOUTS = {
    "token", "emblem", "scheme", "conspiracy", "planar", "vanguard",
    "double_faced_token", "art_series", "reversible_card",
}


def _is_eligible(card: dict) -> bool:
    if card.get("lang") != "en":
        return False
    if card.get("layout") in _EXCLUDED_LAYOUTS:
        return False
    image_uris = card.get("image_uris") or {}
    if not image_uris.get("art_crop"):
        return False
    return True


async def fetch_download_uri() -> str:
    logger.info("Fetching Scryfall bulk data index...")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SCRYFALL_BULK_DATA_URL)
        resp.raise_for_status()
        for entry in resp.json().get("data", []):
            if entry.get("type") == BULK_TYPE:
                logger.info(f"Found download URI: {entry['download_uri']}")
                return entry["download_uri"]
    raise ValueError("Could not find default_cards bulk data entry")


async def download_to_temp(download_uri: str) -> str:
    _, tmppath = tempfile.mkstemp(suffix=".json")
    logger.info("Downloading bulk card data (this takes a few minutes)...")
    async with httpx.AsyncClient(timeout=600, follow_redirects=True) as client:
        async with client.stream("GET", download_uri) as resp:
            resp.raise_for_status()
            total = 0
            with open(tmppath, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    f.write(chunk)
                    total += len(chunk)
                    if total % (50 * 1024 * 1024) < 65536:
                        logger.info(f"  {total // (1024 * 1024)} MB downloaded...")
    logger.info("Download complete.")
    return tmppath


def parse_eligible_cards(tmppath: str) -> list[dict]:
    logger.info("Parsing eligible cards from bulk data...")
    eligible = []
    with open(tmppath, "rb") as f:
        for card in ijson.items(f, "item"):
            if _is_eligible(card):
                image_uris = card["image_uris"]
                eligible.append({
                    "id": card["id"],
                    "name": card["name"],
                    "set_code": card["set"],
                    "set_name": card.get("set_name", ""),
                    "type_line": card.get("type_line", ""),
                    "color_identity": card.get("color_identity", []),
                    "rarity": card.get("rarity", ""),
                    "art_crop": image_uris["art_crop"],
                    "normal": image_uris.get("normal", ""),
                })
    logger.info(f"{len(eligible)} eligible cards found.")
    return eligible


def generate_boards(cards: list[dict]) -> list[dict]:
    logger.info(f"Generating up to {NUM_BOARDS} boards...")
    random.shuffle(cards)
    boards = []

    for i in range(0, len(cards) - BOARD_SIZE, BOARD_SIZE):
        if len(boards) >= NUM_BOARDS:
            break

        group = cards[i : i + BOARD_SIZE]
        non_group = [c for c in cards if c not in group]
        if len(non_group) < NUM_DISTRACTORS:
            continue

        distractors = random.sample(non_group, NUM_DISTRACTORS)

        photos = [
            {
                "card_id": c["id"],
                "photo_url": c["art_crop"],
                "full_card_url": c["normal"],
                "type_line": c["type_line"],
                "color_identity": c["color_identity"],
            }
            for c in group
        ]
        name_chips = [
            {"chip_id": c["id"], "name": c["name"]}
            for c in group + distractors
        ]
        random.shuffle(name_chips)

        boards.append({
            "board_id": len(boards) + 1,
            "photos": photos,
            "name_chips": name_chips,
            "answer_ids": [c["id"] for c in group],
        })

    logger.info(f"Generated {len(boards)} boards.")
    return boards


def compute_stats(cards: list[dict]) -> dict:
    color_dist = {c: 0 for c in ["W", "U", "B", "R", "G", "C"]}
    type_keys = ["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Land", "Planeswalker"]
    type_dist = {t: 0 for t in type_keys}
    rarity_dist = {"common": 0, "uncommon": 0, "rare": 0, "mythic": 0}
    set_counts: dict[str, dict] = {}

    for card in cards:
        ci = card["color_identity"]
        if not ci:
            color_dist["C"] += 1
        else:
            for c in ci:
                if c in color_dist:
                    color_dist[c] += 1

        tl = card.get("type_line", "")
        for t in type_keys:
            if t in tl:
                type_dist[t] += 1

        r = card.get("rarity", "")
        if r in rarity_dist:
            rarity_dist[r] += 1

        sc = card["set_code"]
        if sc not in set_counts:
            set_counts[sc] = {"set_code": sc, "set_name": card["set_name"], "count": 0}
        set_counts[sc]["count"] += 1

    top_sets = sorted(set_counts.values(), key=lambda x: x["count"], reverse=True)[:10]

    return {
        "total_cards": len(cards),
        "color_distribution": color_dist,
        "type_distribution": type_dist,
        "rarity_distribution": rarity_dist,
        "top_sets": top_sets,
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    download_uri = await fetch_download_uri()
    tmppath = await download_to_temp(download_uri)

    try:
        cards = parse_eligible_cards(tmppath)
    finally:
        os.unlink(tmppath)

    boards = generate_boards(cards)
    stats = compute_stats(cards)

    boards_path = OUTPUT_DIR / "boards.json"
    stats_path = OUTPUT_DIR / "stats.json"

    with open(boards_path, "w") as f:
        json.dump(boards, f, separators=(",", ":"))
    logger.info(f"Wrote {boards_path} ({boards_path.stat().st_size // 1024} KB)")

    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Wrote {stats_path}")


if __name__ == "__main__":
    asyncio.run(main())
