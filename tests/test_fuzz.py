# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Hypothesis property and fuzz tests for bankstatementparser-lsp."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from bankstatementparser_lsp.diagnostics import _tag_of, diagnostics_for_mt940


@settings(max_examples=50, deadline=None)
@given(st.text(min_size=0, max_size=2000))
def test_fuzz_diagnostics_for_mt940_never_crashes(content: str) -> None:
    """diagnostics_for_mt940 returns list of diagnostics for any input without crash."""
    diagnostics = diagnostics_for_mt940(content)
    assert isinstance(diagnostics, list)
    for diag in diagnostics:
        assert hasattr(diag, "line")
        assert hasattr(diag, "col_start")
        assert hasattr(diag, "col_end")
        assert hasattr(diag, "severity")
        assert hasattr(diag, "message")
        assert hasattr(diag, "code")


@settings(max_examples=50, deadline=None)
@given(st.lists(st.text(max_size=200), max_size=50))
def test_fuzz_diagnostics_multiline_mt940(lines: list[str]) -> None:
    """diagnostics_for_mt940 handles arbitrary lists of lines."""
    content = "\n".join(lines)
    diagnostics = diagnostics_for_mt940(content)
    assert isinstance(diagnostics, list)


@settings(max_examples=50, deadline=None)
@given(st.text(min_size=0, max_size=100))
def test_fuzz_tag_of_helper(line: str) -> None:
    """_tag_of extracts tag or safely returns None."""
    tag = _tag_of(line)
    assert tag is None or isinstance(tag, str)
