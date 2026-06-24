<!-- SPDX-License-Identifier: Apache-2.0 -->

# BankStatementParser-LSP VS Code extension

A Language Server Protocol client that brings the bankstatementparser-lsp
diagnostics to VS Code for MT940 bank-statement files (`.mt940` / `.sta`):

- **Diagnostics** - missing mandatory tags (`:20:`, `:25:`, `:28C:`,
  `:60F:`, `:62F:`), malformed `:60F:` / `:62F:` balance lines, malformed
  `:61:` statement lines, and orphan `:86:` information lines.

The extension registers the `mt940` language for `.mt940` / `.sta`
files. The actual engine is the Python `bankstatementparser-lsp` server, so the
same checks back the editor and the rest of the toolchain.

## Prerequisites

```bash
pip install bankstatementparser-lsp   # provides the `bankstatementparser-lsp` server on PATH
```

## Run from source

```bash
cd editors/vscode
npm install
npm run compile
# Then press F5 in VS Code to launch an Extension Development Host.
```

Open any MT940 statement file (`.mt940` / `.sta`); diagnostics appear
inline and in the Problems panel. The server command is controlled by
the `bankstatementparser.serverCommand` setting.

## Packaging / publishing

Building a `.vsix` and publishing to the Marketplace is an external,
credentialed step (`vsce package` / `vsce publish`) and is
intentionally left to a maintainer with publisher access - it is
not part of the Python package's automated build.
