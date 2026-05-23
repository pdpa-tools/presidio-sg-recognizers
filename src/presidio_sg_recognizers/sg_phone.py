"""Singapore phone number recognizer.

Recognised forms:
- Mobile: 8 or 9 prefix + 7 more digits (e.g. 8123 4567, 9123 4567).
- Landline: 6 prefix + 7 more digits.
- Voip: 3 prefix + 7 more digits (introduced ~2010).
- With country code: optional +65 or 0065 prefix, with optional
  whitespace, hyphens, or brackets between groupings.

Generic-looking 8-digit sequences without the leading SG prefix
constraint are not matched. Presidio's built-in PHONE_NUMBER recogniser
is too permissive for the SG context (it flags 8-digit dates, unit
numbers, and ID numbers), which is why this custom one exists.

Same lazy-Presidio-import pattern as the other SG recognisers.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from presidio_analyzer import PatternRecognizer

SG_PHONE_ENTITY: str = "SG_PHONE"

# Country code: optional +65 or 0065, with optional whitespace or hyphen
# after.
_CC: str = r"(?:\+?65|0065)?[\s\-]?"

# Local-number body: a single leading digit from {3, 6, 8, 9}, followed
# by 7 more digits, with optional single space or hyphen after the 4th
# digit (the conventional SG visual grouping like 9123 4567).
_LOCAL: str = r"[3689]\d{3}[\s\-]?\d{4}"

# Optional surrounding parentheses around the country code, e.g.
# "(+65) 9123 4567".
_PHONE_REGEX: str = rf"\(?{_CC}\)?{_LOCAL}"

_CONTEXT: tuple[str, ...] = (
    "phone",
    "mobile",
    "tel",
    "telephone",
    "contact",
    "call",
    "DID",
    "Singapore",
)


def build_recognizer() -> PatternRecognizer:
    """Return a Presidio PatternRecognizer for Singapore phone numbers."""
    from presidio_analyzer import Pattern, PatternRecognizer

    return PatternRecognizer(
        supported_entity=SG_PHONE_ENTITY,
        patterns=[
            Pattern(
                name="SG phone (3/6/8/9 prefix, optional +65)",
                regex=_PHONE_REGEX,
                # Lower than NRIC/FIN because there is no checksum to
                # confirm. Downstream pipelines (such as an LLM-as-judge
                # layer) can disambiguate ambiguous 8-digit-shaped
                # strings in context.
                score=0.6,
            ),
        ],
        context=list(_CONTEXT),
        supported_language="en",
    )


PHONE_FORMAT_RE: re.Pattern[str] = re.compile(_PHONE_REGEX)
