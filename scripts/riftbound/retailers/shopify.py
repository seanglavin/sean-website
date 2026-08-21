"""Shared Shopify /products.json paging.

All three launch retailers run Shopify, so each adapter is only an identity
parser on top of this.
"""

from __future__ import annotations

import logging
from typing import Any, Final, Iterator

import httpx

from ..cardcode import normalise_condition
from .base import Offer, to_cents

logger: Final = logging.getLogger(__name__)

PAGE_SIZE: Final = 250
MAX_PAGES: Final = 40


def iter_products(
    client: httpx.Client, site_url: str, collection: str
) -> Iterator[dict[str, Any]]:
    url = f"{site_url.rstrip('/')}/collections/{collection}/products.json"
    for page in range(1, MAX_PAGES + 1):
        response = client.get(url, params={"limit": PAGE_SIZE, "page": page})
        response.raise_for_status()
        products = response.json().get("products", [])
        if not products:
            return
        yield from products
        if len(products) < PAGE_SIZE:
            return
    logger.warning("%s/%s hit the %d page cap", site_url, collection, MAX_PAGES)


def tag_value(product: dict[str, Any], prefix: str) -> str | None:
    for tag in product.get("tags", []):
        if tag.startswith(prefix):
            return tag[len(prefix) :]
    return None


def variant_offers(
    product: dict[str, Any], code: str, finish: str
) -> list[Offer]:
    """Flatten a product's condition variants into offers.

    Variants whose title is not a recognised condition (Shopify's
    "Default Title" on scan/bulk products) carry no grading and are dropped.
    """
    handle = product["handle"]
    offers: list[Offer] = []
    for variant in product.get("variants", []):
        condition = normalise_condition(variant.get("title"))
        cents = to_cents(variant.get("price"))
        if condition is None or cents is None:
            continue
        offers.append(
            Offer(
                code=code,
                finish=finish,
                condition=condition.code,
                grade=condition.grade,
                price_cents=cents,
                available=bool(variant.get("available")),
                handle=handle,
            )
        )
    return offers
