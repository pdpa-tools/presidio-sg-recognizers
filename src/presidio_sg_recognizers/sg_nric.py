"""Singapore NRIC recognizer with checksum validation.

NRIC format: prefix (S or T) + 7 digits + checksum letter.
- S prefix: citizens and PRs born before 1 January 2000.
- T prefix: citizens and PRs born on or after 1 January 2000.

The checksum logic lives in `presidio_sg_recognizers._checksum` so it
can be unit-tested without standing up Presidio's analyzer engine. This
module is the Presidio integration layer: a `PatternRecognizer` subclass
that registers the format regex and uses `_checksum.is_valid_nric_fin`
in `validate_result` to drop format-only false positives.

The Presidio dependency is imported lazily so the package itself can be
imported in environments where presidio-analyzer is not installed.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from presidio_sg_recognizers._checksum import is_valid_nric_fin

if TYPE_CHECKING:
    from presidio_analyzer import PatternRecognizer

# Entity type emitted by this recognizer.
SG_NRIC_ENTITY: str = "SG_NRIC"

# Format regex: bounded so adjacent alphanumerics don't bleed in. Case
# insensitive at scan time; checksum validation normalises to uppercase.
_NRIC_REGEX: str = r"\b[STst][0-9]{7}[A-Za-z]\b"

# Context terms that boost detection confidence when found nearby.
_CONTEXT: tuple[str, ...] = (
    "NRIC",
    "IC",
    "identification",
    "identity card",
    "Singapore",
)


def build_recognizer() -> PatternRecognizer:
    """Return a Presidio PatternRecognizer for Singapore NRIC numbers.

    Lazy-imports presidio_analyzer so this module remains importable
    without presidio installed.
    """
    from presidio_analyzer import Pattern, PatternRecognizer

    class _SGNricRecognizer(PatternRecognizer):
        def validate_result(self, pattern_text: str) -> bool:
            # Strip word-boundary whitespace defensively, even though the
            # regex already excludes them via \b.
            return is_valid_nric_fin(pattern_text.strip())

    return _SGNricRecognizer(
        supported_entity=SG_NRIC_ENTITY,
        patterns=[
            Pattern(
                name="SG_NRIC (S/T series)",
                regex=_NRIC_REGEX,
                # Conservative score; Presidio's calibration starts from
                # here and validate_result either keeps or drops.
                score=0.85,
            ),
        ],
        context=list(_CONTEXT),
        supported_language="en",
    )


# Re-export for convenience and for tests that want to bypass Presidio
# entirely.
NRIC_FORMAT_RE: re.Pattern[str] = re.compile(_NRIC_REGEX)
