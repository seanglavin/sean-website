"""Real store strings from Face to Face, Taps Games, and 401 Games.

Every fixture below was captured from a live products.json response, so a
failure here means a store changed its scheme, not that a mock drifted.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from riftbound.cardcode import (
    canonical_code,
    code_from_public_code,
    detect_finish,
    normalise_condition,
    normalise_number,
    normalise_set,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Origins", "OGN"),
        ("[Origins]", "OGN"),
        ("Origins: Proving Grounds", "OGS"),
        ("Origins Proving Grounds", "OGS"),
        ("Riftbound: Origins: Proving Grounds", "OGS"),
        ("Riftbound: Vendetta", "VEN"),
        ("Spiritforged", "SFD"),
        ("Unleashed", "UNL"),
        ("VEN", "VEN"),
        ("Riftbound Organized Play Promotional Cards", None),
        ("Riftbound Judge Promotional Cards", None),
        ("Collector's Corner", None),
        (None, None),
    ],
)
def test_normalise_set(label: str | None, expected: str | None) -> None:
    assert normalise_set(label) == expected


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        ("45", "045"),
        ("045", "045"),
        ("7", "007"),
        ("045/298", "045"),
        ("189*/166", "189*"),
        ("126b", "126b"),
        ("007a", "007a"),
        ("r04", "R04"),
        ("R04a", "R04a"),
        ("sp1", "SP1"),
        ("T01", "T01"),
        ("", None),
        ("not-a-number", None),
    ],
)
def test_normalise_number(number: str, expected: str | None) -> None:
    assert normalise_number(number) == expected


@pytest.mark.parametrize(
    ("public_code", "expected"),
    [
        ("OGN-007a/298", "OGN-007a"),
        ("OGN-299*/298", "OGN-299*"),
        ("UNL-T01", "UNL-T01"),
        ("VEN-SP1/006", "VEN-SP1"),
        ("VEN-R01", "VEN-R01"),
    ],
)
def test_code_from_public_code(public_code: str, expected: str) -> None:
    assert code_from_public_code(public_code) == expected


@pytest.mark.parametrize(
    ("set_label", "number", "expected"),
    [
        # Face to Face: "Defy - 045/298 [Origins] [Non-Foil]"
        ("Origins", "045/298", "OGN-045"),
        # Taps Games: tag "Number_189*/166", title "[Vendetta]"
        ("Vendetta", "189*/166", "VEN-189*"),
        # 401 Games: tag "Set_Riftbound: Vendetta", title "- 106/166 -"
        ("Riftbound: Vendetta", "106/166", "VEN-106"),
        # Promotional cards have no catalogue entry and must not be forced onto one.
        ("Riftbound Organized Play Promotional Cards", "183/298", None),
    ],
)
def test_canonical_code(set_label: str, number: str, expected: str | None) -> None:
    assert canonical_code(set_label, number) == expected


def test_signature_variant_never_merges_with_base_printing() -> None:
    """A $3,750 signed Akali must not join onto the base card's price row."""
    signature = canonical_code("Vendetta", "189*/166")
    base = canonical_code("Vendetta", "189/166")
    assert signature == "VEN-189*"
    assert base == "VEN-189"
    assert signature != base


def test_showcase_variant_never_merges_with_base_printing() -> None:
    assert canonical_code("Origins", "007a") != canonical_code("Origins", "007")


@pytest.mark.parametrize(
    ("texts", "expected"),
    [
        (("Defy - 045/298 [Origins] [Non-Foil]",), "nonfoil"),
        (("Tideturner - 199/298 [Origins] [Foil]",), "foil"),
        (("Akali - Rogue Assassin (Signature) (189*/166) [Vendetta] Foil",), "foil"),
        (("Wind and Ghosts - 106/166 - Uncommon (Foil)",), "foil"),
        (("Wind and Ghosts - 106/166 - Uncommon",), "nonfoil"),
        (("Finish_Normal",), "nonfoil"),
        (("Finish_Foil",), "foil"),
        ((None, "Jayce, Hammer in Hand - 088/166 - Rare"), "nonfoil"),
    ],
)
def test_detect_finish(texts: tuple[str | None, ...], expected: str) -> None:
    assert detect_finish(*texts) == expected


@pytest.mark.parametrize(
    ("label", "code", "grade"),
    [
        ("Near Mint", "NM", 0),
        ("NM", "NM", 0),
        ("Lightly Played", "LP", 1),
        ("SP", "SP", 1),
        ("PL", "PL", 2),
        ("Moderately Played", "MP", 2),
        ("Heavily Played", "HP", 3),
        ("Damaged", "DMG", 4),
    ],
)
def test_normalise_condition(label: str, code: str, grade: int) -> None:
    condition = normalise_condition(label)
    assert condition is not None
    assert condition.code == code
    assert condition.grade == grade


def test_unknown_condition_is_rejected() -> None:
    assert normalise_condition("Default Title") is None
