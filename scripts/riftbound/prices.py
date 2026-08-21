"""Builds prices/<retailer>.json from a retailer's offers.

Offers are grouped by card code and printing, and prices are stored as integer
cents, so the committed file stays compact and its daily diff stays small.
Listings whose card is absent from the catalogue (promotional printings, signed
variants) are counted, not dropped silently.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .manifest import now_iso
from .retailers import Offer, Retailer

SCHEMA_VERSION = 1


def build_prices(
    retailer: Retailer,
    offers: list[Offer],
    unmatched: list[str],
    known_codes: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return the price payload and a coverage summary for reporting."""
    grouped: dict[str, dict[tuple[str, str], list[Offer]]] = defaultdict(
        lambda: defaultdict(list)
    )
    absent: list[str] = []
    kept = 0

    for offer in offers:
        if offer.code not in known_codes:
            absent.append(offer.code)
            continue
        grouped[offer.code][(offer.finish, offer.handle)].append(offer)
        kept += 1

    cards: dict[str, list[dict[str, Any]]] = {}
    for code, printings in grouped.items():
        entries = []
        for (finish, handle), group in printings.items():
            group.sort(key=lambda item: (item.grade, item.condition))
            entries.append(
                {
                    "finish": finish,
                    "handle": handle,
                    "offers": [
                        [item.condition, item.grade, item.price_cents, item.available]
                        for item in group
                    ],
                }
            )
        entries.sort(key=lambda entry: (entry["finish"], entry["handle"]))
        cards[code] = entries

    payload = {
        "schema_version": SCHEMA_VERSION,
        "retailer_id": retailer.id,
        "generated_at": now_iso(),
        "product_url_template": retailer.product_url_template,
        "currency": retailer.currency,
        "cards": cards,
    }
    summary = {
        "retailer_id": retailer.id,
        "offers_kept": kept,
        "cards_covered": len(cards),
        "offers_absent_from_catalogue": len(absent),
        "products_unparsed": len(unmatched),
        "unparsed_samples": sorted(unmatched)[:25],
        "absent_code_samples": sorted(set(absent))[:25],
    }
    return payload, summary
