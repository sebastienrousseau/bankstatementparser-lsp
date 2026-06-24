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
