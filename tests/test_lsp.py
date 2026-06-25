# Copyright (C) 2023-2026 Bank Statement Parser. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the MT940 diagnostic engine and the pygls server glue."""

import types

import pytest

from bankstatementparser_lsp.diagnostics import (
    Severity,
    diagnostics_for_mt940,
)

GOOD = (
    ":20:STARTUMS\n"
    ":25:1234567890\n"
    ":28C:00001/001\n"
    ":60F:C230101EUR1000,00\n"
    ":61:2301020102C500,00NTRFNONREF//abc\n"
    ":86:Salary payment\n"
    ":62F:C230102EUR1500,00"
)


def _codes(text):
    """Return the rule codes produced for a document."""
    return [d.code for d in diagnostics_for_mt940(text)]


def test_clean_document_has_no_diagnostics():
    """A well-formed MT940 document produces no diagnostics."""
    assert diagnostics_for_mt940(GOOD) == []


def test_empty_document_is_clean():
    """An empty document is treated as clean."""
    assert diagnostics_for_mt940("") == []


def test_whitespace_only_document_is_clean():
    """A whitespace-only document is treated as clean."""
    assert diagnostics_for_mt940("   \n\t\n  ") == []


def test_missing_mandatory_tags_count():
    """A near-empty document reports each missing mandatory tag."""
    text = ":20:ONLY\n:61:2301020102C5,00NTRF"
    codes = _codes(text)
    assert codes.count("missing-tag") == 4


def test_malformed_balance_line():
    """A balance line that breaks the pattern is flagged."""
    text = (
        ":20:X\n:25:X\n:28C:1/1\n"
        ":60F:NOTABALANCE\n"
        ":61:2301020102C5,00NTRF\n"
        ":62F:C230102EUR1500,00"
    )
    diags = diagnostics_for_mt940(text)
    balance = [d for d in diags if d.code == "malformed-balance"]
    assert len(balance) == 1
    assert balance[0].severity is Severity.ERROR
    assert balance[0].line == 3


def test_malformed_statement_line():
    """A statement line that breaks the pattern is flagged."""
    text = (
        ":20:X\n:25:X\n:28C:1/1\n"
        ":60F:C230101EUR1000,00\n"
        ":61:NOTVALID\n"
        ":62F:C230102EUR1500,00"
    )
    codes = _codes(text)
    assert codes.count("malformed-statement-line") == 1


def test_orphan_information_line_warning():
    """An :86: line with no preceding :61: is a warning."""
    text = (
        ":20:X\n:25:X\n:28C:1/1\n"
        ":60F:C230101EUR1000,00\n"
        ":86:Orphan note\n"
        ":62F:C230102EUR1500,00"
    )
    diags = diagnostics_for_mt940(text)
    orphans = [d for d in diags if d.code == "orphan-information-line"]
    assert len(orphans) == 1
    assert orphans[0].severity is Severity.WARNING


def test_information_line_after_statement_is_clean():
    """An :86: line following a valid :61: line is accepted."""
    assert "orphan-information-line" not in _codes(GOOD)


def test_blank_lines_are_skipped():
    """Blank lines between tags do not produce diagnostics."""
    text = GOOD.replace(":25:1234567890\n", ":25:1234567890\n\n   \n")
    assert diagnostics_for_mt940(text) == []


def test_non_tag_line_is_ignored():
    """A continuation line that is not a tag does not break linting."""
    text = GOOD.replace(
        ":86:Salary payment\n",
        ":86:Salary payment\nfree text continuation\n",
    )
    assert diagnostics_for_mt940(text) == []


def test_to_lsp_diagnostic_field_mapping():
    """The internal diagnostic maps onto an LSP diagnostic correctly."""
    pytest.importorskip("pygls")
    from lsprotocol import types as lsp

    from bankstatementparser_lsp.diagnostics import Diagnostic
    from bankstatementparser_lsp.server import _to_lsp_diagnostic

    internal = Diagnostic(
        line=3,
        col_start=0,
        col_end=11,
        severity=Severity.ERROR,
        message="boom",
        code="malformed-balance",
    )
    converted = _to_lsp_diagnostic(internal)
    assert converted.range.start.line == 3
    assert converted.range.start.character == 0
    assert converted.range.end.line == 3
    assert converted.range.end.character == 11
    assert converted.message == "boom"
    assert converted.severity == lsp.DiagnosticSeverity.Error
    assert converted.code == "malformed-balance"
    assert converted.source == "bankstatementparser"


