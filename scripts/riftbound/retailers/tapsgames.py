"""Taps Games — Shopify, five graded conditions per printing.

Identity comes from the ``Number_`` tag and the title's set bracket, never the
SKU: the SKU's set field is a single letter (``RIF-V-189*/166-F-...``), which
will collide as soon as two sets share an initial.
"""

from __future__ import annotations

import re
from typing import Any, Final

import httpx

from ..cardcode import canonical_code, detect_finish
from .base import FetchResult, Offer
from .shopify import iter_products, tag_value, variant_offers

_SET_RE: Final = re.compile(r"\[([^\]]+)\]")

# Its collection metadata is unreliable (the handle
# "riftbound-singles-discounted-copy" is titled "Star Wars Singles Discounted"),
# so products are filtered on product_type and the Brand_ tag instead.
PRODUCT_TYPE: Final = "Riftbound Singles"
BRAND_TAG: Final = "Brand_Riftbound"


class TapsGames:
    id = "tapsgames"
    name = "Taps Games"
    site_url = "https://tapsgames.com"
    currency = "CAD"
    product_url_template = "https://tapsgames.com/products/{handle}"
    collection = "riftbound-singles"

    def fetch(self, client: httpx.Client) -> FetchResult:
        offers: list[Offer] = []
        unmatched: list[str] = []
        for product in iter_products(client, self.site_url, self.collection):
            if not _is_riftbound_single(product):
                continue
            code = _identify(product)
            if not code:
                unmatched.append(product["title"])
                continue
            finish = detect_finish(product["title"], tag_value(product, "Finish_"))
            offers.extend(variant_offers(product, code, finish))
        return FetchResult(offers, unmatched)


def _is_riftbound_single(product: dict[str, Any]) -> bool:
    return product.get("product_type") == PRODUCT_TYPE and BRAND_TAG in product.get("tags", [])


def _identify(product: dict[str, Any]) -> str | None:
    number = tag_value(product, "Number_")
    match = _SET_RE.search(product.get("title", ""))
    return canonical_code(match.group(1) if match else None, number)


RETAILER = TapsGames()
