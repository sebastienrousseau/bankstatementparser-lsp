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

"""Coverage-guided Atheris fuzz target for the MT940 diagnostics engine.

Every keystroke in an editor sends the whole document through
``diagnostics_for_mt940`` and then ``_to_lsp_diagnostic``, which is what
the server publishes. Neither may raise on any text: an exception there
kills the diagnostics for the open file. Each diagnostic must also point
inside the document it came from (a line the engine split out, a column
range within that line), or the editor underlines nothing or the wrong
text. Any exception, or an out-of-range diagnostic, escapes the target
and libFuzzer records it as a crash.

Run (Linux x86_64, Python 3.12+, ``poetry install --with fuzz``)::

    python fuzz/fuzz_diagnostics.py fuzz/corpus -max_total_time=60
"""

from __future__ import annotations

import sys

import atheris

with atheris.instrument_imports():
    from bankstatementparser_lsp.diagnostics import diagnostics_for_mt940
    from bankstatementparser_lsp.server import _to_lsp_diagnostic


def _check_range(text: str, line: int, start: int, end: int) -> None:
    """Fail unless ``line``/``start``/``end`` lie inside ``text``."""
    lines = text.removeprefix("﻿").splitlines() or [""]
    if not 0 <= line < len(lines):
        raise AssertionError(f"line {line} outside {len(lines)} lines")
    if not 0 <= start <= end <= len(lines[line]):
        raise AssertionError(
            f"columns {start}..{end} outside line {line} "
            f"of length {len(lines[line])}"
        )


def test_one_input(data: bytes) -> None:
    """Lint one fuzz input and convert every diagnostic for the client."""
    text = atheris.FuzzedDataProvider(data).ConsumeUnicodeNoSurrogates(
        len(data)
    )
    for diagnostic in diagnostics_for_mt940(text):
        _check_range(
            text, diagnostic.line, diagnostic.col_start, diagnostic.col_end
        )
        _to_lsp_diagnostic(diagnostic)


def main() -> None:
    """Hand the target to libFuzzer with the command-line options."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