def _fake_server(source):
    """Build a SimpleNamespace fake LanguageServer recording publishes."""
    published = []

    def get_text_document(uri):
        """Return a document whose ``source`` is the fixture text."""
        return types.SimpleNamespace(source=source)

    def publish_diagnostics(uri, diagnostics):
        """Record the diagnostics published for ``uri``."""
        published.append((uri, diagnostics))

    ls = types.SimpleNamespace(
        workspace=types.SimpleNamespace(get_text_document=get_text_document),
        publish_diagnostics=publish_diagnostics,
    )
    return ls, published


def test_publish_collects_and_sends_diagnostics():
    """``_publish`` lints the document and forwards LSP diagnostics."""
    pytest.importorskip("pygls")
    from bankstatementparser_lsp.server import _publish

    text = ":20:ONLY\n:61:NOTVALID"
    ls, published = _fake_server(text)
    _publish(ls, "file:///statement.mt940")
    assert len(published) == 1
    uri, diagnostics = published[0]
    assert uri == "file:///statement.mt940"
    codes = {d.code for d in diagnostics}
    assert "malformed-statement-line" in codes
    assert "missing-tag" in codes


def test_publish_clean_document_sends_empty_list():
    """``_publish`` sends an empty list for a clean document."""
    pytest.importorskip("pygls")
    from bankstatementparser_lsp.server import _publish

    ls, published = _fake_server(GOOD)
    _publish(ls, "file:///clean.mt940")
    assert published == [("file:///clean.mt940", [])]


def test_did_open_lints_and_publishes():
    """The ``didOpen`` feature binding lints the opened document."""
    pytest.importorskip("pygls")
    from bankstatementparser_lsp.server import did_open

    ls, published = _fake_server(":20:ONLY")
    params = types.SimpleNamespace(
        text_document=types.SimpleNamespace(uri="file:///opened.mt940")
    )
    did_open(ls, params)
    assert published[0][0] == "file:///opened.mt940"
    assert any(d.code == "missing-tag" for d in published[0][1])


def test_did_change_relints_and_publishes():
    """The ``didChange`` feature binding re-lints the changed document."""
    pytest.importorskip("pygls")
    from bankstatementparser_lsp.server import did_change

    ls, published = _fake_server(GOOD)
    params = types.SimpleNamespace(
        text_document=types.SimpleNamespace(uri="file:///changed.mt940")
    )
    did_change(ls, params)
    assert published == [("file:///changed.mt940", [])]


def test_main_starts_the_server_over_stdio(monkeypatch):
    """``main`` starts the language server over stdio."""
    pytest.importorskip("pygls")
    from bankstatementparser_lsp import server as server_module

    calls = []
    monkeypatch.setattr(
        server_module.server, "start_io", lambda: calls.append(True)
    )
    server_module.main()
    assert calls == [True]


# ---------------------------------------------------------------------------
# Golden-style diagnostics: assert exact (line, code, severity) tuples.
# ---------------------------------------------------------------------------


def _tuples(text):
    """Return ``(line, code, severity)`` tuples for a document, in order."""
    return [(d.line, d.code, d.severity) for d in diagnostics_for_mt940(text)]


def test_all_four_codes_in_one_document():
    """One document triggers every rule code with exact line/severity.

    Per-line diagnostics are emitted in source order, then the
    missing-tag diagnostics (here ``:25:`` and ``:28C:``) are appended,
    all anchored to line 0.
    """
    text = (
        ":20:REF\n"
        ":60F:NOTABALANCE\n"
        ":86:orphan note\n"
        ":61:NOTVALID\n"
        ":62F:C230102EUR1500,00"
    )
    assert _tuples(text) == [
        (1, "malformed-balance", Severity.ERROR),
        (2, "orphan-information-line", Severity.WARNING),
        (3, "malformed-statement-line", Severity.ERROR),
        (0, "missing-tag", Severity.ERROR),
        (0, "missing-tag", Severity.ERROR),
    ]


def test_multiple_statement_and_information_pairs_are_clean():
    """Several valid ``:61:`` / ``:86:`` pairs produce no diagnostics."""
    text = (
        ":20:REF\n"
        ":25:1234567890\n"
        ":28C:00001/001\n"
        ":60F:C230101EUR1000,00\n"
        ":61:2301020102C500,00NTRFNONREF//a\n"
        ":86:first info\n"
        ":61:2301030103D250,00NTRFNONREF//b\n"
        ":86:second info\n"
        ":62F:C230103EUR1250,00"
    )
    assert _tuples(text) == []


