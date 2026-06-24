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

"""Pure diagnostic engine for MT940 bank statement documents.

No LSP or editor dependencies, so it is unit-testable in isolation.
Given the raw text of an MT940 (``.mt940``/``.sta``) file it returns a
list of :class:`Diagnostic` objects locating missing mandatory tags and
malformed balance / statement lines, using the same tag patterns the
bankstatementparser MT940 parser relies on.
"""

import re
from dataclasses import dataclass
from enum import IntEnum

_BALANCE_RE = re.compile(r"^:(60F|62F):[CD]\d{6}[A-Z]{3}[0-9,]+$")
_STATEMENT_RE = re.compile(r"^:61:\d{6}(?:\d{4})?[CD][0-9,]+.*$")
_REQUIRED_TAGS: tuple[str, ...] = (":20:", ":25:", ":28C:", ":60F:", ":62F:")


class Severity(IntEnum):
    """Diagnostic severity, matching the LSP numeric scale."""

    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


@dataclass(frozen=True)
class Diagnostic:
    """A single editor diagnostic over a 0-based line/character range.

    Attributes:
        line: Zero-based line index of the affected text.
        col_start: Zero-based start character on the line.
        col_end: Zero-based end character (exclusive) on the line.
        severity: Diagnostic severity.
        message: Human-readable description of the problem.
        code: Stable machine-readable rule identifier.
    """

    line: int
    col_start: int
    col_end: int
    severity: Severity
    message: str
    code: str


def _tag_of(stripped: str) -> str | None:
    """Return the leading ``:tag:`` of a stripped line, if any.

    Args:
        stripped: A whitespace-stripped MT940 line.

    Returns:
        The tag token including its colons, or ``None`` when the line
        does not begin with a tag.
    """
    match = re.match(r"^:[0-9]{2}[A-Z]?:", stripped)
    return match.group(0) if match is not None else None


def diagnostics_for_mt940(text: str) -> list[Diagnostic]:
    """Lint an MT940 statement document and return diagnostics.

    Args:
        text: The full text of the MT940 document.

    Returns:
        A list of :class:`Diagnostic` objects (empty when the document
        is clean or has no content).
    """
    # A leading UTF-8 BOM (U+FEFF) is not whitespace, so without this it
    # would cling to the first tag (e.g. ``﻿:20:``) and be misread as
    # a missing :20:. Strip a single leading BOM before scanning.
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.splitlines()
    if not any(line.strip() for line in lines):
        return []

    diagnostics: list[Diagnostic] = []
    seen_tags: set[str] = set()
    seen_statement = False

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped:
            continue
        tag = _tag_of(stripped)
        if tag is not None:
            seen_tags.add(tag)

        if tag in (":60F:", ":62F:") and not _BALANCE_RE.match(stripped):
            diagnostics.append(
                Diagnostic(
                    line=index,
                    col_start=0,
                    col_end=len(raw_line),
                    severity=Severity.ERROR,
                    message=(
                        f"Malformed balance line {tag} — expected "
                        "C/D + YYMMDD + 3-letter currency + amount"
                    ),
                    code="malformed-balance",
                )
            )
        elif tag == ":61:":
            if _STATEMENT_RE.match(stripped):
                seen_statement = True
            else:
                diagnostics.append(
                    Diagnostic(
                        line=index,
                        col_start=0,
                        col_end=len(raw_line),
                        severity=Severity.ERROR,
                        message=(
                            "Malformed :61: statement line — expected "
                            "YYMMDD + C/D + amount"
                        ),
                        code="malformed-statement-line",
                    )
                )
        elif tag == ":86:" and not seen_statement:
            diagnostics.append(
                Diagnostic(
                    line=index,
                    col_start=0,
                    col_end=len(raw_line),
                    severity=Severity.WARNING,
                    message=(
                        ":86: information line has no preceding :61: "
                        "statement line; it will be ignored"
                    ),
                    code="orphan-information-line",
                )
            )

    for tag in _REQUIRED_TAGS:
        if tag not in seen_tags:
            diagnostics.append(
                Diagnostic(
                    line=0,
                    col_start=0,
                    col_end=len(lines[0]),
                    severity=Severity.ERROR,
                    message=f"Missing mandatory MT940 tag: {tag}",
                    code="missing-tag",
                )
            )
    return diagnostics
