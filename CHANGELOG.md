# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- CI: four pinned actions move to their latest releases:
  codeql-action 4.39.5, markdownlint-cli2-action 25.1.0,
  cosign-installer 4.1.4 and sbom-action 0.24.4.

## [0.0.36] - 2026-11-27

### Added

- An Atheris fuzz target, `fuzz/fuzz_diagnostics.py`, for
  `diagnostics_for_mt940` and the `lsprotocol` conversion, with a seed
  corpus; it fails on any exception or any diagnostic outside the
  document. CI runs it for 120 s on every change; `make fuzz` locally.
- A MkDocs Material user manual (`mkdocs.yml`, `docs/`) with an
  mkdocstrings API reference, built with `--strict` on every pull
  request and deployed to GitHub Pages from `main`
  (`.github/workflows/docs.yml`, `make docs`). It replaces a Sphinx
  configuration that nothing built.
- `docs/POLICIES.md`, `docs/BENCHMARKS.md` (a run of
  `benches/bench_diagnostics.py` with its environment),
  `docs/COMPARISON.md`, `docs/diagnostics.md`, `docs/editors.md` and
  `docs/suite.md`.
- Signed releases: keyless cosign `.sig` and `.pem` per distribution,
  SLSA provenance (`bankstatementparser-lsp-vX.Y.Z.intoto.jsonl`,
  slsa-github-generator 2.1.0), CycloneDX and SPDX SBOMs and a licence
  manifest on every GitHub release, and PEP 740 attestations on PyPI.
- The OpenSSF Scorecard workflow, the suite's Docs Lint workflow
  (`scripts/readme-check.sh` and markdownlint), the portfolio pull
  request template, and `.github/demo.gif` rendered by `make demo` from
  `.github/demo.tape`.
- Hash-pinned requirement sets exported from the lock
  (`requirements/{runtime,ci,fuzz,docs}.txt`, by the suite's
  `scripts/export_locked_requirements.py`) and compiled release tooling
  (`requirements/{build,sbom}.txt`).

### Changed

- Require `bankstatementparser >= 0.0.35`, the newest core release, and
  align the version with the suite's 0.0.36 release; `poetry.lock`
  moves core to 0.0.35.
- CI pins every action by commit SHA, installs only the hashed lock
  exports, and tests CPython 3.10 to 3.14 on Ubuntu, macOS and Windows.
  Write permissions sit on the jobs that need them.
- The Docker image builds from a digest-pinned `python:3.14-slim` and
  installs the locked runtime set with `--require-hashes`; Dependabot
  now tracks the base image.
- `README.md` follows the portfolio template and states the
  Apache-2.0 OR MIT licence; the suite table moves to `docs/suite.md`.
  `CODE-OF-CONDUCT.md` is now `CODE_OF_CONDUCT.md`, and the issue
  templates ask for the editor and an MT940 document.
