# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-23

Initial release. Extracted from the [pdpa-scrub](https://github.com/pdpa-tools/pdpa-scrub) project.

### Added

- `SG_NRIC` recognizer with full checksum validation (S and T series).
- `SG_FIN` recognizer with full checksum validation (F, G, and M series).
- `SG_PHONE` recognizer for Singapore phone numbers (3/6/8/9 prefix, optional +65 / 0065 country code).
- `SG_POSTAL` recognizer for 6-digit Singapore postal codes with address-context boosting.
- `INTERNAL_CODE` recognizer for configurable letter+digit code patterns (default: 3 letters + 4 digits).
- Top-level `all_recognizers()` convenience that returns the full bundle.
- Per-recognizer `*_FORMAT_RE` re-exports for callers that want the bare regex without Presidio.
- Test suite: 145+ tests including hand-verified fixtures, Hypothesis property-based round trips, samliew-cross-validated samples, format-regex behaviour, and Presidio integration.

[Unreleased]: https://github.com/pdpa-tools/presidio-sg-recognizers/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pdpa-tools/presidio-sg-recognizers/releases/tag/v0.1.0
