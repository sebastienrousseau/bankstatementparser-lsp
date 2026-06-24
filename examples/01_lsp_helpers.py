#!/usr/bin/env python3
"""Example: the LSP server's MT940 diagnostic engine.

Usage:
    pip install bankstatementparser-lsp     # requires Python 3.10+
    python examples/01_lsp_helpers.py

The bankstatementparser language server (launched as ``bankstatementparser-lsp``
over stdio) powers editor diagnostics for MT940 bank-statement files. Its
logic lives in the pure, dependency-free :func:`diagnostics_for_mt940`
helper that you can call directly — exactly what the server runs on each
edit.
"""

from bankstatementparser_lsp.diagnostics import diagnostics_for_mt940

# --- A clean MT940 statement ----------------------------------------------
valid_doc = (
    ":20:STARTUMS\n"
    ":25:1234567890\n"
    ":28C:00001/001\n"
    ":60F:C230101EUR1000,00\n"
    ":61:2301020102C500,00NTRFNONREF//abc\n"
    ":86:Salary payment\n"
    ":62F:C230102EUR1500,00"
)
print("clean document diagnostics:", diagnostics_for_mt940(valid_doc))

# --- Missing mandatory tags -----------------------------------------------
missing = ":20:ONLY\n:61:2301020102C5,00NTRF"
print(
    "missing-tag diagnostics:",
    len(diagnostics_for_mt940(missing)),
    "issue(s)",
)

# --- Malformed balance and statement lines --------------------------------
bad_lines = (
    ":20:X\n:25:X\n:28C:1/1\n"
    ":60F:NOTABALANCE\n"
    ":61:NOTVALID\n"
    ":62F:C230102EUR1500,00"
)
for diagnostic in diagnostics_for_mt940(bad_lines):
    print(
        f"  line {diagnostic.line}: {diagnostic.code} — {diagnostic.message}"
    )