- `ROADMAP.md` no longer calls v0.0.13 current or targets v0.1.0.
- Diagnostic rules maintained: `missing-tag`, `malformed-balance`,
  `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.

## [0.0.35] - 2026-11-26

### Added

- `scripts/check_complexity.py`, the suite's standard-library
  complexity gate, copied byte for byte from `bankstatementparser`:
  cyclomatic 10, cognitive 15, Halstead difficulty 30 and 60 lines per
  function, 500 lines per file. The 3 functions and files already over
  a ceiling are recorded in `scripts/complexity_baseline.json`; CI and
  `make check` fail when one gets worse, a new one appears, or an
  improvement is left unrecorded, so the baseline can only shrink.

### Changed

- Require `bankstatementparser >= 0.0.34`, the newest core release, and
  align the version with the suite's 0.0.35 release, in which all
  fourteen packages and bankstatementparser.com share one version.
- `scripts/check_suite_consistency.py` now checks all fourteen suite
  packages on PyPI and the bankstatementparser.com GitHub release.
- Development dependency `ruff` updated from 0.17.5 to 0.17.6.
- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.

## [0.0.34] - 2026-11-18

### Changed

- Require `bankstatementparser >= 0.0.33`, the newest core release, and
  align the version with the suite's 0.0.34 release. No other changes.
- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.

## [0.0.33] - 2026-11-18

### Changed

- Require `bankstatementparser >= 0.0.32`, the newest core release, and
  align the version with the suite's 0.0.33 release. No other changes.
- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.

## [0.0.32] - 2026-11-18

### Changed

- Require `bankstatementparser >= 0.0.31`, the newest core release, and
  align the version with the suite's 0.0.32 release.
- Release notes are written by the release workflow. A final
  `release-notes` job runs after every asset is attached and rewrites
  the GitHub release in the suite's format: Highlights, What's Changed,
  New Contributors (when any), Checksums of every asset, and the Full
  Changelog link. Until now the body was the CHANGELOG section,
  with no Highlights or Checksums, so 0.0.31 had to be corrected by
  hand. `softprops/action-gh-release` is no longer used.
- The Highlights are the one hand-written part, kept in
  `.github/releases/<tag>.md`. The build refuses to publish when that
  file is missing, has fewer than 2 or more than 4
  `* **Headline**: text` bullets, or contains an em dash.
- `scripts/release_notes.py`, shared with every suite repository,
  composes the body from the GitHub API and the downloaded assets.
- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.

## [0.0.31] - 2026-11-18

### Changed

- Require `bankstatementparser >= 0.0.30`, the newest core release, and
  align the version with the suite's 0.0.31 release.
- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.
- Release titles read `bankstatementparser-lsp <version>` instead of the bare tag.

## [0.0.30] - 2026-11-18

### Changed

- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.
- Bumped dependency to `bankstatementparser >= 0.0.29`.
- Aligned version with `bankstatementparser` 0.0.30 suite release.
- Updated ruff to 0.17.5 (dev).
- 0.0.29 was prepared but never published; its changes ship in 0.0.30.

## [0.0.28] - 2026-10-11

### Changed

- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.
- Bumped dependency to `bankstatementparser >= 0.0.28`.
- Aligned version with `bankstatementparser` 0.0.28 suite release.

## [0.0.19] - 2026-08-31

### Changed

- Extended MT940 diagnostic regex to support reversal and electronic transaction codes (`RC`, `RD`, `EC`, `ED`) in `malformed-statement-line`.
- Diagnostic rules maintained: `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line`.
- Four runnable examples verified across the test suite.
- Updated `bankstatementparser` dependency floor to `>=0.0.19`.

## [0.0.18] - 2026-08-29

Aligns the `bankstatementparser` suite on one version number, and adds
the scheduled drift check this repository was missing.

### Added

- `scripts/check_suite_consistency.py` and a scheduled **Suite
  Consistency** workflow compare this tree, and every published member of
  the suite, against PyPI. A member left a release behind still installs,
  still imports and still passes its own tests; only the index disagrees,
  and only if somebody goes and looks. This does the looking.

### Changed

- Version aligned to `0.0.18` across all six `bankstatementparser`
  packages, which had drifted to `0.0.14`, `0.0.15`, `0.0.17`, `0.0.16`,
  `0.0.16` and `0.0.15`.
- Refreshed the vendored `tests/test_suite_conformance.py` to the current
  canonical copy. Its drift-check probe now matches the bare word `pypi`
  rather than the hostname, which CodeQL read as an incomplete URL
  sanitisation on a line that never validates a URL.

### Unchanged

No diagnostic behaviour changed in this release. The engine still emits
the same four stable rule codes — `missing-tag`, `malformed-balance`,
`malformed-statement-line` and `orphan-information-line` — and the
repository still ships Four runnable examples under `examples/`.

## [0.0.15] - 2026-08-29

Brings this repository onto the **suite conformance gate**.

### Added

- **`benches/bench_diagnostics.py`** — how long the editor waits.

  A language server is not measured in throughput. It is measured against
  a person typing: the client recomputes diagnostics on every change, so
  the only question is whether the answer arrives before the user
  notices. The table marks two thresholds — **16 ms** (one frame, feels
  instantaneous) and **100 ms** (the limit of "reacting instantly").

  The number to read is the **budget**: how large a document stays
  interactive. It is a budget, not a score.

  For comparison across the three language servers in the suite, all
  doing the same shape of work:

  | Server | Cost | Interactive budget |
  |---|---|---|
  | `bankstatementparser-lsp` | 0.0018 ms/entry | ~56,000 entries |
  | `pain001-lsp` | 0.08 ms/record | ~1,200 records |
  | `camt053-lsp` | **0.86 ms/record** | **~116 records** |

  The malformed column matters too: that is the state a document spends
  most of its life in while somebody is typing. A linter fast on valid
  input and slow on invalid input is slowest exactly when the editor
  calls it most.

  Nothing asserts a timing threshold — wall-clock is not comparable
  between machines, and a flaky performance gate teaches people to
  ignore red. CI runs `--quick`, so a benchmark that stops compiling
  fails the build rather than rotting.

  This server is the fastest of the three by two orders of magnitude:
  0.0018 ms per entry, a budget of roughly 56,000 entries. It lints text
  directly rather than validating records against a schema, which is
  where the difference comes from.

  No functional or API change: the diagnostics engine still emits
  `missing-tag`, `malformed-balance`, `malformed-statement-line`, and
  `orphan-information-line`, and the package still ships
  Four runnable examples.

- **`tests/test_suite_conformance.py`** — invariants shared by every
  repository in the suite, vendored from one canonical copy and
  checksummed by its own test.

### Changed

- CI lints, formats and runs `benches/` alongside everything else.
- `tests/test_suite_conformance.py` is excluded from black: it is
  generated, and the suite uses three different line lengths.

## [0.0.14] - 2026-08-28

### Changed

- **A plain `pytest` now enforces the same 100% coverage floor CI does.**
  `--cov`, `--cov-branch` and `--cov-report=term-missing` move into
  `[tool.pytest.ini_options] addopts`. Before this, running `pytest`
  locally measured no coverage at all: the developer saw green and learned
  otherwise from the build.

  The gate itself was never missing — CI has always run
  `--cov-fail-under=100`, so nothing could regress onto `main` unnoticed.
  What was missing was the local half of it.

- **The floor is stated once.** It was in two places, the
  `--cov-fail-under` flag in `ci.yml` and `fail_under` under
  `[tool.coverage.report]`, which is how two numbers meant to be equal stop
  being equal. pytest-cov honours `fail_under` from the coverage config, so
  the flag is gone from both `addopts` and the workflow and the number lives
  in exactly one place.

  CI now runs `pytest tests/ --cov-report=xml -v`; only the XML report is
  CI-specific.

No functional or API change: the diagnostics engine still emits
`missing-tag`, `malformed-balance`, `malformed-statement-line`, and
`orphan-information-line`, and the package still ships
Four runnable examples.

### Verification

Coverage was already 100% and remains so. The gate was mutation-tested:
adding a function no test calls drops coverage below the floor and fails
the run, locally as well as in CI.

## [0.0.13] - 2026-07-18

### Changed

- chore(deps): require `bankstatementparser>=0.0.11` (was `>=0.0.9`),
  keeping the language server in lockstep with the 0.0.11 core release.
  No functional or API changes: the diagnostics engine still emits
  `missing-tag`, `malformed-balance`, `malformed-statement-line`, and
  `orphan-information-line`, and the package still ships
  Four runnable examples.

## [0.0.12] - 2026-06-25

### Changed

- **Audit pass.** Covered `main`/`did_open`/`did_change` (removed `# pragma: no cover` directives that masked testable code) and made the test-count guard count executed cases via `--collect-only`. The diagnostics engine is unchanged — it still emits `missing-tag`, `malformed-balance`, `malformed-statement-line`, and `orphan-information-line` — and the package still ships Four runnable examples.

