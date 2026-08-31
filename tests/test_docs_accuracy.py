# Copyright (C) 2023-2026 Bank Statement Parser. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0

"""Automated validation that README, docs, and examples stay in sync
with the actual codebase.

If any of these tests fail, the corresponding markdown file has a stale
claim that a human will trust and act on. Fix the docs, not the test.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import bankstatementparser_lsp
from bankstatementparser_lsp import diagnostics as diag_mod

# ---------------------------------------------------------------------------
# Repo paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"
EXAMPLES_README = REPO_ROOT / "examples" / "README.md"

SRC_DIR = REPO_ROOT / "bankstatementparser_lsp"
TESTS_DIR = REPO_ROOT / "tests"
EXAMPLES_DIR = REPO_ROOT / "examples"

# The stable rule codes the diagnostic engine emits. Kept here as the
# single source of truth the README/CHANGELOG are checked against.
DIAGNOSTIC_CODES = (
    "missing-tag",
    "malformed-balance",
    "malformed-statement-line",
    "orphan-information-line",
)


def _read(path: Path) -> str:
    """Return the UTF-8 text of a file."""
    return path.read_text(encoding="utf-8")


def _pyproject_version() -> str:
    """Return the version declared in pyproject.toml."""
    match = re.search(r'^version\s*=\s*"([^"]+)"', _read(PYPROJECT), re.M)
    assert match is not None, "pyproject.toml has no version field"
    return match.group(1)


# ---------------------------------------------------------------------------
# 1. Version consistency: badge / pyproject / __version__ / verify script
# ---------------------------------------------------------------------------


class TestVersionConsistency:
    """The version string agrees across every source of truth."""

    def test_package_version_matches_pyproject(self) -> None:
        assert bankstatementparser_lsp.__version__ == _pyproject_version()

    def test_changelog_has_current_version_entry(self) -> None:
        version = _pyproject_version()
        assert f"[{version}]" in _read(
            CHANGELOG
        ), f"CHANGELOG has no entry for current version {version}"

    def test_readme_verify_snippet_matches_version(self) -> None:
        """The README install-check shows the real current version."""
        readme = _read(README)
        version = bankstatementparser_lsp.__version__
        assert (
            f"bankstatementparser-lsp {version}" in readme
        ), f"README install-check should print version {version}"

    def test_readme_state_line_matches_version(self) -> None:
        """The README 'Current state (vX)' line uses the real version."""
        readme = _read(README)
        version = _pyproject_version()
        assert (
            f"v{version}" in readme
        ), f"README should reference v{version} in its current-state line"


# ---------------------------------------------------------------------------
# 2. Public API surface documented
# ---------------------------------------------------------------------------


class TestApiSurface:
    """Every public symbol and rule code is documented in the README."""

    readme_text = _read(README)

    def test_all_exports_present(self) -> None:
        assert set(bankstatementparser_lsp.__all__) == {
            "Diagnostic",
            "Severity",
            "diagnostics_for_mt940",
        }

    def test_exported_symbols_in_readme(self) -> None:
        for sym in bankstatementparser_lsp.__all__:
            assert (
                sym in self.readme_text
            ), f"README doesn't mention public symbol '{sym}'"

    def test_diagnostic_codes_in_readme(self) -> None:
        for code in DIAGNOSTIC_CODES:
            assert (
                f"`{code}`" in self.readme_text
            ), f"README doesn't document diagnostic code '{code}'"

    def test_server_conversion_symbol_in_readme(self) -> None:
        """The server's lsprotocol conversion is mentioned in the docs."""
        assert "lsprotocol" in self.readme_text

    def test_diagnostic_codes_match_engine_source(self) -> None:
        """Every documented code is actually emitted by the engine."""
        source = _read(SRC_DIR / "diagnostics.py")
        for code in DIAGNOSTIC_CODES:
            assert (
                f'code="{code}"' in source
            ), f"diagnostics.py never emits documented code '{code}'"

    def test_no_undocumented_codes(self) -> None:
        """The engine emits no code the README forgets to document."""
        source = _read(SRC_DIR / "diagnostics.py")
        emitted = set(re.findall(r'code="([a-z-]+)"', source))
        assert emitted == set(
            DIAGNOSTIC_CODES
        ), f"engine codes {emitted} != documented {set(DIAGNOSTIC_CODES)}"


