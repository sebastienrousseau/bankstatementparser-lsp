# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  BOM it clung to the first tag (`﻿:20:`) and the engine reported a
  spurious `missing-tag` for `:20:`. `diagnostics_for_mt940` now strips a
  single leading BOM before scanning, so BOM-prefixed documents lint
  identically to their plain counterparts. This is the only engine
  behaviour change in this release.

The diagnostic engine still emits the same four codes — `missing-tag`,
`malformed-balance`, `malformed-statement-line`, and
`orphan-information-line` — over the same four runnable examples
(`examples/01_lsp_helpers.py` … `examples/04_server_publish.py`).

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
