<!-- SPDX-License-Identifier: Apache-2.0 -->

# bankstatementparser-lsp Architecture

A map of the codebase for new contributors and maintainers. The goal is
that anyone can navigate, extend, and reason about bankstatementparser-lsp without
prior context.

## The pipeline

```
Editor LSP client (Neovim, VS Code, Helix, ...)
        |  stdio (LSP JSON-RPC)
        v
bankstatementparser_lsp/server.py
   |   |
   |   `-- did_change -> _publish() -> diagnostics_for_mt940() -> [Diagnostic]
   `------ did_open   -> _publish() -> diagnostics_for_mt940() -> [Diagnostic]
                                  |
                                  `-> _to_lsp_diagnostic() -> lsprotocol.Diagnostic
```

The diagnostic engine is pure (no LSP / pygls dependency); the LSP
feature handlers are thin glue that maps the engine's `Diagnostic`
objects into `lsprotocol` types and publishes them.

## Module map

| Area | Module | Responsibility |
| :--- | :--- | :--- |
| **Engine** | `bankstatementparser_lsp/diagnostics.py` | Pure, dependency-free MT940 linter (`diagnostics_for_mt940`, `Diagnostic`, `Severity`) |
| **Server** | `bankstatementparser_lsp/server.py` | pygls `LanguageServer` instance, `did_open` / `did_change` handlers, `_to_lsp_diagnostic` / `_publish` glue |
| **Entry point** | `bankstatementparser_lsp.server:main` (console script: `bankstatementparser-lsp`) | Launches the server over stdio |
| **Version** | `bankstatementparser_lsp/__init__.py` | Single source of truth (`__version__`); re-exports the engine's public surface |
| **Tests** | `tests/test_lsp.py` | Engine unit tests + server glue tests via a fake LanguageServer |
| **Examples** | `examples/` | One runnable script per usage shape |
| **Release helpers** | `scripts/verify_versions.py` | Asserts `__version__`, `pyproject.toml`, and `CHANGELOG.md` agree |

## Editor features

The current LSP surface is diagnostics-only. For each MT940 statement
document the engine emits:

- **`missing-tag`** (error) - a mandatory tag (`:20:`, `:25:`, `:28C:`,
  `:60F:`, `:62F:`) is absent.
- **`malformed-balance`** (error) - a `:60F:` / `:62F:` balance line
  does not match `C/D + YYMMDD + 3-letter currency + amount`.
- **`malformed-statement-line`** (error) - a `:61:` statement line does
  not match `YYMMDD + C/D + amount`.
- **`orphan-information-line`** (warning) - an `:86:` information line
  has no preceding `:61:` statement line.

Diagnostics are republished on `textDocument/didOpen` and
`textDocument/didChange`.

## Pure engine (the public Python surface)

- `diagnostics_for_mt940(text) -> list[Diagnostic]`
- `Diagnostic` - frozen dataclass (`line`, `col_start`, `col_end`,
  `severity`, `message`, `code`)
- `Severity` - `IntEnum` matching the LSP numeric scale

The engine is independently testable; the LSP handlers above it are thin
glue.

## Key design decisions

- **Pure engine, thin server.** All linting logic lives in
  `diagnostics.py` with zero LSP/editor imports, so it is unit-testable
  in isolation and reusable outside an editor.
- **Shared tag patterns.** The balance / statement regexes mirror the
  tag structure the `bankstatementparser` MT940 parser accepts, so editor
  squiggles match what the parser will ingest.
- **Pygls 1.x for runtime parity.** Pinned to `pygls >=1.3,<2`.
- **Coverage enforced at 100%** line+branch and docstring; only the thin
  pygls event bindings and the process entry point are
  `# pragma: no cover`.

## Extension points

- **Add a diagnostic rule:** extend `diagnostics_for_mt940()` in
  `diagnostics.py` to append a new `Diagnostic` with a stable `code`.
- **Surface a new LSP feature:** add an
  `@server.feature(lsp.TEXT_DOCUMENT_*)` handler in `server.py` that
  reuses the engine.

## Where to look first

- Runnable examples: [`examples/`](examples/)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Release process: [`RELEASING.md`](RELEASING.md)
- Parent library: [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser)
