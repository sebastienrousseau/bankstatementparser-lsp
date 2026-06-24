#!/usr/bin/env python3
"""Example: grouping MT940 diagnostics by severity.

Usage:
    pip install bankstatementparser-lsp     # requires Python 3.10+
    python examples/02_severity_filtering.py

Each diagnostic produced by the engine carries a :class:`Severity`
(``ERROR``, ``WARNING``, ``INFORMATION`` or ``HINT``). Editors colour
squiggles by severity; this example reproduces that grouping locally.
"""

from collections import defaultdict

from bankstatementparser_lsp.diagnostics import (
    Severity,
    diagnostics_for_mt940,
)

# An :86: information line with no preceding :61: statement line is a
# warning, while missing mandatory tags are errors.
document = (
    ":20:STARTUMS\n"
    ":25:1234567890\n"
    ":28C:00001/001\n"
    ":60F:C230101EUR1000,00\n"
    ":86:Orphan note with no statement line\n"
    ":62F:C230102EUR1500,00"
)

by_severity: dict[Severity, list[str]] = defaultdict(list)
for diagnostic in diagnostics_for_mt940(document):
    by_severity[diagnostic.severity].append(diagnostic.code)

for severity in Severity:
    codes = by_severity.get(severity, [])
    print(f"{severity.name:12} {len(codes)} issue(s): {codes}")
