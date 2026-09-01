---
summary: Catalog of every documentation page in this repository, the front door for an agent or a reader who needs to find something without opening every file.
tags: [index, catalog]
updated: 2026-09-01
---

# Documentation index

Documentation for `sezzle-calculator`, a take-home technical assessment: a full-stack
calculator with a React frontend and a Python FastAPI backend.

**If you are evaluating this submission**, start at the root
[`README.md`](../README.md), then read
[ADR-0002](decisions/0002-python-fastapi-instead-of-go.md), which argues the one deliberate
departure from the brief.

**If you are an agent**, read [`CLAUDE.md`](CLAUDE.md) first. It is the schema and it
overrides defaults.

## Start here

| Page | What it gives you |
|---|---|
| [`../README.md`](../README.md) | Setup, how to run each layer, API examples, design decisions. The graded front door |
| [`architecture.md`](architecture.md) | The whole design: goals, constraints, containers, components, runtime, deployment and continuous integration, quality, risks |
| [`CLAUDE.md`](CLAUDE.md) | Wiki schema. How this documentation is structured and maintained |

## Decisions

Eight substantive decisions plus the meta-decision. Full rationale, including rejected
alternatives.

| ADR | Decision recorded | Status |
|---|---|---|
| [0001](decisions/0001-record-architecture-decisions.md) | Decisions carrying risk get a numbered record; routine choices do not | Accepted |
| [0002](decisions/0002-python-fastapi-instead-of-go.md) | Python and FastAPI instead of the brief's preferred Go, with the cost stated plainly | Accepted |
| [0003](decisions/0003-single-calculate-endpoint.md) | One generic `POST /api/calculations` rather than an endpoint per operation | Accepted |
| [0004](decisions/0004-exact-decimal-arithmetic.md) | Exact decimal arithmetic, and JSON string transport so the client cannot undo it | Accepted |
| [0005](decisions/0005-error-model-and-status-codes.md) | One error envelope, stable codes, 422 for anything well-formed but not computable | Accepted |
| [0006](decisions/0006-shadcn-ui-component-library.md) | shadcn/ui on Radix, generated into the repository rather than imported, so the component code is ours | Accepted |
| [0007](decisions/0007-api-first-openapi-contract.md) | A hand-authored `openapi.yaml` as the source of truth, enforced by a drift check | Accepted |
| [0008](decisions/0008-generate-all-wire-types.md) | Every wire type generated from the contract on both sides, with Zod validating responses at runtime | Accepted |
| [0009](decisions/0009-toolchain.md) | uv, pnpm, Ruff, Biome, and `ty` as a non-blocking check because it is pre-1.0 | Accepted |

## Sources

| Page | Summary |
|---|---|
| [`sources/assignment-brief.md`](sources/assignment-brief.md) | The assignment requirements, the deliverables checklist, and the ambiguities that became documented assumptions |

Raw, unmodified sources are in [`raw/`](raw/). Wiki pages cite the summary page above, not
the raw file.

## Other

| Page | Summary |
|---|---|
| [`13-prompt-record.md`](13-prompt-record.md) | Chronological record of prompts used to build this repository. **An explicit deliverable of the brief** |
| [`log.md`](log.md) | Chronological record of documentation operations |

## Common questions, and where they are answered

| Question | Page |
|---|---|
| Why not Go, when the brief preferred it? | [ADR-0002](decisions/0002-python-fastapi-instead-of-go.md) |
| Why is `0.1 + 0.2` exactly `0.3` here? | [ADR-0004](decisions/0004-exact-decimal-arithmetic.md) |
| Why are operands JSON strings instead of numbers? | [ADR-0004](decisions/0004-exact-decimal-arithmetic.md), transport section |
| Why one endpoint instead of one per operation? | [ADR-0003](decisions/0003-single-calculate-endpoint.md) |
| Is this really API-first, given FastAPI generates a spec? | [ADR-0007](decisions/0007-api-first-openapi-contract.md) |
| Does the keypad mean the frontend computes? | [`architecture.md`](architecture.md) § 5.3. It does not |
| Why a component library instead of plain CSS? | [ADR-0006](decisions/0006-shadcn-ui-component-library.md) |
| Why generate types instead of writing them? | [ADR-0008](decisions/0008-generate-all-wire-types.md) |
| Why validate responses at runtime as well? | [ADR-0008](decisions/0008-generate-all-wire-types.md) |
| Why is the type check not blocking in CI? | [ADR-0009](decisions/0009-toolchain.md) |
| How do I run this? | [`../README.md`](../README.md), `just dev` |
| Why does division by zero return 422 and not 400? | [ADR-0005](decisions/0005-error-model-and-status-codes.md) |
| What does "percentage" mean here? | [`architecture.md`](architecture.md) § 11.3 |
| What was left out on purpose? | [`architecture.md`](architecture.md) § 11.2 |
| How is this tested? | [`architecture.md`](architecture.md) § 8.4 |
