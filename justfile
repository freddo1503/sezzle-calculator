# Every command in this repository is a recipe here. A developer, continuous
# integration and an AI agent all enter through `just`, so there is no second,
# undocumented way to build, generate or test this project.
#
# See .claude/rules/principles.md, "Don't Repeat Yourself".

set shell := ["bash", "-euo", "pipefail", "-c"]
set dotenv-load := false

backend := "backend"
frontend := "frontend"
contract := "openapi.yaml"

# List the recipes. Running `just` with no argument lands here.
default:
    @just --list --unsorted

# ---------------------------------------------------------------- environment

# Install both layers from a clean clone.
install:
    cd {{backend}} && uv sync
    cd {{frontend}} && pnpm install --frozen-lockfile

# Install, generate from the contract, then run both layers with reload.
dev: install generate
    #!/usr/bin/env bash
    set -euo pipefail
    trap 'kill 0' EXIT INT TERM
    cd {{backend}} && uv run uvicorn app.main:app --reload --port 8000 &
    cd {{frontend}} && pnpm dev &
    wait

# Run the backend alone, with reload, on port 8000.
backend:
    cd {{backend}} && uv run uvicorn app.main:app --reload --port 8000

# Run the frontend alone, on the Vite development server.
frontend:
    cd {{frontend}} && pnpm dev

# ----------------------------------------------------------------- generation

# Regenerate every type, model, client and schema from the contract.
generate: generate-backend generate-frontend

# Pydantic models from the contract. Never edit app/contract.py by hand.
generate-backend:
    cd {{backend}} && uv run datamodel-codegen \
        --input ../{{contract}} \
        --input-file-type openapi \
        --output-model-type pydantic_v2.BaseModel \
        --use-annotated \
        --field-constraints \
        --formatters ruff-format \
        --output app/contract.py

# TypeScript types, HTTP client and Zod schemas from the contract.
generate-frontend:
    cd {{frontend}} && pnpm exec orval --config ../orval.config.ts

# ------------------------------------------------------------------ verifying

# The contract is a valid OpenAPI document.
check-contract:
    cd {{backend}} && uv run openapi-spec-validator ../{{contract}}

# Every generated artefact is current. Fails if `just generate` would change anything.
check-generated: generate
    git diff --exit-code -- {{backend}}/app/contract.py {{frontend}}/src/api

# --------------------------------------------------------------------- checks

# Lint and format both layers, writing fixes.
lint:
    cd {{backend}} && uv run ruff check --fix . && uv run ruff format .
    cd {{frontend}} && pnpm exec biome check --write .

# Lint and format both layers without writing. What continuous integration runs.
check-lint:
    cd {{backend}} && uv run ruff check . && uv run ruff format --check .
    cd {{frontend}} && pnpm exec biome ci .

# Type-check the backend. Non-blocking in continuous integration: `ty` is beta,
# and an unpinned beta regression must not redden a public repository.
typecheck:
    cd {{backend}} && uv run ty check

# ---------------------------------------------------------------------- tests

# Unit tests for both layers.
test: test-backend test-frontend

test-backend:
    cd {{backend}} && uv run pytest

test-frontend:
    cd {{frontend}} && pnpm exec vitest run

# Unit tests with coverage. Reported as a fact, never gated on a threshold.
coverage:
    cd {{backend}} && uv run pytest --cov --cov-report=term-missing --cov-report=xml
    cd {{frontend}} && pnpm exec vitest run --coverage

# The one end-to-end test, against the assembled stack.
e2e: up
    cd {{frontend}} && pnpm exec playwright test
    just down

# ------------------------------------------------------------------- assembled

# Build and run the assembled stack. Not the development path; see `just dev`.
up:
    docker compose up --build --detach --wait

# Stop the assembled stack.
down:
    docker compose down --volumes

# ------------------------------------------------------------------------- ci

# Everything continuous integration runs, in order, blocking steps only.
ci: check-contract check-generated check-lint coverage e2e
