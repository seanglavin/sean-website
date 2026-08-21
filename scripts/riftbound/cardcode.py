"""Canonical Riftbound card identity.

The catalogue's ``public_code`` (``OGN-007a/298``) is authoritative; the part
before the slash is the canonical code every retailer adapter must produce.
"""

from __future__ import annotations

import re
from typing import Final, Literal, NamedTuple

Finish = Literal["nonfoil", "foil"]

SET_NAMES: Final[dict[str, str]] = {
    "OGN": "Origins",
    "OGS": "Origins: Proving Grounds",
    "SFD": "Spiritforged",
    "UNL": "Unleashed",
    "VEN": "Vendetta",
}

# Store-facing set labels, normalised by _normalise_label. Promotional sets are
# deliberately absent: they have no catalogue entry, so listings for them are
# reported as unmatched rather than being forced onto a real card.
SET_ALIASES: Final[dict[str, str]] = {
    "origins": "OGN",
    "origins proving grounds": "OGS",
    "origins: proving grounds": "OGS",
    "proving grounds": "OGS",
    "spiritforged": "SFD",
    "unleashed": "UNL",
    "vendetta": "VEN",
}


class Condition(NamedTuple):
    code: str
    label: str
    grade: int


# Stores use different grading scales; they are preserved rather than collapsed.
# ``grade`` orders comparable conditions across stores for sorting.
CONDITIONS: Final[dict[str, Condition]] = {
    "NM": Condition("NM", "Near Mint", 0),
    "LP": Condition("LP", "Lightly Played", 1),
    "SP": Condition("SP", "Slightly Played", 1),
    "PL": Condition("PL", "Played", 2),
    "MP": Condition("MP", "Moderately Played", 2),
    "HP": Condition("HP", "Heavily Played", 3),
    "DMG": Condition("DMG", "Damaged", 4),
}

_CONDITION_ALIASES: Final[dict[str, str]] = {
    "near mint": "NM",
    "nm": "NM",
    "mint": "NM",
    "lightly played": "LP",
    "lp": "LP",
    "slightly played": "SP",
    "sp": "SP",
    "played": "PL",
    "pl": "PL",
    "moderately played": "MP",
    "mp": "MP",
    "heavily played": "HP",
    "hp": "HP",
    "damaged": "DMG",
    "dmg": "DMG",
    "dm": "DMG",
}

_NUMBER_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<prefix>[A-Za-z]*)(?P<digits>\d+)(?P<suffix>[A-Za-z*]*)$"
)


def _normalise_label(label: str) -> str:
    text = label.strip().strip("[]()").lower()
    text = re.sub(r"^riftbound\s*:?\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def normalise_set(label: str | None) -> str | None:
    """Map a store's set label to a canonical three-letter set code."""
    if not label:
        return None
    key = _normalise_label(label)
    if key.upper() in SET_NAMES:
        return key.upper()
    return SET_ALIASES.get(key)


def normalise_number(number: str | None) -> str | None:
    """Normalise a collector number to its catalogue form.

    Plain numbers are zero-padded to three digits (``45`` -> ``045``). Prefixed
    numbers keep the catalogue's own width (``r04`` -> ``R04``, ``sp1`` -> ``SP1``).
    """
    if not number:
        return None
    raw = number.strip().split("/")[0].strip()
    match = _NUMBER_RE.match(raw)
    if not match:
        return None
    prefix = match.group("prefix").upper()
    digits = match.group("digits")
    suffix = match.group("suffix")
    suffix = suffix if suffix == "*" else suffix.lower()
    if not prefix:
        digits = f"{int(digits):03d}"
    return f"{prefix}{digits}{suffix}"


def canonical_code(set_label: str | None, number: str | None) -> str | None:
    """Build a canonical card code, or None if either half cannot be resolved."""
    set_code = normalise_set(set_label)
    card_number = normalise_number(number)
    if not set_code or not card_number:
        return None
    return f"{set_code}-{card_number}"


def code_from_public_code(public_code: str) -> str:
    """``OGN-007a/298`` -> ``OGN-007a``."""
    return public_code.split("/", 1)[0].strip()


def normalise_condition(label: str | None) -> Condition | None:
    if not label:
        return None
    key = re.sub(r"\s+", " ", label.strip().lower())
    code = _CONDITION_ALIASES.get(key)
    return CONDITIONS[code] if code else None


def detect_finish(*texts: str | None) -> Finish:
    """Foil unless nothing says so. ``Non-Foil`` must not read as ``Foil``."""
    for text in texts:
        if not text:
            continue
        lowered = text.lower()
        without_negatives = re.sub(r"non[\s-]*foil|normal", "", lowered)
        if "foil" in without_negatives:
            return "foil"
    return "nonfoil"
