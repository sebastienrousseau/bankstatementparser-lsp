#!/usr/bin/env python3
"""Example: converting engine diagnostics to LSP diagnostics.

Usage:
    pip install bankstatementparser-lsp     # requires Python 3.10+
    python examples/03_lsp_conversion.py

The server maps each internal :class:`Diagnostic` onto an
``lsprotocol`` diagnostic before publishing it to the editor. This
example shows that conversion for a malformed balance line, exactly as
``bankstatementparser-lsp`` would emit it over stdio.
"""

from bankstatementparser_lsp.diagnostics import diagnostics_for_mt940
from bankstatementparser_lsp.server import _to_lsp_diagnostic

document = (
    ":20:X\n:25:X\n:28C:1/1\n"
    ":60F:NOTABALANCE\n"
    ":61:2301020102C500,00NTRF\n"
    ":62F:C230102EUR1500,00"
)

for diagnostic in diagnostics_for_mt940(document):
    lsp_diagnostic = _to_lsp_diagnostic(diagnostic)
    start = lsp_diagnostic.range.start
    print(
        f"line {start.line}:{start.character} "
        f"[{lsp_diagnostic.severity.name}] "
        f"{lsp_diagnostic.code}: {lsp_diagnostic.message}"
    )
