# Editor wiring

Register `bankstatementparser-lsp` as the server command for MT940 files
in your editor's LSP client. MT940 files commonly use the `.mt940` or
`.sta` extension; most editors need a filetype mapping for them. The
command takes no arguments and speaks LSP over stdin and stdout.

## Neovim (built-in `vim.lsp.config`)

```lua
-- Map the MT940 extensions to a filetype.
vim.filetype.add({
  extension = {
    mt940 = "mt940",
    sta = "mt940",
  },
})

vim.lsp.config["bankstatementparser"] = {
  cmd = { "bankstatementparser-lsp" },
  filetypes = { "mt940" },
  root_markers = { ".git" },
}
vim.lsp.enable("bankstatementparser")
```

## VS Code (bundled scaffold)

A TypeScript language-client scaffold ships at
[`editors/vscode/`](https://github.com/sebastienrousseau/bankstatementparser-lsp/tree/main/editors/vscode),
runnable straight from source:

```bash
cd editors/vscode
npm install
npm run compile
# Press F5 in VS Code to launch an Extension Development Host.
```

`bankstatementparser.serverCommand` (default `bankstatementparser-lsp`)
is exposed as a setting; the extension activates for `.mt940` / `.sta`
files.

## Helix, Emacs and other clients

Any client that can spawn a stdio language server works. The command is
`bankstatementparser-lsp` and the documents are MT940 statement files
(`.mt940` / `.sta`).

## Docker

The GHCR image runs the same server over stdio:
`docker run --rm -i ghcr.io/sebastienrousseau/bankstatementparser-lsp:latest`.
Use that as the command in any client that can launch one.