## [0.0.11] - 2026-06-24

### Changed

- **Pruned CI over-scaffolding.** Removed the `nightly.yml` and
  `docs.yml` GitHub Actions workflows; the maintained surface is now
  `ci.yml`, `pr.yml`, `codeql.yml`, `security.yml`, `release.yml`, and
  `docker.yml`. No README badge or Makefile target referenced the
  deleted workflows.

### Added

- **Install smoke test** (`smoke` job in `ci.yml`, Python 3.12 / Ubuntu):
  builds the wheel with `python -m build`, installs it into a fresh
  throwaway virtualenv so `bankstatementparser` and `pygls` are pulled
  from PyPI exactly as an end user would get them, prints
  `bankstatementparser_lsp.__version__`, and runs one example
  (`examples/01_lsp_helpers.py`) from a neutral working directory to
  prove the installed package works without the source tree on the path.
- **Expanded golden-style diagnostics tests** asserting exact
  `(line, code, severity)` tuples while keeping 100% line + branch
  coverage. New cases cover: a single document that triggers all four
  rule codes (`missing-tag`, `malformed-balance`,
  `malformed-statement-line`, `orphan-information-line`) at once;
  multiple `:61:` / `:86:` statement/information pairs; CRLF
  (`\r\n`) line endings; leading and trailing blank lines together
  with a UTF-8 BOM; and a fully valid multi-statement MT940 document
  that yields zero diagnostics.

