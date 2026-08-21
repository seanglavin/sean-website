"""Builds cards.json from the RiftScribe card API."""

from __future__ import annotations

import logging
from typing import Any, Final

import httpx

from .cardcode import SET_NAMES, code_from_public_code

logger: Final = logging.getLogger(__name__)

API_URL: Final = "https://riftscribe.gg/api/cards"
PAGE_SIZE: Final = 200
SCHEMA_VERSION: Final = 1


def fetch_cards(client: httpx.Client) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    offset = 0
    while True:
        response = client.get(API_URL, params={"limit": PAGE_SIZE, "offset": offset})
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        cards.extend(batch)
        offset += PAGE_SIZE
        logger.info("fetched %d cards", len(cards))
    return cards


def _simplify(card: dict[str, Any]) -> dict[str, Any]:
    stats = card.get("stats") or {}
    thumbs = card.get("image_thumb") or {}
    set_code = card["set_id"]
    return {
        "code": code_from_public_code(card["public_code"]),
        "name": card["name"],
        "set": set_code,
        "set_name": SET_NAMES.get(set_code, set_code),
        "collector_number": card.get("collector_number"),
        "variant": card.get("variant") or None,
        "rarity": card.get("rarity"),
        "type": card.get("type"),
        "domains": card.get("domains") or [],
        "energy": stats.get("energy"),
        "might": stats.get("might"),
        "power": stats.get("power"),
        "image": {
            "small": thumbs.get("small"),
            "medium": thumbs.get("medium"),
            "large": thumbs.get("large") or card.get("image"),
        },
    }


def build_catalog(client: httpx.Client) -> dict[str, Any]:
    raw = fetch_cards(client)
    if not raw:
        raise RuntimeError("RiftScribe returned no cards")

    cards = [_simplify(card) for card in raw]
    cards.sort(key=lambda card: card["code"])

    unknown = sorted({c["set"] for c in cards} - set(SET_NAMES))
    if unknown:
        # A new set ships before SET_NAMES knows its display name; the catalogue
        # still works, but retailer set labels for it will not resolve.
        logger.warning("unknown set codes, add them to SET_NAMES: %s", unknown)

    return {"schema_version": SCHEMA_VERSION, "cards": cards}
