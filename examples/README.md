# bankstatementparser-lsp examples

Runnable, self-contained examples for the **bankstatementparser-lsp** language server.
Run any of them from the repository root:

```sh
python examples/<name>.py
```

| Example | Demonstrates |
|---------|--------------|
| [`01_lsp_helpers.py`](01_lsp_helpers.py) | The pure MT940 diagnostic engine — `diagnostics_for_mt940` over clean, missing-tag, and malformed documents |
| [`02_severity_filtering.py`](02_severity_filtering.py) | Grouping diagnostics by `Severity` (errors vs. warnings) the way an editor colours squiggles |
| [`03_lsp_conversion.py`](03_lsp_conversion.py) | Converting internal diagnostics to `lsprotocol` diagnostics via `_to_lsp_diagnostic`, as the server publishes them |
| [`04_server_publish.py`](04_server_publish.py) | The server's lint-and-publish path (`_publish`) over clean and broken documents, driven by a fake `LanguageServer` so it needs no editor |

These helpers are exactly what the `bankstatementparser-lsp` server runs on each edit,
so you can call them directly to see the diagnostics an editor would receive
for `.mt940` / `.sta` bank-statement files.

Both `bankstatementparser-lsp` and its core dependency `bankstatementparser` must be installed
(Python 3.10+):

```sh
pip install bankstatementparser-lsp
```
