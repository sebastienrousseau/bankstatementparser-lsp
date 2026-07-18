# syntax=docker/dockerfile:1.6
# Multi-stage build for a minimal bankstatementparser-lsp image.
#
# The container runs the pygls language server over stdio so an LSP
# client can launch it directly with ``docker run -i --rm bankstatementparser-lsp``.

FROM python:3.12-slim AS builder

WORKDIR /build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Pin can be overridden at build-time so the GHCR pipeline can install
# bankstatementparser from a matching feat/* branch before the parent release hits
# PyPI; the default resolves the published version once available. The
# git client is needed only when the override spec is a git+ URL; it
# stays in this build stage and never ships in the final image.
ARG BANKSTATEMENTPARSER_PIP_SPEC="bankstatementparser>=0.0.11"
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# pyproject.toml carries ``readme = "README.md"``, so README.md must be
# present at build-time for ``pip install .`` to resolve the package
# metadata.
COPY pyproject.toml README.md ./
COPY bankstatementparser_lsp ./bankstatementparser_lsp

# Install bankstatementparser from PyPI (or the override spec), then layer this
# package on top inside a self-contained virtualenv.
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install "$BANKSTATEMENTPARSER_PIP_SPEC" \
    && /opt/venv/bin/pip install .


FROM python:3.12-slim

LABEL org.opencontainers.image.title="bankstatementparser-lsp" \
      org.opencontainers.image.description="Language Server Protocol server that lints MT940 bank-statement files, backed by the bankstatementparser library." \
      org.opencontainers.image.source="https://github.com/sebastienrousseau/bankstatementparser-lsp" \
      org.opencontainers.image.licenses="Apache-2.0"

# Non-root user (LSP clients launch the container with stdio; no extra
# privileges needed).
RUN groupadd --system lsp && useradd --system --gid lsp --home /home/lsp lsp \
    && mkdir -p /home/lsp \
    && chown -R lsp:lsp /home/lsp

COPY --from=builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER lsp
WORKDIR /home/lsp

# A non-zero exit here means an import / dependency mismatch; the LSP
# client will see it before the first request.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import bankstatementparser_lsp.server" || exit 1

ENTRYPOINT ["bankstatementparser-lsp"]
