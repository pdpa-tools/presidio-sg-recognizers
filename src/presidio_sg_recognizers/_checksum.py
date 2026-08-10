"""Singapore NRIC / FIN checksum algorithm (pure functions).

This module is the load-bearing piece of the Singapore identifier
recognisers. It implements the weighted-sum + prefix-offset + lookup-table
algorithm that ICA uses to compute the trailing checksum letter of a
9-character NRIC or FIN.

Design notes:

- This module is import-safe with zero third-party dependencies. The
  Presidio `PatternRecognizer` wrappers in `sg_nric.py` and `sg_fin.py`
  call into this module's pure functions. That separation lets the
  algorithm be tested in isolation without standing up Presidio's
  analyzer engine.

- The identifier structure (prefix from {S, T, F, G, M}, seven decimal
  digits, trailing checksum letter) is publicly documented on the
  National Registration Identity Card Wikipedia article. The checksum
  algorithm itself is not officially published by ICA; the
  implementation here uses the community-reverse-engineered tables that
  agree across multiple independent implementations (Ngiam 2004,
  samliew's `singapore-nric` library, others). See `ATTRIBUTIONS.md`
  for the project's full provenance stance. The lookup tables and
  modular arithmetic used here are not subject to copyright.

- All three currently-issued series are supported:
    S / T  -> NRIC (citizens and PRs; T-cutoff 1 January 2000)
    F / G  -> FIN, legacy (foreigners; G-cutoff 1 January 2000)
    M      -> FIN, current (foreigners issued long-term passes
                            from 1 January 2022)

- Empirically verified (May 2026): F, G, and M all use the same
  11-letter lookup table; they differ only in the prefix offset added
  to the weighted sum. Earlier community write-ups sometimes claim
  three distinct tables; cross-checking against 15 samples validated
  by samliew's online NRIC validator
  (https://samliew.com/singapore-nric-validator) disproves that. The
  samples are pinned as `SAMLIEW_VALIDATED_SAMPLES` in
  `tests/test_checksum.py`, alongside hand-verified fixtures and
  property tests covering the full input space.
"""

from __future__ import annotations

# The seven-digit weight vector applied to the numeric portion of the
# identifier, in order from leftmost to rightmost digit.
_WEIGHTS: tuple[int, ...] = (2, 7, 6, 5, 4, 3, 2)

# Per-prefix offset added to the weighted sum before the modulo step.
# S and F: no offset. T and G: +4. M: +3.
_PREFIX_OFFSET: dict[str, int] = {
    "S": 0,
    "T": 4,
    "F": 0,
    "G": 4,
    "M": 3,
}

# Lookup tables mapping (weighted_sum + offset) mod 11 to the expected
# trailing checksum letter. Two distinct tables: one for NRIC (S/T)
# and one for FIN (F/G/M; same letters across all three FIN series,
# differentiated only by the prefix offset above). Indexed by remainder,
# 0 through 10.
_NRIC_TABLE: str = "JZIHGFEDCBA"
_FIN_TABLE: str = "XWUTRQPNMLK"


def expected_checksum(prefix: str, digits: str) -> str:
    """Compute the expected trailing checksum letter for an NRIC/FIN.

    Parameters
    ----------
    prefix : str
        Single uppercase letter, one of "S", "T", "F", "G", "M".
    digits : str
        Exactly seven decimal digits as a string.

    Returns
    -------
    str
        Single uppercase checksum letter.

    Raises
    ------
    ValueError
        If `prefix` is not a recognised series letter, or if `digits` is
        not exactly seven decimal characters.
    """
    if prefix not in _PREFIX_OFFSET:
        raise ValueError(f"unknown prefix {prefix!r}; expected one of S, T, F, G, M")
    if len(digits) != 7 or not digits.isdigit():
        raise ValueError(f"digits must be exactly seven decimal characters, got {digits!r}")

    weighted = sum(int(d) * w for d, w in zip(digits, _WEIGHTS, strict=True))
    weighted += _PREFIX_OFFSET[prefix]
    remainder = weighted % 11

    table = _NRIC_TABLE if prefix in ("S", "T") else _FIN_TABLE
    return table[remainder]


def is_valid_nric_fin(value: str) -> bool:
    """Return True iff `value` is a syntactically valid NRIC or FIN.

    Validation steps:
    1. Length is exactly 9 characters.
    2. First character is one of S, T, F, G, M (case insensitive).
    3. Characters 2 through 8 are decimal digits.
    4. Character 9 is alphabetic and matches the computed checksum.

    Whitespace is not stripped; the caller is responsible for trimming.
    """
    if not isinstance(value, str) or len(value) != 9:
        return False
    upper = value.upper()
    prefix = upper[0]
    digits = upper[1:8]
    checksum = upper[8]
    if prefix not in _PREFIX_OFFSET:
        return False
    if not digits.isdigit():
        return False
    if not checksum.isalpha():
        return False
    try:
        expected = expected_checksum(prefix, digits)
    except ValueError:
        return False
    return checksum == expected
