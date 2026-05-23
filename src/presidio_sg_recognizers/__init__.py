"""Singapore-specific custom recognizers for Microsoft Presidio.

Each recognizer subclasses Presidio's `PatternRecognizer` (or
`EntityRecognizer` for non-pattern cases) and implements
`validate_result()` where a checksum applies. No code is copied from
any upstream PII project; see `ATTRIBUTIONS.md` at the project root for
the project's attribution stance.

Modules:
    sg_nric         NRIC pattern + checksum (S- and T-prefix)
    sg_fin          FIN pattern + checksum (F-, G-, and M-prefix)
    sg_phone        +65 mobile and landline, with country-code variants
    sg_postal       6-digit Singapore postal codes with context check
    internal_code   Short internal alphanumeric codes (cost-centre code,
                    department code, project code, clinical-service code,
                    course code, etc.) with configurable per-organisation
                    pattern (default: three uppercase letters + four
                    digits)

Convenience top-level imports for the common case where a caller just
wants to register everything:

    from presidio_sg_recognizers import all_recognizers
    from presidio_analyzer import AnalyzerEngine

    analyzer = AnalyzerEngine()
    for recognizer in all_recognizers():
        analyzer.registry.add_recognizer(recognizer)
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from . import internal_code, sg_fin, sg_nric, sg_phone, sg_postal

try:
    __version__ = version("presidio-sg-recognizers")
except PackageNotFoundError:
    # Editable install without dist-info present, or running from a
    # source checkout. Match the source-of-truth value in pyproject.toml.
    __version__ = "0.0.0+local"


def all_recognizers() -> list:
    """Build and return a list of every recognizer in this package.

    Each call constructs fresh recognizer instances. Convenient for the
    common case where a caller wants to register the full Singapore
    bundle against a Presidio AnalyzerEngine in one shot. Callers that
    want only a subset can import and call the per-module
    `build_recognizer()` factories directly.

    Lazy-imports presidio_analyzer (via the per-module factories), so
    this function only works in environments that have it installed.
    """
    return [
        sg_nric.build_recognizer(),
        sg_fin.build_recognizer(),
        sg_phone.build_recognizer(),
        sg_postal.build_recognizer(),
        internal_code.build_recognizer(),
    ]


__all__ = [
    "__version__",
    "all_recognizers",
    "internal_code",
    "sg_fin",
    "sg_nric",
    "sg_phone",
    "sg_postal",
]
