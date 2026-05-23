"""Internal-code recognizer with configurable per-organisation pattern.

Matches short alphanumeric codes that organisations use to identify
internal units, projects, departments, cost centres, clinical concepts,
or academic modules. Examples across deployment contexts:

- Enterprise: cost-centre codes like `FIN2026`, project codes like
  `PRJ4015`, employee-grade codes like `LVL5024`.
- SMB: department codes like `OPS1001`, client-engagement codes like
  `CLI2099`, sprint codes like `SPR2026`.
- Healthcare: clinical-service codes like `MED1234`, drug-formulary codes
  like `DRG2007`, internal procedure codes like `PRC3015`. (Note: this
  recognizer does not specifically target ICD-10 diagnosis codes; those
  have their own shape and warrant a dedicated recognizer if needed.)
- Educational: course or module codes like `INF2007`, `ICT1001`, `LAW3015`.

Default pattern: three uppercase letters followed by four digits, which
fits all four contexts above. Letter and digit counts are configurable
per call site by passing `prefix_letters` and `digit_count` to
`build_recognizer()`.

These codes are pseudonymised because in combination with date, team, or
cohort information they can re-identify a specific individual (an
employee on a specific team in a specific quarter, a patient under a
specific consultant, a member in a specific cohort) even when names have
been scrubbed.

Same lazy-Presidio-import pattern as the other recognisers.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from presidio_analyzer import PatternRecognizer

INTERNAL_CODE_ENTITY: str = "INTERNAL_CODE"

# Default pattern: three uppercase letters then four digits, bounded so
# longer identifiers don't accidentally match.
_DEFAULT_REGEX: str = r"\b[A-Z]{3}\d{4}\b"

_CONTEXT: tuple[str, ...] = (
    # Enterprise / SMB context words
    "cost centre",
    "cost-centre",
    "department",
    "project code",
    "GL code",
    "budget code",
    "engagement",
    # Healthcare context words
    "ward",
    "clinic",
    "consultant",
    "procedure",
    "diagnosis",
    "drug",
    "formulary",
    # Educational context words
    "course",
    "module",
    "subject",
    "elective",
    "syllabus",
    "credits",
    "prerequisite",
    # Shared
    "code",
    "ID",
    "reference",
)


def build_recognizer(
    prefix_letters: int = 3,
    digit_count: int = 4,
) -> PatternRecognizer:
    """Return a Presidio PatternRecognizer for internal codes.

    Parameters
    ----------
    prefix_letters : int
        Number of leading uppercase letters in the code pattern.
        Default 3 (fits common conventions across enterprise, SMB,
        healthcare, and educational deployments).
    digit_count : int
        Number of trailing decimal digits. Default 4.
    """
    from presidio_analyzer import Pattern, PatternRecognizer

    regex = (
        rf"\b[A-Z]{{{prefix_letters}}}\d{{{digit_count}}}\b"
        if (prefix_letters, digit_count) != (3, 4)
        else _DEFAULT_REGEX
    )

    return PatternRecognizer(
        supported_entity=INTERNAL_CODE_ENTITY,
        patterns=[
            Pattern(
                name=f"internal code ({prefix_letters}L+{digit_count}D)",
                regex=regex,
                # Mid score: the format is distinctive but the same
                # shape appears in product codes and serial numbers, so
                # the context boost from nearby domain-specific words
                # is the main signal.
                score=0.55,
            ),
        ],
        context=list(_CONTEXT),
        supported_language="en",
    )


INTERNAL_CODE_FORMAT_RE: re.Pattern[str] = re.compile(_DEFAULT_REGEX)
