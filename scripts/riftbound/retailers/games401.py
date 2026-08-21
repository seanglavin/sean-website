"""401 Games — Shopify, NM/SP/MP conditions.

Set and finish come from its structured tags (``Set_Riftbound: Vendetta``,
``Finish_Foil``); the collector number comes from the title. Its SKU is the
least regular of the three (``RFB-004-VEN-R04SP`` folds the condition in), so
it is not used for identity.
"""

from __future__ import annotations

import re
from typing import Any, Final

import httpx

from ..cardcode import canonical_code, detect_finish
from .base import FetchResult, Offer
from .shopify import iter_products, tag_value, variant_offers

_TITLE_RE: Final = re.compile(r"-\s*(?P<number>[A-Za-z]*\d+[A-Za-z*]*)\s*/\s*\d+")


class Games401:
    id = "games401"
    name = "401 Games"
    site_url = "https://store.401games.ca"
    currency = "CAD"
    product_url_template = "https://store.401games.ca/products/{handle}"
    collection = "riftbound-league-of-legends-singles"

    def fetch(self, client: httpx.Client) -> FetchResult:
        offers: list[Offer] = []
        unmatched: list[str] = []
        for product in iter_products(client, self.site_url, self.collection):
            code = _identify(product)
            if not code:
                unmatched.append(product["title"])
                continue
            finish = detect_finish(tag_value(product, "Finish_"), product["title"])
            offers.extend(variant_offers(product, code, finish))
        return FetchResult(offers, unmatched)


def _identify(product: dict[str, Any]) -> str | None:
    match = _TITLE_RE.search(product.get("title", ""))
    if not match:
        return None
    return canonical_code(tag_value(product, "Set_"), match.group("number"))


RETAILER = Games401()
