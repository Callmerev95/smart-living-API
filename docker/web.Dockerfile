# syntax=docker/dockerfile:1

# ==============================================================================
# Smart Living Web (Next.js) — image produksi
#
# Build context: ROOT REPO (konsisten dengan api.Dockerfile).
#   docker build -f docker/web.Dockerfile .
#
# PENTING: `NEXT_PUBLIC_*` dibakar saat build, bukan saat runtime. URL API
# produksi harus dikirim sebagai build-arg — nilai di sini hanya default untuk
# lokal (`docs/deployment.md` menjelaskan alur ini).
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1 — dependencies: pnpm install dengan cache store
# ------------------------------------------------------------------------------
FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS dependencies

# pnpm via corepack — versi dibaca dari package.json `packageManager`.
RUN corepack enable

WORKDIR /app

RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    --mount=type=bind,source=apps/web/package.json,target=package.json \
    --mount=type=bind,source=apps/web/pnpm-lock.yaml,target=pnpm-lock.yaml \
    pnpm install --frozen-lockfile

# ------------------------------------------------------------------------------
# Stage 2 — builder: build Next.js standalone
# ------------------------------------------------------------------------------
FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS builder

RUN corepack enable

WORKDIR /app

ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=dependencies /app/node_modules ./node_modules
COPY apps/web/package.json apps/web/pnpm-lock.yaml apps/web/tsconfig.json apps/web/next.config.ts apps/web/postcss.config.mjs apps/web/eslint.config.mjs ./
COPY apps/web/app ./app
COPY apps/web/types ./types
COPY apps/web/lib ./lib
COPY apps/web/hooks ./hooks
COPY apps/web/components ./components

RUN pnpm build

# ------------------------------------------------------------------------------
# Stage 3 — runner: hanya hasil standalone, tanpa node_modules penuh
# ------------------------------------------------------------------------------
FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

WORKDIR /app

# standalone sudah berisi server.js + node_modules hasil trace Next.js.
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

USER node

EXPOSE 3000

CMD ["node", "server.js"]
