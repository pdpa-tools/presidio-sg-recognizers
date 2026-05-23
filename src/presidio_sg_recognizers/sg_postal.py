"""Singapore postal code recognizer.

Singapore postal codes are exactly 6 digits with no internal separators.
A bare 6-digit number is too ambiguous to flag on its own (phone
last-six, reference numbers, year-month concatenations), so this
recogniser relies on Presidio's context-boosting mechanism: the score is
set low at the regex layer, and address-shaped context words nearby
(e.g. "Singapore", "Blk", street suffixes) elevate it into the
detection range.

When context is absent the recogniser still produces a candidate; it is
the consuming pipeline's responsibility to set an appropriate score
threshold. Downstream layers (such as an LLM-as-judge) can pick up
genuinely-ambiguous cases.

Same lazy-Presidio-import pattern as the other SG recognisers.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from presidio_analyzer import PatternRecognizer

SG_POSTAL_ENTITY: str = "SG_POSTAL"

# Six contiguous digits. Word boundaries on both sides prevent matches
# inside longer numeric runs (NRIC digits, account numbers, dates as
# YYYYMMDD).
_POSTAL_REGEX: str = r"\b\d{6}\b"

# Context terms that elevate a bare 6-digit string to a likely postal
# code. Presidio's analyzer engine boosts the recogniser score when any
# of these appear within the proximity window.
_CONTEXT: tuple[str, ...] = (
    "Singapore",
    "postal",
    "postcode",
    "post code",
    "zip",
    "address",
    "Blk",
    "Block",
    "Road",
    "Street",
    "Avenue",
    "Lane",
    "Drive",
    "Crescent",
    "Boulevard",
    "Walk",
    "Way",
    "Circle",
    "Place",
    "Park",
)


def build_recognizer() -> PatternRecognizer:
    """Return a Presidio PatternRecognizer for Singapore postal codes."""
    from presidio_analyzer import Pattern, PatternRecognizer

    return PatternRecognizer(
        supported_entity=SG_POSTAL_ENTITY,
        patterns=[
            Pattern(
                name="SG postal code (6 digits with context)",
                regex=_POSTAL_REGEX,
                # Low base score; Presidio's context-boost mechanism
                # raises this when address-shaped surroundings are
                # present. Bare 6-digit numbers default to dropped.
                score=0.3,
            ),
        ],
        context=list(_CONTEXT),
        supported_language="en",
    )


POSTAL_FORMAT_RE: re.Pattern[str] = re.compile(_POSTAL_REGEX)
