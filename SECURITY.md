# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in bankstatementparser-lsp, please email
**security@bankstatementparser.com** instead of using the issue tracker.

Please include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)

We will acknowledge receipt within 48 hours and provide updates on
remediation timeline.

## Threat Model

`bankstatementparser-lsp` is a Language Server Protocol server. It runs locally over
stdio under the user's editor process, so its security surface is:

- **Document contents** - MT940 statement files (`.mt940` / `.sta`) an
  editor sends via `textDocument/didOpen` and `textDocument/didChange`.

There is **no network listener, no caller-supplied filesystem path, and
no shell-out**. The server's behaviour is bounded by what the editor
chooses to send.

## Hardening

- **Pure-`re` line scanner** - the diagnostic engine
  (`diagnostics_for_mt940`) is a pure function of the document text using
  only the standard-library `re` module; no `eval`, no `json`/XML
  parsing, no file or network access.
- **No code execution from documents** - diagnostics are derived solely
  from matching MT940 tag patterns against the text.
- **Errors don't leak tracebacks** - the engine returns plain
  `Diagnostic` objects; the server maps them to `lsprotocol.Diagnostic`
  with no stack frames.

## Continuous Integration

- `ci.yml` runs the full quality matrix (ruff, mypy, pytest with the
  100% coverage gate, interrogate).
- `security.yml` runs `bandit` against the package on every push and
  weekly via cron.
- `codeql.yml` runs GitHub's CodeQL Python analysis weekly.

## Cryptography Status

`bankstatementparser-lsp` does not perform cryptographic operations.

## Contact

- **Email**: security@bankstatementparser.com
- **GitHub Advisories**: https://github.com/sebastienrousseau/bankstatementparser-lsp/security/advisories
- **GitHub Discussions**: https://github.com/sebastienrousseau/bankstatementparser/discussions
