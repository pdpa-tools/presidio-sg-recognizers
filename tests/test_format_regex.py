"""Tests for the format-only regex on each SG recogniser module.

These exercise the bare regex patterns (NRIC, FIN, phone, postal,
internal code) without going through Presidio's analyzer engine. That
lets the tests run with only the dev-dep stack installed, no
presidio-analyzer required.

The Presidio integration layer (the `build_recognizer()` factories)
is tested separately in `test_recognizers_integration.py` and skipped
when presidio is not installed.
"""

from __future__ import annotations

import pytest

from presidio_sg_recognizers.internal_code import INTERNAL_CODE_FORMAT_RE
from presidio_sg_recognizers.sg_fin import FIN_FORMAT_RE
from presidio_sg_recognizers.sg_nric import NRIC_FORMAT_RE
from presidio_sg_recognizers.sg_phone import PHONE_FORMAT_RE
from presidio_sg_recognizers.sg_postal import POSTAL_FORMAT_RE


class TestNricFormatRegex:
    @pytest.mark.parametrize(
        "text",
        [
            "S1234567D",
            "T1234567J",
            "s1234567d",  # lowercase prefix accepted
            "Please verify S1234567D before submission.",
        ],
    )
    def test_matches_well_formed(self, text):
        assert NRIC_FORMAT_RE.search(text) is not None

    @pytest.mark.parametrize(
        "text",
        [
            "F1234567N",  # FIN, not NRIC
            "M1234567X",  # FIN, not NRIC
            "S12345678D",  # 8 digits not 7
            "S123456D",  # 6 digits not 7
            "SX234567D",  # non-digit in body
            "S1234567",  # missing checksum
            "ABC1234567D",  # not the leading SG-NRIC shape
        ],
    )
    def test_does_not_match_other_shapes(self, text):
        assert NRIC_FORMAT_RE.search(text) is None


class TestFinFormatRegex:
    @pytest.mark.parametrize(
        "text",
        [
            "F1234567N",
            "G1234567X",
            "M1234567X",
            "g0000001A",  # case insensitive
            "Work permit FIN: G9876543K",
        ],
    )
    def test_matches_well_formed(self, text):
        assert FIN_FORMAT_RE.search(text) is not None

    @pytest.mark.parametrize(
        "text",
        [
            "S1234567D",  # NRIC, not FIN
            "T1234567J",  # NRIC, not FIN
            "X1234567A",  # unknown prefix
            "F12345678N",  # 8 digits
            "ABCFG1234567",  # not the leading SG-FIN shape
        ],
    )
    def test_does_not_match_other_shapes(self, text):
        assert FIN_FORMAT_RE.search(text) is None


class TestPhoneFormatRegex:
    @pytest.mark.parametrize(
        "text",
        [
            "91234567",  # bare mobile (9-prefix)
            "81234567",  # bare mobile (8-prefix)
            "61234567",  # bare landline (6-prefix)
            "31234567",  # bare VOIP (3-prefix)
            "9123 4567",  # conventional grouping
            "9123-4567",  # hyphen separator
            "+6591234567",  # with country code
            "+65 9123 4567",  # country code + space + grouping
            "(+65) 9123-4567",  # parens + country code + hyphen
            "006591234567",  # 0065 country code
        ],
    )
    def test_matches_well_formed(self, text):
        assert PHONE_FORMAT_RE.search(text) is not None

    @pytest.mark.parametrize(
        "text",
        [
            "12345678",  # leading 1, not in SG prefix set
            "21234567",  # leading 2, not in SG prefix set
            "71234567",  # leading 7, not in SG prefix set
            "9123",  # too short
        ],
    )
    def test_does_not_match_other_shapes(self, text):
        assert PHONE_FORMAT_RE.search(text) is None


class TestPostalFormatRegex:
    @pytest.mark.parametrize(
        "text",
        [
            "123456",
            "Singapore 238859",
            "Blk 123 Tampines St 11, Singapore 521123",
        ],
    )
    def test_matches_six_digit_runs(self, text):
        assert POSTAL_FORMAT_RE.search(text) is not None

    @pytest.mark.parametrize(
        "text",
        [
            "12345",  # 5 digits
            "1234567",  # 7 digits (the regex requires word boundary on both
            # sides, so a 7-digit run does NOT contain a 6-digit
            # match: there is no \b in the middle of digits)
        ],
    )
    def test_does_not_match_wrong_length(self, text):
        assert POSTAL_FORMAT_RE.search(text) is None


class TestInternalCodeFormatRegex:
    @pytest.mark.parametrize(
        "text",
        [
            # Enterprise contexts
            "FIN2026",  # cost-centre code
            "PRJ4015",  # project code
            "Charge time to cost-centre OPS3022 this quarter.",
            # SMB contexts
            "CLI2099",  # client-engagement code
            "Sprint SPR2026 starts on Monday.",
            # Healthcare contexts
            "MED1234",  # clinical-service code
            "Refer patient under formulary code DRG2007.",
            # Educational contexts
            "INF2007",  # course/module code
            "LAW3015",
        ],
    )
    def test_matches_well_formed(self, text):
        assert INTERNAL_CODE_FORMAT_RE.search(text) is not None

    @pytest.mark.parametrize(
        "text",
        [
            "INF20",  # too few digits
            "INF200000",  # too many digits
            "IN2007",  # too few letters
            "INFO2007",  # too many letters
            "inf2007",  # lowercase letters
        ],
    )
    def test_does_not_match_other_shapes(self, text):
        assert INTERNAL_CODE_FORMAT_RE.search(text) is None
