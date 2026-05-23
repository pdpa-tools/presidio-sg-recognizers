"""Integration tests that build real Presidio PatternRecognizer objects.

These tests require `presidio-analyzer` to be installed. When it isn't,
the whole module is skipped cleanly so the rest of the test suite can
still run in lightweight environments.

Design note: these tests deliberately bypass `AnalyzerEngine` and call
`recognizer.analyze()` directly with `nlp_artifacts=None`. The
recognisers we ship are regex + checksum based; they do not need an
NLP engine to produce results. AnalyzerEngine's role is orchestration
across many recognisers plus context-score boosting, which is Presidio's
concern, not ours. Avoiding AnalyzerEngine here means the tests do not
need spaCy (or any other NLP backend) installed in CI.
"""

from __future__ import annotations

import pytest

presidio_analyzer = pytest.importorskip("presidio_analyzer")

from presidio_sg_recognizers import (  # noqa: E402
    all_recognizers,
    internal_code,
    sg_fin,
    sg_nric,
    sg_phone,
    sg_postal,
)


def _entity_types(results) -> list[str]:
    return sorted(r.entity_type for r in results)


def test_nric_detection_through_presidio():
    """A valid NRIC is detected with the SG_NRIC entity type."""
    recognizer = sg_nric.build_recognizer()
    results = recognizer.analyze(
        text="Please verify S1234567D before submission.",
        entities=["SG_NRIC"],
        nlp_artifacts=None,
    )
    assert "SG_NRIC" in _entity_types(results)


def test_invalid_nric_checksum_dropped_by_validate_result():
    """A format-correct but checksum-invalid NRIC is dropped by validate_result.

    The format regex would match S1234567Z; the checksum check rejects it
    because the correct checksum letter for S1234567 is D.
    """
    recognizer = sg_nric.build_recognizer()
    results = recognizer.analyze(
        text="Bogus ID S1234567Z appears in the document.",
        entities=["SG_NRIC"],
        nlp_artifacts=None,
    )
    assert _entity_types(results) == []


def test_fin_m_series_detection_through_presidio():
    """An M-series FIN with valid checksum is detected with SG_FIN.

    Note: M1234567 with X would NOT match (samliew-confirmed; the
    correct trailing checksum for M1234567 is K). The previous version
    of this test used M1234567X and slipped through unnoticed because
    the older _checksum.py erroneously accepted it. The corrected
    fixture below uses the actually-valid form, which is also a
    regression guard against the same bug reappearing.
    """
    recognizer = sg_fin.build_recognizer()
    results = recognizer.analyze(
        text="Work pass M1234567K expires next year.",
        entities=["SG_FIN"],
        nlp_artifacts=None,
    )
    assert "SG_FIN" in _entity_types(results)


def test_phone_detection_through_presidio():
    """A +65-prefixed SG mobile is detected with SG_PHONE."""
    recognizer = sg_phone.build_recognizer()
    results = recognizer.analyze(
        text="Call me at +65 9123 4567 when you arrive.",
        entities=["SG_PHONE"],
        nlp_artifacts=None,
    )
    assert "SG_PHONE" in _entity_types(results)


def test_postal_format_matches_with_address_context():
    """The postal recognizer's regex matches a 6-digit run in address text.

    Note: contextual score-boosting (penalising bare 6-digit numbers
    without address context) happens at the AnalyzerEngine layer in
    Presidio, not at the recognizer layer. We don't test that here
    because it is Presidio behaviour, not behaviour we own.
    """
    recognizer = sg_postal.build_recognizer()
    results = recognizer.analyze(
        text="Office at Blk 123 Tampines Street 11, Singapore 521123.",
        entities=["SG_POSTAL"],
        nlp_artifacts=None,
    )
    assert "SG_POSTAL" in _entity_types(results)


def test_internal_code_detection_through_presidio():
    """Two distinct internal codes in a sentence both surface as INTERNAL_CODE.

    The example below uses a corporate cost-centre code and a project
    code; the recogniser is intentionally context-agnostic and treats
    any three-letter-four-digit code identically across enterprise, SMB,
    healthcare, and educational contexts.
    """
    recognizer = internal_code.build_recognizer()
    results = recognizer.analyze(
        text="All FIN2026 spend must be allocated against project PRJ4015.",
        entities=["INTERNAL_CODE"],
        nlp_artifacts=None,
    )
    assert _entity_types(results).count("INTERNAL_CODE") == 2


def test_all_recognizers_bundle_size_and_entity_types():
    """`all_recognizers()` returns one of each supported recognizer.

    Guards against accidental drops or duplicates if the bundle changes.
    """
    bundle = all_recognizers()
    assert len(bundle) == 5
    entity_types = sorted(r.supported_entities[0] for r in bundle)
    assert entity_types == [
        "INTERNAL_CODE",
        "SG_FIN",
        "SG_NRIC",
        "SG_PHONE",
        "SG_POSTAL",
    ]
