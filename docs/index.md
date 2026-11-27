# bankstatementparser-lsp

A **language server** speaks the
[Language Server Protocol (LSP)](https://microsoft.github.io/language-server-protocol/),
the editor-agnostic protocol that lets one backend deliver diagnostics to
any LSP client (VS Code, Neovim, Helix, Emacs and others).
**bankstatementparser-lsp** is that backend for **MT940 bank-statement
files** (`.mt940` / `.sta`): the SWIFT tag-and-line format parsed by the
[`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser)
library.

The diagnostic engine shares the MT940 tag patterns the
`bankstatementparser` parser relies on, so the squiggles you see in the
editor match the structure the parser will accept.

| Concern | How bankstatementparser-lsp handles it |
| :--- | :--- |
| Mandatory tags | Flags any missing `:20:`, `:25:`, `:28C:`, `:60F:`, `:62F:` tag |
| Balance lines | Validates `:60F:` / `:62F:` against `C/D + YYMMDD + 3-letter currency + amount` |
| Statement lines | Validates `:61:` against `YYMMDD + C/D + amount` |
| Information lines | Warns when an `:86:` line has no preceding `:61:` statement line |
| Live linting | Re-lints on open and on every change, publishing diagnostics back to the editor |

## In this manual

- [Diagnostics](diagnostics.md): the four rules and the engine behind them.
- [Editor wiring](editors.md): Neovim, VS Code, Helix and any stdio client.
- [The suite](suite.md): the `bankstatementparser` packages.
- [Comparison](COMPARISON.md) and [Benchmarks](BENCHMARKS.md).
- [Supported Python policy](POLICIES.md).
- [API reference](api.md): the importable engine and server glue.
- [Roadmap](roadmap.md), [Changelog](changelog.md) and
  [Security policy](security.md).

The source, issues and releases live on
[GitHub](https://github.com/sebastienrousseau/bankstatementparser-lsp);
the package is on [PyPI](https://pypi.org/project/bankstatementparser-lsp/).
