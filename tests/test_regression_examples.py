# Copyright (C) 2023-2026 Bank Statement Parser. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0

"""Regression suite: execute every shipped example script end-to-end.

Each ``examples/*.py`` script is run as a real subprocess with
``sys.executable``, exactly as a user would run it from the repository
root. A script that crashes, prints to stderr, or drifts away from the
current public API fails the suite — examples cannot silently rot.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"

EXAMPLE_SCRIPTS = sorted(EXAMPLES_DIR.glob("*.py"))


def _run_example(script: Path) -> subprocess.CompletedProcess[str]:
    """Run an example as a subprocess and return the completed process."""
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_examples_directory_is_not_empty() -> None:
    """The examples directory ships at least one runnable script."""
    assert EXAMPLE_SCRIPTS, "no examples/*.py scripts found"


@pytest.mark.parametrize(
    "script", EXAMPLE_SCRIPTS, ids=[p.name for p in EXAMPLE_SCRIPTS]
)
def test_example_runs_clean(script: Path) -> None:
    """Every example script exits 0 with no stderr output."""
    proc = _run_example(script)
    assert proc.returncode == 0, (
        f"{script.name} exited {proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
    )
    assert proc.stdout.strip(), f"{script.name} produced no output"


def test_helpers_example_shows_clean_and_broken() -> None:
    """01_lsp_helpers covers a clean doc and malformed-line codes."""
    out = _run_example(EXAMPLES_DIR / "01_lsp_helpers.py").stdout
    assert "clean document diagnostics: []" in out
    assert "4 issue(s)" in out
    assert "malformed-balance" in out
    assert "malformed-statement-line" in out


def test_severity_example_groups_warning() -> None:
    """02_severity_filtering surfaces the orphan-information warning."""
    out = _run_example(EXAMPLES_DIR / "02_severity_filtering.py").stdout
    assert "WARNING" in out
    assert "orphan-information-line" in out


def test_conversion_example_emits_lsp_diagnostic() -> None:
    """03_lsp_conversion prints a converted lsprotocol diagnostic."""
    out = _run_example(EXAMPLES_DIR / "03_lsp_conversion.py").stdout
    assert "[Error]" in out
    assert "malformed-balance" in out


def test_publish_example_covers_every_code() -> None:
    """04_server_publish drives the publish path over every code."""
    out = _run_example(EXAMPLES_DIR / "04_server_publish.py").stdout
    assert "clean: published 0 diagnostic(s)" in out
    for code in (
        "missing-tag",
        "malformed-balance",
        "malformed-statement-line",
        "orphan-information-line",
    ):
        assert code in out, f"04_server_publish never emits {code}"
