# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2026-08-18

### Changed

- Cross-validation fixtures now use repeated digits (`S1111111D` and
  friends) instead of random-looking ones. The previous set was generated
  rather than harvested, but a checksum-valid identifier is checksum-valid
  whoever holds it, and nothing in the number records where it came from,
  so a reader could not tell them apart from identifiers issued to real
  people. All fifteen were re-confirmed against samliew's validator, in a
  run that included two controls with known answers.
- The contributing rule now asks for a visibly fabricated shape, a repeated
  digit, a run, or zero-padded, rather than for values that "are not real".
  A short section explains why the shape matters more than the origin, and
  records that this project did not always meet its own rule.
- Attribution updated for Presidio's move out of Microsoft: the project
  now lives at `data-privacy-stack/presidio` and its LICENSE names the
  Presidio Contributors as copyright holder. `ATTRIBUTIONS.md`, `NOTICE`,
  the README, the package description, and the module docstring no
  longer credit Microsoft Corporation; an origin note records the
  history.
- Checksum provenance comments now name samliew's NRIC validator
  explicitly and point to the pinned `SAMLIEW_VALIDATED_SAMPLES`
  fixtures.

## [0.1.1] - 2026-05-23

Internal release. No package behaviour changes.

### Changed

- Publish workflow bumped to Node 24-compatible action majors:
  `actions/setup-python` v5 -> v6, `actions/upload-artifact` v4 -> v7,
  `actions/download-artifact` v4 -> v8. GitHub Actions runners
  default to Node 24 from 2026-06-02, after which the older
  versions emit deprecation warnings.

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

[Unreleased]: https://github.com/pdpa-tools/presidio-sg-recognizers/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/pdpa-tools/presidio-sg-recognizers/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/pdpa-tools/presidio-sg-recognizers/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/pdpa-tools/presidio-sg-recognizers/releases/tag/v0.1.0
