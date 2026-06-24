<!-- SPDX-License-Identifier: Apache-2.0 -->

# Getting support

Thanks for using bankstatementparser-lsp. Here's the fastest way to get help, by
need.

## Questions & how-to

- **Read first:** the [README](README.md), the runnable
  [`examples/`](examples/) (engine walkthrough, severity grouping,
  `lsprotocol` conversion), and the parent
  [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) repo for
  MT940 statement-format background.
- **Still stuck?** Open a
  [GitHub Discussion](https://github.com/sebastienrousseau/bankstatementparser/discussions)
  on the parent repo (shared with bankstatementparser and bankstatementparser-mcp) or a question
  issue here. Include your Python version, `bankstatementparser-lsp` version
  (`python -c "import bankstatementparser_lsp; print(bankstatementparser_lsp.__version__)"`), your
  editor + LSP client, and a minimal reproducer.

## Bugs

Open a bug report at
<https://github.com/sebastienrousseau/bankstatementparser-lsp/issues/new> with a
minimal reproducer, the file type you're editing (JSON record array or
CSV), and what you saw vs what you expected.

## Feature requests

Open a feature request at
<https://github.com/sebastienrousseau/bankstatementparser-lsp/issues/new>. Editor
features that surface more of the
[`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) public API are
especially welcome - see [ARCHITECTURE.md](ARCHITECTURE.md) for the
extension points and [ROADMAP.md](ROADMAP.md) for what's planned.

## Security

**Do not** open public issues for vulnerabilities. Follow the private
disclosure process in [SECURITY.md](SECURITY.md).

## Contributing & maintaining

See [CONTRIBUTING.md](CONTRIBUTING.md) and [GOVERNANCE.md](GOVERNANCE.md).

## Supported versions

Fixes land on the latest release line. See [SECURITY.md](SECURITY.md)
for the supported-version policy. bankstatementparser-lsp requires Python 3.10+.
