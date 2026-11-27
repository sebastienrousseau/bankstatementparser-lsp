# syntax=docker/dockerfile:1.6
# Multi-stage build for a minimal bankstatementparser-lsp image.
#
# The container runs the pygls language server over stdio so an LSP
# client can launch it directly with ``docker run -i --rm bankstatementparser-lsp``.

# Pinned by digest; Dependabot's docker updater moves it.
FROM python:3.15-slim@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5 AS builder

WORKDIR /build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# requirements/runtime.txt is exported from poetry.lock with hashes, so
# the image installs exactly the locked runtime set; the package itself
# goes on top without resolving anything further.
#
# pyproject.toml carries ``readme = "README.md"``, so README.md must be
# present at build-time for ``pip install .`` to resolve the package
# metadata.
COPY requirements/runtime.txt ./requirements.txt
COPY pyproject.toml README.md ./
COPY bankstatementparser_lsp ./bankstatementparser_lsp

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --require-hashes -r requirements.txt \
    && /opt/venv/bin/pip wheel --no-deps --wheel-dir /tmp/wheels . \
    && /opt/venv/bin/pip install --no-deps /tmp/wheels/*.whl

FROM python:3.15-slim@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5

LABEL org.opencontainers.image.title="bankstatementparser-lsp" \
      org.opencontainers.image.description="Language Server Protocol server that lints MT940 bank-statement files, backed by the bankstatementparser library." \
      org.opencontainers.image.source="https://github.com/sebastienrousseau/bankstatementparser-lsp" \
      org.opencontainers.image.licenses="Apache-2.0 OR MIT"

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