# ---------------------------------------------------------------------------
# 3. CHANGELOG documents the public surface
# ---------------------------------------------------------------------------


class TestChangelogAccuracy:
    """The CHANGELOG documents every code and example for this version."""

    changelog_text = _read(CHANGELOG)

    def test_current_version_documents_codes(self) -> None:
        version = _pyproject_version()
        section = self.changelog_text.split(f"[{version}]")[1]
        section = section.split("\n## [")[0]
        for code in DIAGNOSTIC_CODES:
            assert (
                f"`{code}`" in section
            ), f"CHANGELOG v{version} doesn't document code '{code}'"

    def test_changelog_example_count_matches_reality(self) -> None:
        version = _pyproject_version()
        section = self.changelog_text.split(f"[{version}]")[1]
        section = section.split("\n## [")[0]
        match = re.search(r"(\w+) runnable examples", section)
        assert (
            match is not None
        ), "CHANGELOG should state the runnable-example count"
        words = {"Three": 3, "Four": 4, "Five": 5}
        claimed = words.get(match.group(1).capitalize())
        assert (
            claimed is not None
        ), f"unrecognised example count word: {match.group(1)!r}"
        actual = len(list(EXAMPLES_DIR.glob("*.py")))
        assert (
            claimed == actual
        ), f"CHANGELOG claims {claimed} examples but actual is {actual}"


# ---------------------------------------------------------------------------
# 4. Examples exist, are referenced, and numeric claims match
# ---------------------------------------------------------------------------


class TestExamplesExist:
    """Every referenced example exists and the counts are accurate."""

    readme_text = _read(README)
    examples_readme_text = _read(EXAMPLES_README)

    def _referenced_scripts(self, text: str) -> list[str]:
        return re.findall(r"`((?:examples/)?\w+\.py)`", text)

    def test_readme_example_paths_exist(self) -> None:
        for ref in self._referenced_scripts(self.readme_text):
            name = ref.split("/")[-1]
            assert (
                EXAMPLES_DIR / name
            ).exists(), f"README references {ref} but file doesn't exist"

    def test_examples_readme_paths_exist(self) -> None:
        for ref in self._referenced_scripts(self.examples_readme_text):
            name = ref.split("/")[-1]
            assert (
                EXAMPLES_DIR / name
            ).exists(), (
                f"examples/README.md references {ref} but file is missing"
            )

    def test_every_example_is_listed_in_examples_readme(self) -> None:
        listed = {
            ref.split("/")[-1]
            for ref in self._referenced_scripts(self.examples_readme_text)
        }
        for script in EXAMPLES_DIR.glob("*.py"):
            assert (
                script.name in listed
            ), f"examples/README.md doesn't list {script.name}"

    def test_test_count_claim_matches_reality(self) -> None:
        """Every 'N tests' claim in the README is the real count."""
        actual = _actual_test_count()
        for claimed in re.findall(r"(\d+)\s+tests", self.readme_text):
            assert (
                int(claimed) == actual
            ), f"README claims {claimed} tests but actual is {actual}"


# ---------------------------------------------------------------------------
# 5. Module count and severities documented
# ---------------------------------------------------------------------------


def _actual_test_count() -> int:
    """Return the number of test cases pytest actually collects.

    This counts the real executed cases — including every parametrised
    instance — by asking pytest to collect the suite, so a ``N tests``
    claim in the README must match what genuinely runs, not merely the
    number of ``def test_`` functions.
    """
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            str(TESTS_DIR),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    match = re.search(r"(\d+)\s+tests?\s+collected", proc.stdout)
    assert match is not None, (
        "could not determine collected test count from pytest output:\n"
        f"{proc.stdout}\n{proc.stderr}"
    )
    return int(match.group(1))


class TestEngineClaims:
    """README claims about the engine match the engine itself."""

    readme_text = _read(README)

    def test_required_tags_documented(self) -> None:
        for tag in diag_mod._REQUIRED_TAGS:
            assert (
                tag in self.readme_text
            ), f"README doesn't mention required tag {tag}"

    def test_severity_scale_documented(self) -> None:
        """The README references the Severity enum used by diagnostics."""
        assert "Severity" in self.readme_text
        assert diag_mod.Severity.ERROR.value == 1
        assert diag_mod.Severity.WARNING.value == 2

    def test_mermaid_diagram_present(self) -> None:
        assert "```mermaid" in self.readme_text
        assert "diagnostics_for_mt940" in self.readme_text
