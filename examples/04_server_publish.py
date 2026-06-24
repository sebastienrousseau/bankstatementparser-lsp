#!/usr/bin/env python3
"""Example: the server's lint-and-publish path without an editor.

Usage:
    pip install bankstatementparser-lsp     # requires Python 3.10+
    python examples/04_server_publish.py

The :func:`bankstatementparser_lsp.server._publish` helper is what the
language server runs on every ``textDocument/didOpen`` and
``textDocument/didChange`` notification: it reads the document from the
workspace, lints it with :func:`diagnostics_for_mt940`, converts each
internal :class:`Diagnostic` to an ``lsprotocol`` diagnostic via
:func:`_to_lsp_diagnostic`, and calls ``publish_diagnostics``.

This example drives that exact path with a fake ``LanguageServer`` built
from :class:`types.SimpleNamespace`, so it needs no running editor and no
stdio transport — just the public diagnostic engine and the server glue.
"""

import types

from bankstatementparser_lsp.server import _publish


def make_fake_server(
    source: str,
) -> tuple[types.SimpleNamespace, list[tuple[str, list[object]]]]:
    """Build a fake ``LanguageServer`` recording published diagnostics.

    Args:
        source: The MT940 document text the workspace should return.

    Returns:
        A ``(server, published)`` pair, where ``published`` is the list
        the fake server appends ``(uri, diagnostics)`` tuples to.
    """
    published: list[tuple[str, list[object]]] = []

    def get_text_document(uri: str) -> types.SimpleNamespace:
        """Return a document whose ``source`` is the fixture text."""
        return types.SimpleNamespace(source=source)

    def publish_diagnostics(uri: str, diagnostics: list[object]) -> None:
        """Record the diagnostics published for ``uri``."""
        published.append((uri, diagnostics))

    server = types.SimpleNamespace(
        workspace=types.SimpleNamespace(get_text_document=get_text_document),
        publish_diagnostics=publish_diagnostics,
    )
    return server, published


# --- A clean document publishes an empty diagnostic list ------------------
CLEAN = (
    ":20:STARTUMS\n"
    ":25:1234567890\n"
    ":28C:00001/001\n"
    ":60F:C230101EUR1000,00\n"
    ":61:2301020102C500,00NTRFNONREF//abc\n"
    ":86:Salary payment\n"
    ":62F:C230102EUR1500,00"
)
server, published = make_fake_server(CLEAN)
_publish(server, "file:///clean.mt940")
uri, diagnostics = published[0]
print(f"clean: published {len(diagnostics)} diagnostic(s) to {uri}")

# --- A broken document publishes one LSP diagnostic per problem -----------
BROKEN = (
    ":20:ONLY\n"
    ":60F:NOTABALANCE\n"
    ":61:NOTVALID\n"
    ":86:Orphan note with no statement line"
)
server, published = make_fake_server(BROKEN)
_publish(server, "file:///broken.mt940")
uri, diagnostics = published[0]
print(f"broken: published {len(diagnostics)} diagnostic(s) to {uri}")
for lsp_diagnostic in diagnostics:
    start = lsp_diagnostic.range.start
    print(
        f"  line {start.line}:{start.character} "
        f"[{lsp_diagnostic.severity.name}] "
        f"{lsp_diagnostic.code}: {lsp_diagnostic.message}"
    )
