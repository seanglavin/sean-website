#!/usr/bin/env python3
"""Generates the Riftbound dashboard's static data.

Run manually or from .github/workflows/riftbound-data.yml:

    python scripts/riftbound/generate.py --all
    python scripts/riftbound/generate.py --catalog
    python scripts/riftbound/generate.py --prices --retailer tapsgames

A retailer that fails is recorded in the manifest as "error" and keeps its
previous data file; it never fails the run, because a broken store must not be
able to block the site's deploy.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Final

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from riftbound import manifest as manifest_module
from riftbound.catalog import build_catalog
from riftbound.jsonio import read_json, write_json
from riftbound.paths import CARDS_FILE, PRICES_DIR, REPORT_FILE
from riftbound.prices import build_prices
from riftbound.retailers import REGISTRY

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger: Final = logging.getLogger("riftbound")

TIMEOUT: Final = httpx.Timeout(30.0, connect=15.0)
HEADERS: Final = {"User-Agent": "skglavin.com Riftbound dashboard (+https://skglavin.com)"}


def _client() -> httpx.Client:
    return httpx.Client(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True)


def generate_catalog(client: httpx.Client, manifest: dict[str, Any]) -> None:
    catalog = build_catalog(client)
    write_json(CARDS_FILE, catalog)
    cards = catalog["cards"]
    manifest["catalog"] = {
        "file": "cards.json",
        "card_count": len(cards),
        "sets": sorted({card["set"] for card in cards}),
        "generated_at": manifest_module.now_iso(),
    }
    logger.info("catalogue: %d cards", len(cards))


def _known_codes() -> set[str]:
    catalog = read_json(CARDS_FILE)
    if not catalog:
        raise RuntimeError("cards.json is missing; run with --catalog first")
    return {card["code"] for card in catalog["cards"]}


# A store that quietly returns nothing must not overwrite good data. Shopify
# answers 200 with an empty product list for a renamed collection handle, so
# an empty or sharply collapsed result is treated as a failure, not a scrape
# that legitimately found no stock.
COLLAPSE_RATIO: Final = 0.5


def _previous_listing_count(manifest: dict[str, Any], retailer_id: str) -> int:
    for entry in manifest.get("retailers", []):
        if entry["id"] == retailer_id and entry.get("status") == "ok":
            return int(entry.get("listing_count") or 0)
    return 0


def _check_plausible(manifest: dict[str, Any], retailer_id: str, count: int) -> None:
    if count == 0:
        raise RuntimeError("returned no matched offers")
    previous = _previous_listing_count(manifest, retailer_id)
    if previous and count < previous * COLLAPSE_RATIO:
        raise RuntimeError(f"offers collapsed from {previous} to {count}")


def generate_prices(
    client: httpx.Client, manifest: dict[str, Any], retailer_ids: list[str]
) -> list[dict[str, Any]]:
    known = _known_codes()
    summaries: list[dict[str, Any]] = []

    for retailer_id in retailer_ids:
        retailer = REGISTRY[retailer_id]
        try:
            result = retailer.fetch(client)
            payload, summary = build_prices(retailer, result.offers, result.unmatched, known)
            _check_plausible(manifest, retailer_id, summary["offers_kept"])
        except Exception as error:  # noqa: BLE001 - one store must not stop the rest
            logger.error("%s failed: %s", retailer_id, error)
            manifest_module.mark_failed(manifest, retailer_id, retailer.name, str(error))
            continue

        relative = f"prices/{retailer.id}.json"
        write_json(PRICES_DIR / f"{retailer.id}.json", payload)
        manifest_module.merge_retailer(
            manifest,
            {
                "id": retailer.id,
                "name": retailer.name,
                "site_url": retailer.site_url,
                "currency": retailer.currency,
                "file": relative,
                "generated_at": payload["generated_at"],
                "cards_covered": summary["cards_covered"],
                "listing_count": summary["offers_kept"],
                "status": "ok",
            },
        )
        summaries.append(summary)
        logger.info(
            "%s: %d offers across %d cards (%d products unparsed, %d absent from catalogue)",
            retailer.id,
            summary["offers_kept"],
            summary["cards_covered"],
            summary["products_unparsed"],
            summary["offers_absent_from_catalogue"],
        )
    return summaries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", action="store_true", help="regenerate cards.json")
    parser.add_argument("--prices", action="store_true", help="regenerate retailer prices")
    parser.add_argument("--all", action="store_true", help="both of the above")
    parser.add_argument(
        "--retailer",
        action="append",
        choices=sorted(REGISTRY),
        help="limit --prices to one retailer (repeatable)",
    )
    args = parser.parse_args()

    do_catalog = args.catalog or args.all
    do_prices = args.prices or args.all
    if not do_catalog and not do_prices:
        parser.error("pass --catalog, --prices, or --all")

    manifest = manifest_module.load()
    summaries: list[dict[str, Any]] = []

    with _client() as client:
        if do_catalog:
            generate_catalog(client, manifest)
        if do_prices:
            summaries = generate_prices(client, manifest, args.retailer or sorted(REGISTRY))

    manifest_module.save(manifest)
    if summaries:
        write_json(REPORT_FILE, {"retailers": summaries})
        logger.info("coverage report: %s", REPORT_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
