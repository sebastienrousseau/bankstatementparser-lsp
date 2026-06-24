# Contributing to bankstatementparser-lsp

Thank you for your interest in contributing to **bankstatementparser-lsp**, the Language
Server Protocol server for the [bankstatementparser](https://github.com/sebastienrousseau/bankstatementparser)
suite. This guide covers the development workflow and standards.

## Development Setup

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- Git with SSH commit signing configured

### Setup

```bash
# Clone and install
git clone git@github.com:sebastienrousseau/bankstatementparser-lsp.git
cd bankstatementparser-lsp
poetry install

# Verify
poetry run pytest tests/ -q
```

The package depends on the core `bankstatementparser` library and `pygls`; both are
installed automatically by `poetry install`.

### On macOS

```bash
brew install python@3.12 poetry
```

### On Linux (Debian/Ubuntu)

```bash
sudo apt install python3 python3-pip
pip install poetry
```

### On WSL

```bash
sudo apt install python3 python3-pip
pip install poetry
# Ensure ~/.local/bin is in PATH
```

## Workflow

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
3. **Make changes** - follow the coding standards below
4. **Run tests**:
   ```bash
   poetry run pytest tests/ -v
   ```
5. **Run linters**:
   ```bash
   poetry run ruff check bankstatementparser_lsp/
   poetry run mypy bankstatementparser_lsp/
   poetry run black --check bankstatementparser_lsp/ tests/
   ```
6. **Sign and commit**:
   ```bash
   git commit -S -m "feat: add my feature"
   ```
7. **Push** and open a pull request

## Commit Signing (Required)

All commits **must** be signed with SSH or GPG.

### SSH Signing

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519
git config --global commit.gpgsign true
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add a continuity check for closing :62F: balances
fix: handle CRLF line endings in MT940 documents
docs: update README with editor wiring examples
test: cover the orphan information-line diagnostic path
refactor: simplify the MT940 tag-matching helper
```

## Coding Standards

- **Line length:** 79 characters (enforced by Black + Ruff)
- **Type hints:** Required on all public functions (mypy strict)
- **Docstrings:** Required on all public classes and functions
- **Tests:** Every new feature must include tests

## Testing

```bash
# Full suite
poetry run pytest tests/ -v

# Single file
poetry run pytest tests/test_lsp.py -v
```

## Pull Request Checklist

- [ ] All tests pass (`poetry run pytest`)
- [ ] Linters pass (`ruff check`, `mypy`, `black --check`)
- [ ] Commits are signed
- [ ] PR title follows conventional commit format
- [ ] New features include tests and documentation

## License

By contributing, you agree that your contributions will be licensed under
the [Apache License 2.0](LICENSE).
