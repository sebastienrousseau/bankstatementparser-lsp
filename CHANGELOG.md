# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2026-06-24

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
- Three runnable examples (`examples/01_lsp_helpers.py`,
  `examples/02_severity_filtering.py`, `examples/03_lsp_conversion.py`).
- Part of the **bankstatementparser suite** alongside the core
  `bankstatementparser` library.
- **Quality gates pinned at 100%** from the initial release:
  - `pytest --cov=bankstatementparser_lsp --cov-branch --cov-fail-under=100`
    covering every line and branch of the diagnostic engine and the
    server's `_to_lsp_diagnostic` / `_publish` glue.
  - `interrogate --fail-under=100` for module and function docstring
    coverage.
  - `ruff` and `mypy --strict` clean.
- `scripts/verify_versions.py` — pre-release script asserting
  `__version__`, `pyproject.toml`, and `CHANGELOG.md` agree.

[0.0.1]: https://github.com/sebastienrousseau/bankstatementparser-lsp/releases/tag/v0.0.1
