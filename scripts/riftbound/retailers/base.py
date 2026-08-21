from __future__ import annotations

from typing import Any, NamedTuple, Protocol

import httpx

from ..cardcode import Finish


class Offer(NamedTuple):
    """One purchasable condition of one printing at one store."""

    code: str
    finish: Finish
    condition: str
    grade: int
    price_cents: int
    available: bool
    handle: str


class FetchResult(NamedTuple):
    offers: list[Offer]
    unmatched: list[str]


class Retailer(Protocol):
    id: str
    name: str
    site_url: str
    currency: str
    product_url_template: str

    def fetch(self, client: httpx.Client) -> FetchResult: ...


def to_cents(price: Any) -> int | None:
    try:
        return round(float(price) * 100)
    except (TypeError, ValueError):
        return None