def test_multiple_malformed_statement_and_orphan_pairs():
    """Two bad ``:61:`` lines and the ``:86:`` lines that follow them.

    The first ``:86:`` is orphaned because no valid ``:61:`` has been
    seen yet; once a malformed ``:61:`` never flips ``seen_statement``,
    every following ``:86:`` stays orphaned too.
    """
    text = (
        ":20:REF\n"
        ":25:1234567890\n"
        ":28C:00001/001\n"
        ":60F:C230101EUR1000,00\n"
        ":61:BADONE\n"
        ":86:info one\n"
        ":61:BADTWO\n"
        ":86:info two\n"
        ":62F:C230102EUR1500,00"
    )
    assert _tuples(text) == [
        (4, "malformed-statement-line", Severity.ERROR),
        (5, "orphan-information-line", Severity.WARNING),
        (6, "malformed-statement-line", Severity.ERROR),
        (7, "orphan-information-line", Severity.WARNING),
    ]


def test_crlf_line_endings_are_clean():
    """A clean document with Windows CRLF endings lints identically."""
    text = (
        ":20:REF\r\n"
        ":25:1234567890\r\n"
        ":28C:00001/001\r\n"
        ":60F:C230101EUR1000,00\r\n"
        ":61:2301020102C500,00NTRFNONREF//a\r\n"
        ":86:Salary\r\n"
        ":62F:C230102EUR1500,00\r\n"
    )
    assert _tuples(text) == []


def test_crlf_line_endings_report_exact_lines():
    """CRLF endings do not shift the reported line numbers."""
    text = (
        ":20:REF\r\n"
        ":25:1234567890\r\n"
        ":28C:00001/001\r\n"
        ":60F:NOTABALANCE\r\n"
        ":61:2301020102C500,00NTRFNONREF//a\r\n"
        ":62F:C230102EUR1500,00\r\n"
    )
    assert _tuples(text) == [(3, "malformed-balance", Severity.ERROR)]


def test_leading_blank_lines_and_trailing_blank_lines_are_clean():
    """Leading and trailing blank lines do not produce diagnostics."""
    text = (
        "\n"
        "   \n"
        ":20:REF\n"
        ":25:1234567890\n"
        ":28C:00001/001\n"
        ":60F:C230101EUR1000,00\n"
        ":61:2301020102C500,00NTRFNONREF//a\n"
        ":86:Salary\n"
        ":62F:C230102EUR1500,00\n"
        "\n"
        "   \n"
    )
    assert _tuples(text) == []


def test_bom_at_start_with_trailing_blank_lines_is_clean():
    """A real byte-0 UTF-8 BOM plus trailing blank lines lints clean.

    The BOM is prefixed directly to the first tag (``﻿:20:``), exactly
    as a UTF-8-with-BOM export produces it; the engine strips the single
    leading BOM so ``:20:`` is still recognised.
    """
    text = (
        "﻿:20:REF\n"
        ":25:1234567890\n"
        ":28C:00001/001\n"
        ":60F:C230101EUR1000,00\n"
        ":61:2301020102C500,00NTRFNONREF//a\n"
        ":86:Salary\n"
        ":62F:C230102EUR1500,00\n"
        "\n"
        "   \n"
    )
    assert _tuples(text) == []


def test_bom_prefixed_first_tag_is_not_a_missing_tag():
    """A BOM glued to ``:20:`` must not be misread as a missing tag."""
    bare = (
        ":20:REF\n:25:1234567890\n:28C:00001/001\n"
        ":60F:C230101EUR1000,00\n"
        ":61:2301020102C500,00NTRFNONREF//a\n:86:Salary\n"
        ":62F:C230102EUR1500,00"
    )
    assert _tuples("﻿" + bare) == _tuples(bare) == []


def test_valid_multi_statement_document_has_zero_diagnostics():
    """Two back-to-back valid MT940 statements produce no diagnostics."""
    text = (
        ":20:REF1\n:25:1234567890\n:28C:00001/001\n"
        ":60F:C230101EUR1000,00\n"
        ":61:2301020102C500,00NTRFNONREF//a\n:86:info a\n"
        ":62F:C230102EUR1500,00\n"
        ":20:REF2\n:25:1234567890\n:28C:00002/001\n"
        ":60F:C230103EUR1500,00\n"
        ":61:2301040104D200,00NTRFNONREF//b\n:86:info b\n"
        ":62F:C230104EUR1300,00"
    )
    assert _tuples(text) == []
