# Copyright (C) 2023-2026 Bank Statement Parser. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0

"""Regression suite: every code example in the docs must actually run.

``test_docs_accuracy.py`` checks that *claims* in the docs match the
codebase; this module goes further and *executes* the documented
examples themselves.

Every fenced ``python`` block in README.md and ``docs/*.md`` must be
classified in :data:`BLOCK_SPECS` below. Adding a new python block to
the docs without classifying it fails the suite, so examples cannot
silently rot. Each classified block is compiled and executed in-process
against the real public API.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_FILES = ("README.md",) + tuple(
    f"docs/{p.name}" for p in sorted((REPO_ROOT / "docs").glob("*.md"))
)


# ----------------------------------------------------------------------
# Block extraction
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class DocBlock:
    """One fenced code block lifted from a markdown file."""

    doc: str
    line: int
    lang: str
    body: str

    @property
    def location(self) -> str:
        """A ``path:line`` label identifying the block."""
        return f"{self.doc}:{self.line}"


def _extract_blocks() -> list[DocBlock]:
    """Return every fenced code block across the scanned doc files."""
    blocks: list[DocBlock] = []
    for rel in DOC_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(
            r"^```(\w*)\n(.*?)^```", text, re.DOTALL | re.MULTILINE
        ):
            blocks.append(
                DocBlock(
                    doc=rel,
                    line=text[: match.start()].count("\n") + 1,
                    lang=match.group(1),
                    body=match.group(2),
                )
            )
    return blocks


ALL_BLOCKS = _extract_blocks()
PYTHON_BLOCKS = [b for b in ALL_BLOCKS if b.lang == "python"]


# ----------------------------------------------------------------------
# Classification registry
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class BlockSpec:
    """How to exercise one documented python block.

    Attributes:
        marker: A substring unique to exactly one python block across all
            scanned docs.
        preamble: Optional code executed before the block body.
    """

    marker: str
    preamble: str = ""


BLOCK_SPECS: tuple[BlockSpec, ...] = (
    # README — "Using the helpers": clean vs. missing-tag documents.
    BlockSpec(
        marker="from bankstatementparser_lsp.diagnostics "
        "import diagnostics_for_mt940",
    ),
)


def _matching_blocks(spec: BlockSpec) -> list[DocBlock]:
    """Return the python blocks whose body contains ``spec.marker``."""
    return [b for b in PYTHON_BLOCKS if spec.marker in b.body]


# ----------------------------------------------------------------------
# Structural guarantees
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "block", PYTHON_BLOCKS, ids=[b.location for b in PYTHON_BLOCKS]
)
def test_python_block_is_valid_syntax(block: DocBlock) -> None:
    """Every documented python block parses as valid Python."""
    ast.parse(block.body, filename=block.location)


def test_every_python_block_is_classified() -> None:
    """Each documented python block maps to exactly one BlockSpec."""
    unmatched = [
        b.location
        for b in PYTHON_BLOCKS
        if not any(spec.marker in b.body for spec in BLOCK_SPECS)
    ]
    assert not unmatched, (
        "Unclassified python blocks in docs (add a BlockSpec so the "
        f"example is executed by the regression suite): {unmatched}"
    )

    for spec in BLOCK_SPECS:
        matches = _matching_blocks(spec)
        assert len(matches) == 1, (
            f"BlockSpec marker {spec.marker!r} must match exactly one "
            f"block, matched {[b.location for b in matches]}"
        )


# ----------------------------------------------------------------------
# Execution
# ----------------------------------------------------------------------


def _spec_id(spec: BlockSpec) -> str:
    """Return a stable parametrize id for a BlockSpec."""
    blocks = _matching_blocks(spec)
    return blocks[0].location if blocks else spec.marker[:30]


@pytest.mark.parametrize(
    "spec", BLOCK_SPECS, ids=[_spec_id(s) for s in BLOCK_SPECS]
)
def test_documented_python_block(
    spec: BlockSpec,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Execute one classified python block against the public API."""
    blocks = _matching_blocks(spec)
    assert len(blocks) == 1
    block = blocks[0]

    namespace: dict[str, object] = {"__name__": "bsp_lsp_doc_example"}
    if spec.preamble:
        exec(
            compile(spec.preamble, f"{block.location}-preamble", "exec"),
            namespace,
        )
    exec(compile(block.body, block.location, "exec"), namespace)
    capsys.readouterr()  # examples are allowed to print
