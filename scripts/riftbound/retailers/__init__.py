"""Retailer registry.

Adding a Canadian store is one module plus one line here. The frontend reads
the manifest, so no frontend change is needed.
"""

from __future__ import annotations

from typing import Final

from . import facetofacegames, games401, tapsgames
from .base import FetchResult, Offer, Retailer

REGISTRY: Final[dict[str, Retailer]] = {
    retailer.id: retailer
    for retailer in (tapsgames.RETAILER, facetofacegames.RETAILER, games401.RETAILER)
}

__all__ = ["REGISTRY", "FetchResult", "Offer", "Retailer"]
