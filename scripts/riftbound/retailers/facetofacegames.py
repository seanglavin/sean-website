"""Face to Face Games — Shopify, NM/PL conditions.

The title carries the cleanest identity (``Defy - 045/298 [Origins] [Non-Foil]``).
The SKU is not used for the set because promotional printings prefix it
(``SIN-RBD-PORGOGN-183-...``), and those cards have no catalogue entry anyway.
"""

from __future__ import annotations

import re
from typing import Any, Final

import httpx

from ..cardcode import canonical_code, detect_finish
from .base import FetchResult, Offer
from .shopify import iter_products, variant_offers

_TITLE_RE: Final = re.compile(r"-\s*(?P<number>[A-Za-z]*\d+[A-Za-z*]*)\s*/\s*\d+\s*\[(?P<set>[^\]]+)\]")


class FaceToFaceGames:
    id = "facetofacegames"
    name = "Face to Face Games"
    site_url = "https://facetofacegames.com"
    currency = "CAD"
    product_url_template = "https://facetofacegames.com/products/{handle}"
    collection = "riftbound-singles"

    def fetch(self, client: httpx.Client) -> FetchResult:
        offers: list[Offer] = []
        unmatched: list[str] = []
        for product in iter_products(client, self.site_url, self.collection):
            code = _identify(product)
            if not code:
                unmatched.append(product["title"])
                continue
            finish = detect_finish(product["title"])
            offers.extend(variant_offers(product, code, finish))
        return FetchResult(offers, unmatched)


def _identify(product: dict[str, Any]) -> str | None:
    match = _TITLE_RE.search(product.get("title", ""))
    if not match:
        return None
    return canonical_code(match.group("set"), match.group("number"))


RETAILER = FaceToFaceGames()
