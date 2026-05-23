# Attributions

This package depends on third-party software. Each dependency below is
credited with its copyright owner, license, and source URL.

## Runtime dependencies

### Microsoft Presidio (presidio-analyzer)

Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
Source: https://github.com/microsoft/presidio
PyPI: https://pypi.org/project/presidio-analyzer/

This package builds on Presidio's `PatternRecognizer` and
`EntityRecognizer` base classes. No Presidio source is vendored; the
dependency is installed at runtime via pip.

## Development dependencies

### pytest

Copyright (c) 2004 Holger Krekel and others.
Licensed under the MIT License.
Source: https://github.com/pytest-dev/pytest

### Hypothesis

Copyright (c) the Hypothesis authors.
Licensed under the Mozilla Public License 2.0.
Source: https://github.com/HypothesisWorks/hypothesis

### Ruff

Copyright (c) Charlie Marsh and Astral Software contributors.
Licensed under the MIT License.
Source: https://github.com/astral-sh/ruff

## Singapore identifier algorithms

The NRIC and FIN checksum implementations in `_checksum.py` are
written from public algorithm specifications, not copied from any
prior open-source project.

The identifier *structure* (prefix from {S, T, F, G, M}, seven decimal
digits, trailing checksum letter) is publicly documented on the
National Registration Identity Card Wikipedia article. The checksum
*algorithm itself* is not officially published by the Immigration and
Checkpoints Authority (ICA). The implementation uses the
community-reverse-engineered weight vector, prefix offsets, and lookup
tables that agree across multiple independent implementations (Ngiam
2004, samliew's `singapore-nric` library, others). These mathematical
inputs are not subject to copyright; only specific code expressions of
them are.

For independent verification, the test suite cross-checks fifteen
synthetic samples against samliew's online NRIC validator
(https://samliew.com/singapore-nric-validator), confirming agreement
on every series prefix.

## Trademarks

"Presidio" is a project of Microsoft Corporation. "Singapore" and
"NRIC" / "FIN" are not trademarks; the algorithms and identifier
formats are public-domain administrative protocols.

This project is not affiliated with, sponsored by, or endorsed by
Microsoft Corporation, the Immigration and Checkpoints Authority of
Singapore, or the Personal Data Protection Commission of Singapore.
