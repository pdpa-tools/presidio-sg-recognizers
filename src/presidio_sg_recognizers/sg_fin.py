"""Singapore FIN (Foreign Identification Number) recognizer with checksum.

FIN format: prefix (F, G, or M) + 7 digits + checksum letter.
- F: foreigners issued long-term passes before 1 January 2000.
- G: foreigners issued long-term passes 2000 through 2021.
- M: foreigners issued long-term passes from 1 January 2022 onwards.

The M-series uses a +3 offset and a distinct lookup table compared to
F/G (+4 offset, legacy table). All three are validated by the same
`is_valid_nric_fin` function in `presidio_sg_recognizers._checksum`.

Same lazy-Presidio-import pattern as `sg_nric.py`.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from presidio_sg_recognizers._checksum import is_valid_nric_fin

if TYPE_CHECKING:
    from presidio_analyzer import PatternRecognizer

# Entity type emitted by this recognizer. NRIC and FIN are deliberately
# emitted under distinct entity types so downstream pipelines can choose
# whether to treat them as one class or two.
SG_FIN_ENTITY: str = "SG_FIN"

# Format regex covers all three FIN series in one pattern: F, G, M.
_FIN_REGEX: str = r"\b[FGMfgm][0-9]{7}[A-Za-z]\b"

# Context terms that boost detection confidence when found nearby.
_CONTEXT: tuple[str, ...] = (
    "FIN",
    "foreign identification",
    "work permit",
    "S Pass",
    "Employment Pass",
    "long-term pass",
    "Singapore",
)


def build_recognizer() -> PatternRecognizer:
    """Return a Presidio PatternRecognizer for Singapore FIN numbers.

    Lazy-imports presidio_analyzer so this module remains importable
    without presidio installed.
    """
    from presidio_analyzer import Pattern, PatternRecognizer

    class _SGFinRecognizer(PatternRecognizer):
        def validate_result(self, pattern_text: str) -> bool:
            return is_valid_nric_fin(pattern_text.strip())

    return _SGFinRecognizer(
        supported_entity=SG_FIN_ENTITY,
        patterns=[
            Pattern(
                name="SG_FIN (F/G/M series)",
                regex=_FIN_REGEX,
                score=0.85,
            ),
        ],
        context=list(_CONTEXT),
        supported_language="en",
    )


FIN_FORMAT_RE: re.Pattern[str] = re.compile(_FIN_REGEX)
