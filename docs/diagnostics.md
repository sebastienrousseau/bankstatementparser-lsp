# Diagnostics

For MT940 bank-statement documents (one statement of SWIFT-style
`:tag:` lines), the server publishes these diagnostics:

| Rule code | Severity | Behaviour |
| :--- | :--- | :--- |
| `missing-tag` | error | A mandatory tag (`:20:`, `:25:`, `:28C:`, `:60F:`, `:62F:`) is absent |
| `malformed-balance` | error | A `:60F:` / `:62F:` balance line does not match `C/D + YYMMDD + 3-letter currency + amount` |
| `malformed-statement-line` | error | A `:61:` statement line does not match `YYMMDD + C/D + amount` |
| `orphan-information-line` | warning | An `:86:` information line has no preceding `:61:` statement line |

Diagnostics are republished on `textDocument/didOpen` and
`textDocument/didChange`, so the editor stays in sync on every keystroke.
An empty or whitespace-only document produces no diagnostics. A single
leading UTF-8 byte-order mark is ignored, and CRLF line endings lint the
same as LF.

## The engine

The rules live in a pure, importable engine with no LSP dependency:
`diagnostics_for_mt940(text)` returns a list of `Diagnostic` objects.
Each exposes `line`, `col_start`, `col_end` (a 0-based range),
`severity` (a `Severity` enum matching the LSP numeric scale: 1 error,
2 warning, 3 information, 4 hint), `message` and a stable `code`. The
server maps each one to an `lsprotocol.Diagnostic` (source
`bankstatementparser`) before publishing.

Because the engine is pure, you can call it from Python without an
editor or a server process; the README's Examples section and
[`examples/`](https://github.com/sebastienrousseau/bankstatementparser-lsp/tree/main/examples)
show how.

## Fuzzing

`fuzz/fuzz_diagnostics.py` drives `diagnostics_for_mt940` and the
`lsprotocol` conversion with Atheris in CI. It fails on any exception and
on any diagnostic whose range falls outside the document.
