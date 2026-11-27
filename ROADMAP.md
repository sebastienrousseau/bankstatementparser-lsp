# bankstatementparser-lsp Roadmap

This roadmap tracks the next set of capabilities for the LSP companion
of the [bankstatementparser](https://github.com/sebastienrousseau/bankstatementparser) library.
Releases stay on the `0.0.x` line, one `0.0.1` step at a time with the
rest of the suite, so the sections below are ordered, not versioned;
releases ship when the gates pass, not on a calendar.

## Shipped (0.0.36, current)

- MT940 diagnostics over stdio: missing mandatory tags, malformed
  balance lines (`:60F:` / `:62F:`), malformed statement lines (`:61:`),
  and orphan information lines (`:86:`).
- Pure, importable diagnostic engine (`diagnostics_for_mt940`), now
  robust to a leading UTF-8 BOM and CRLF line endings.
- 100% line+branch coverage gate, 100% docstring coverage gate.
- Golden-style diagnostics tests pinning exact `(line, code, severity)`
  tuples; wheel-install smoke test in CI; pruned CI workflows.
- Four runnable examples covering the engine, severity grouping, the
  `lsprotocol` conversion, and the server's publish path.
- Tested on Linux, macOS and Windows with CPython 3.10 to 3.14; Atheris
  fuzzing of the engine; signed releases with SLSA provenance; a
  digest-pinned container image; a MkDocs user manual.

## Next: richer statement diagnostics

- Balance continuity checks: warn when a closing `:62F:` balance does
  not equal the opening `:60F:` balance plus the sum of `:61:` lines.
- Statement-number / sequence checks across `:28C:` pages.
- `textDocument/documentSymbol` so editors can outline each statement by
  its `:25:` account / `:28C:` statement number.

## Later: authoring-grade UX

- Targeted code actions per diagnostic (e.g. "insert missing `:60F:`
  opening balance").
- `textDocument/hover` describing the tag under the cursor.
- CAMT (ISO 20022 XML) statement diagnostics behind a URI-suffix
  dispatch, reusing the core `bankstatementparser` parser.

## Out of scope (handled elsewhere)

- **Full parsing into structured records** - see the core
  [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) library.
