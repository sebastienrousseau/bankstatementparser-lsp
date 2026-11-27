# API reference

The importable Python surface: the pure diagnostic engine, which any
tool can call in-process, and the server glue that maps its results to
`lsprotocol` and publishes them. Generated from the docstrings by
mkdocstrings.

::: bankstatementparser_lsp.diagnostics

::: bankstatementparser_lsp.server
    options:
      members:
        - main
        - did_open
        - did_change
        - "_to_lsp_diagnostic"
        - "_publish"
