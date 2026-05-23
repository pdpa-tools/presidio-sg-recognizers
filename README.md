# presidio-sg-recognizers

[![CI](https://github.com/pdpa-tools/presidio-sg-recognizers/actions/workflows/ci.yml/badge.svg)](https://github.com/pdpa-tools/presidio-sg-recognizers/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/presidio-sg-recognizers.svg)](https://pypi.org/project/presidio-sg-recognizers/)
[![Python versions](https://img.shields.io/pypi/pyversions/presidio-sg-recognizers.svg)](https://pypi.org/project/presidio-sg-recognizers/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Singapore-specific custom recognizers for [Microsoft Presidio](https://github.com/microsoft/presidio). Detects identifiers that Presidio's defaults miss or overshoot in a Singapore context: NRIC and FIN with full checksum validation, Singapore mobile and landline phone numbers, six-digit postal codes, and configurable internal codes (cost-centre, project, clinical-service, course code, etc.).

The Personal Data Protection Act 2012 (PDPA) is Singapore's data protection law. PDPA-grade detection requires correct, locally-aware recognizers; this package fills the gap that Presidio's out-of-the-box English recognizers leave open for Singapore data.

## What's in the box

| Entity type      | What it matches                                  | Validation     |
|------------------|--------------------------------------------------|----------------|
| `SG_NRIC`        | NRIC (National Registration Identity Card), S/T prefix | Checksum   |
| `SG_FIN`         | FIN (Foreign Identification Number), F/G/M prefix      | Checksum   |
| `SG_PHONE`       | Singapore phone: +65 / 0065 prefix optional, 3/6/8/9 leading digit | Format only |
| `SG_POSTAL`      | 6-digit postal code with address-context scoring       | Context-boosted |
| `INTERNAL_CODE`  | Configurable letter+digit code (default: 3 letters + 4 digits) | Format only |

NRIC and FIN go through full checksum verification, so format-only false positives (random `S1234567X`-shaped strings that happen to appear in the text) are filtered out. Phone, postal code, and internal code rely on regex format plus Presidio's context boosting; the consuming pipeline is expected to set an appropriate score threshold.

## Install

```bash
pip install presidio-sg-recognizers
```

Or with uv:

```bash
uv add presidio-sg-recognizers
```

Requires Python 3.11 or newer, and `presidio-analyzer>=2.2,<3` (installed automatically as a dependency).

## Use

The fastest path is `all_recognizers()`, which returns one of each recognizer in a list. Register them against a Presidio `AnalyzerEngine`:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_sg_recognizers import all_recognizers

analyzer = AnalyzerEngine()
for recognizer in all_recognizers():
    analyzer.registry.add_recognizer(recognizer)

results = analyzer.analyze(
    text="Please verify S0000001I before processing.",
    entities=["SG_NRIC", "SG_FIN", "SG_PHONE", "SG_POSTAL", "INTERNAL_CODE"],
    language="en",
)
for r in results:
    print(r.entity_type, r.start, r.end, r.score)
```

If you only want a subset, import the per-module factories directly:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_sg_recognizers import sg_nric, sg_fin

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(sg_nric.build_recognizer())
analyzer.registry.add_recognizer(sg_fin.build_recognizer())
```

The internal-code recognizer accepts custom letter and digit counts for organisations whose codes don't fit the 3-letter + 4-digit default:

```python
from presidio_sg_recognizers import internal_code

# e.g. department codes shaped as DEPT12 (4 letters + 2 digits)
recognizer = internal_code.build_recognizer(prefix_letters=4, digit_count=2)
```

## Design notes

### Lazy Presidio import

Each recognizer module's `presidio_analyzer` import is gated behind `TYPE_CHECKING` at module load time and only imported inside `build_recognizer()`. That means you can `import presidio_sg_recognizers` in a lightweight environment (e.g. CI without presidio installed) and only pay the import cost when you actually build a recognizer. The format regexes (`NRIC_FORMAT_RE`, `FIN_FORMAT_RE`, etc.) are usable without Presidio at all.

### Checksum module is pure-Python, dependency-free

`_checksum.py` has zero third-party dependencies and is import-safe in any environment. It implements the weighted-sum + prefix-offset + lookup-table algorithm shared by NRIC and FIN. The Presidio `PatternRecognizer` wrappers in `sg_nric.py` and `sg_fin.py` call into it from `validate_result()` to drop format-correct but checksum-invalid candidates.

### F, G, and M share a single FIN lookup table

Earlier community write-ups sometimes claim three distinct M-series tables; cross-checking against fifteen samples confirmed valid by an independent online tool (see test_checksum.py) disproves that. F, G, and M differ only in the prefix offset added before the modulo step; the trailing-letter lookup table is the same.

### Context-aware postal codes

A bare 6-digit number is too ambiguous to flag on its own (phone last-six, reference numbers, year-month concatenations, the like). The postal recognizer ships with a low base score (0.3) and a context list of street suffixes, "Singapore", "Blk", and similar. Presidio's analyzer engine boosts the score when those context words appear within the proximity window, so address-shaped surroundings raise the postal candidate into the detection range while isolated 6-digit runs stay below it.

## Testing

```bash
uv sync --group dev
uv run pytest -ra
uv run ruff check .
uv run ruff format --check .
```

The test suite has three parts:

1. **Checksum tests** (`tests/test_checksum.py`): hand-verified fixed fixtures, samliew-cross-validated samples, and a Hypothesis property-based pass that exercises the full (prefix, digits) input space.
2. **Format-regex tests** (`tests/test_format_regex.py`): bare-regex behaviour for every recognizer, runnable without `presidio-analyzer` installed.
3. **Presidio integration tests** (`tests/test_recognizers_integration.py`): construct real `PatternRecognizer` instances and call `analyze()` directly. Skipped cleanly when `presidio-analyzer` isn't installed.

## Versioning

Follows [Semantic Versioning](https://semver.org/). Public API for v0.x is:

- Module names: `sg_nric`, `sg_fin`, `sg_phone`, `sg_postal`, `internal_code`.
- Entity type strings: `SG_NRIC`, `SG_FIN`, `SG_PHONE`, `SG_POSTAL`, `INTERNAL_CODE`.
- Per-module `build_recognizer()` factories and `*_FORMAT_RE` re-exports.
- The top-level `all_recognizers()` convenience.

Breaking changes to any of the above will bump the major version once the package reaches 1.0.

## License

Apache License 2.0. See [LICENSE](LICENSE).

The patent grant in Apache 2.0 is the reason this package ships under Apache rather than MIT (the underlying `pdpa-scrub` project that motivated it uses MIT). Library-style packages benefit from explicit patent terms.

## Attribution

See [ATTRIBUTIONS.md](ATTRIBUTIONS.md) for dependency credits and the provenance stance on the NRIC/FIN checksum algorithm.

## Contributing

Issues and pull requests are welcome. Before opening a PR:

- Tests pass (`uv run pytest -ra`).
- Code is formatted (`uv run ruff format .`) and lint-clean (`uv run ruff check .`).
- No real Singapore identifiers, names, or organisations in fixtures or examples. The test suite uses obvious synthetic placeholders (`S0000001I`, `S1234567D`, "Jane Doe") that pass format checks but are not real. PRs that introduce real-looking values will be asked to swap them out.

For larger changes (new recognizer types, breaking API changes, new ways to configure existing recognizers), open an issue first to talk through the design.

## Context

This package was extracted from [pdpa-scrub](https://github.com/pdpa-tools/pdpa-scrub), a two-stage anonymiser for PDPA and intellectual property material. The Singapore recognizers are useful on their own (anywhere a Presidio pipeline runs against Singapore-context text), so they live here as a separate Apache 2.0 library.