### Fixed

- **UTF-8 BOM false positive.** A leading UTF-8 byte-order mark
  (`U+FEFF`) is not whitespace, so when an MT940 file was exported with a
  BOM it clung to the first tag (`:20:`) and the engine reported a
  spurious `missing-tag` for `:20:`. `diagnostics_for_mt940` now strips a
  single leading BOM before scanning, so BOM-prefixed documents lint
  identically to their plain counterparts. This is the only engine
  behaviour change in this release.

The diagnostic engine still emits the same four codes — `missing-tag`,
`malformed-balance`, `malformed-statement-line`, and
`orphan-information-line` — over the same four runnable examples
(`examples/01_lsp_helpers.py` … `examples/04_server_publish.py`).

[0.0.14]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.14
[0.0.13]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.13
[0.0.12]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.12
[0.0.11]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.11

## [0.0.10] - 2026-06-24

### Added

- Initial release of `bankstatementparser-lsp`, a [pygls](https://github.com/openlawlibrary/pygls)-based
  Language Server Protocol (LSP) server that lints **MT940 bank-statement
  files** (`.mt940` / `.sta`) as you type (Python 3.10+).
- A `bankstatementparser-lsp` console entry point that starts the language server
  over stdio for editor LSP clients.
- **Diagnostics** for MT940 statement documents, backed by a pure,
  dependency-free engine (`diagnostics_for_mt940`) that shares the tag
  patterns the [`bankstatementparser`](https://pypi.org/project/bankstatementparser/)
  MT940 parser relies on:
  - `missing-tag` — a mandatory tag (`:20:`, `:25:`, `:28C:`, `:60F:`,
    `:62F:`) is absent.
  - `malformed-balance` — a `:60F:` / `:62F:` balance line does not match
    `C/D + YYMMDD + 3-letter currency + amount`.
  - `malformed-statement-line` — a `:61:` statement line does not match
    `YYMMDD + C/D + amount`.
  - `orphan-information-line` — an `:86:` information line has no
    preceding `:61:` statement line (warning).
- Pure, importable helpers (`Diagnostic`, `Severity`,
  `diagnostics_for_mt940`) so the diagnostics are unit-testable in
  isolation and reusable outside an editor.
- Four runnable examples (`examples/01_lsp_helpers.py`,
  `examples/02_severity_filtering.py`, `examples/03_lsp_conversion.py`,
  `examples/04_server_publish.py`) covering the clean and broken
  documents, the `Diagnostic` / `Severity` types, the `lsprotocol`
  conversion, and the server's lint-and-publish path (driven by a fake
  `LanguageServer`, so no editor is required).
- Part of the **bankstatementparser suite** alongside the core
  `bankstatementparser` library.
- **Quality gates pinned at 100%** from the initial release:
  - `pytest --cov=bankstatementparser_lsp --cov-branch --cov-fail-under=100`
    covering every line and branch of the diagnostic engine and the
    server's `_to_lsp_diagnostic` / `_publish` glue.
  - `interrogate --fail-under=100` for module and function docstring
    coverage.
  - `ruff` and `mypy --strict` clean.
  - Documentation and example regression suites
    (`tests/test_docs_accuracy.py`, `tests/test_regression_docs.py`,
    `tests/test_regression_examples.py`) that assert the README, docs,
    and shipped examples stay in lockstep with the public API: the
    version string, every exported symbol, every diagnostic rule code,
    and every example path are checked, and each documented `python`
    block and `examples/*.py` script is executed.
- `scripts/verify_versions.py` — pre-release script asserting
  `__version__`, `pyproject.toml`, and `CHANGELOG.md` agree.

[0.0.10]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.10

[0.0.35]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.35
[0.0.34]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.34
[0.0.33]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.33
[0.0.32]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.32
[0.0.31]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.31
[0.0.30]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.30
[0.0.28]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.28
[0.0.19]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.19
