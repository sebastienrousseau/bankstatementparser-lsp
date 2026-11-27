# Comparison

Where bankstatementparser-lsp fits next to the tools a reader would
otherwise reach for. Every cell comes from this repository or the linked
project's own README; nothing here is a measured ranking.

| Project | Format | Interface | What it gives you |
| :--- | :--- | :--- | :--- |
| **bankstatementparser-lsp** | MT940 | Language Server Protocol (stdio) | Live diagnostics while editing |
| [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) | CAMT, pain.001, CSV, OFX, QFX, MT940, PDF | Python library and CLI | Parsed statements as structured records |
| [`bankstatementparser-mcp`](https://github.com/sebastienrousseau/bankstatementparser-mcp) | CAMT.053, pain.001, MT940, OFX, QFX, CSV | Model Context Protocol tools | Detection, parsing and validation for AI agents |

## When each fits

- **bankstatementparser-lsp**: you write or edit MT940 statements by hand
  and want missing tags and malformed lines flagged as you type.
- **bankstatementparser**: you need the parsed transactions, not editor
  feedback.
- **bankstatementparser-mcp**: an AI agent reads the statements.

The wider family is listed in [The suite](suite.md).
