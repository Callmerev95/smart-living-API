# syntax=docker/dockerfile:1

# ==============================================================================
# Smart Living API — image produksi
#
# Build context: ROOT REPO (bukan apps/api), karena image butuh `data/recipes/`.
#   docker build -f docker/api.Dockerfile .
#
# Pola multi-stage mengikuti astral-sh/uv-docker-example: `uv` hanya ada di stage
# builder, image final bersih tanpa build tool.
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1 — builder: pasang dependency ke virtualenv
# ------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 AS builder

# Bytecode dikompilasi saat build agar startup lebih cepat.
ENV UV_COMPILE_BYTECODE=1
# Cache adalah mount, jadi copy alih-alih hardlink.
ENV UV_LINK_MODE=copy
# Dependency dev (pytest, ruff) tidak masuk image produksi.
ENV UV_NO_DEV=1
# Pakai interpreter dari base image, jangan unduh Python lain.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Layer dependency dipisah dari source: perubahan kode tidak membatalkan cache
# instalasi dependency.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=apps/api/uv.lock,target=uv.lock \
    --mount=type=bind,source=apps/api/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY apps/api/pyproject.toml apps/api/uv.lock apps/api/.python-version ./
COPY apps/api/app ./app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# ------------------------------------------------------------------------------
# Stage 2 — runtime: tanpa uv, tanpa dependency dev
# ------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

# Container tidak boleh berjalan sebagai root.
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

COPY --from=builder --chown=nonroot:nonroot /app/.venv ./.venv
COPY --from=builder --chown=nonroot:nonroot /app/app ./app

# Dataset harus ada di image — tanpa ini repository gagal saat startup.
COPY --chown=nonroot:nonroot data/recipes ./data/recipes

# Executable virtualenv di depan PATH agar `uvicorn` bisa dipanggil langsung.
ENV PATH="/app/.venv/bin:$PATH"
# Jangan buffer stdout/stderr supaya log tidak hilang saat container crash.
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Path absolut: `Settings` memakai nilai ini apa adanya, tidak menebak posisi
# repo root seperti saat dijalankan dari checkout.
ENV RECIPES_PATH=/app/data/recipes/recipes.json
ENV INGREDIENTS_PATH=/app/data/recipes/ingredients.json

USER nonroot

EXPOSE 8000

# Railway (dan platform PaaS lain) menyuntikkan PORT saat runtime, jadi perlu
# shell form agar variabelnya diekspansi.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
