---
number: 7
title: API-first, with a hand-authored OpenAPI contract and generated frontend types
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: A hand-authored openapi.yaml at the repository root is the source of truth for both layers, enforced by a continuous integration check that fails on drift between it and FastAPI's generated document, with frontend TypeScript types generated from it rather than written by hand.
tags: [api, contract, openapi, codegen, ci]
updated: 2026-09-01
---

# ADR-0007: API-first, with a hand-authored OpenAPI contract and generated frontend types

## Context

Two layers have to agree on one contract: the request shape, the operation enumeration, the
string transport for operands and results
([ADR-0004](0004-exact-decimal-arithmetic.md)), and the full error envelope with its code
enumeration ([ADR-0005](0005-error-model-and-status-codes.md)).

The usual failure mode in a two-layer application is drift. The backend renames a field or
adds an error code, the frontend keeps branching on the old one, and nothing catches it
until something breaks at runtime. Hand-written client types are a copy of the contract that
nobody updates.

**The honest difficulty, stated before the decision rather than after it: FastAPI is
code-first by default, and that is the opposite of what is wanted here.** The normal FastAPI
workflow is to write Pydantic models and let the framework derive `/openapi.json` from them.
That produces a generated specification, which is a useful artefact, but it does not make a
project API-first. The specification is downstream of the implementation, so it can never
contradict it, which means it can never catch a mistake either. Describing FastAPI's
generated document as "API-first" would be a claim the architecture does not support.

Being genuinely API-first therefore requires working against the framework's default and
adding a mechanism that can fail.

Decision criteria:

1. One contract that both layers are held to, not two views of it.
2. The contract must be able to fail the build. A contract nothing enforces is a comment.
3. Frontend types must not be a hand-maintained copy.
4. Affordable inside a 2 to 4 hour budget.

## Decision

Adopt an API-first workflow with four moving parts.

**1. `openapi.yaml` is committed at the repository root and authored first**, before either
layer exists. It defines `POST /api/calculations`, the operation enumeration, the operand and
result string types, the success response, and the error envelope with its code
enumeration. It is a source file, edited deliberately, not a build output.

**2. The backend implements the contract.** Pydantic models exist to satisfy `openapi.yaml`,
not to define it. When the two disagree, the contract is right and the code is wrong.

**3. Continuous integration fails when anything drifts from the contract, in two parts.**
`check-generated` regenerates every derived artefact and fails on any `git diff`, so no bespoke
comparison step is needed for those. The document the application serves is compared against the
committed contract by ordinary tests in `test_contract.py`. This is the most important element of
this decision and the only reason the rest of it is true rather than aspirational.

Its limit was measured rather than assumed, by injecting four deliberate drifts. A renamed path, a
changed media type and an omitted title are all caught by the document comparison. **Changing a
status the code returns is not**, because statuses are declared in the route decorator, so the
served document does not move; the behavioural scenarios catch that one. Document comparison
catches shape drift, behaviour catches behavioural drift, and neither substitutes for the
other. Without this gate, "API-first" is a description of intent that the repository
cannot verify; with it, the contract is enforced on every push. Directionally, this inverts
FastAPI's default: the framework still generates a document, but that document is now a
*test subject* compared against the source of truth rather than being the source of truth.

**4. Both layers' wire types are generated from the committed contract**, never hand-written
and never generated from a running server. Which generators, and why the frontend also
validates at runtime, is [ADR-0008](0008-generate-all-wire-types.md).

The consequence for the frontend is worth one sentence: the client cannot construct a
request the contract does not allow, and every error code it branches on comes from the
contract's enumeration, which removes the whole class of front-to-back drift bugs by
construction rather than by discipline.

This reinforces [ADR-0003](0003-single-calculate-endpoint.md). A single endpoint with a
discriminated union is markedly cheaper to hand-author and keep current than seven endpoints
would be, so the API shape chosen there is part of what makes a hand-written contract
affordable here.

## Alternatives considered

- **Code-first, with the specification generated from Pydantic (the FastAPI default).** The
  strongest counter-argument, and the option most defensible on a 2 to 4 hour budget. It
  costs nothing, it is idiomatic FastAPI, and the generated document is genuinely accurate
  as a description of the implementation. It was rejected because it cannot detect a
  mistake: a specification derived from the code agrees with the code by construction, so
  it validates nothing, and the frontend would be generating types from whatever the
  backend happened to do rather than from what was agreed. It is the right choice for a
  single-team service with no external consumers, and the wrong one when the point is to
  demonstrate that a contract is being honoured.
- **Hand-written frontend types.** Simple, no tooling, no generation step. Rejected because
  it is precisely the copy that drifts. Two hand-maintained descriptions of one contract
  will disagree, and the disagreement surfaces at runtime.
- **Generating nothing, and hand-writing both sides against the contract.** Rejected: the
  contract would bind only as far as discipline reached. See
  [ADR-0008](0008-generate-all-wire-types.md).
- **JSON Schema or a hand-written contract in prose.** Rejected: OpenAPI is what FastAPI
  already emits, which is what makes the comparison direct rather than a translation.

## Consequences

### Positive

- One source of truth that both layers are held to, with a mechanism that can fail.
- Front-to-back drift is caught in continuous integration rather than at runtime.
- Frontend types cost nothing to keep current and cannot silently disagree with the backend.
- The contract can be read and reviewed before any implementation exists, which is what
  made it possible to write this documentation layer before the code.

### Negative

- **It works against FastAPI's grain**, which costs setup time and needs explaining to any
  reader who expects the conventional code-first flow. This ADR is that explanation.
- **The drift gates will be irritating**, by design. Any deliberate contract change means
  editing `openapi.yaml` and regenerating, in the same commit. That friction is the feature,
  but it is still friction.
- **Two generated artefacts are committed** (the frontend types), and committed generated
  code always risks going stale. Mitigated by `check-generated`, which regenerates and fails on
  any `git diff`, and which is itself another gate to maintain.
- **Budget cost.** Authoring the contract by hand, wiring two checks, and configuring
  generation is real time on a 2 to 4 hour exercise, spent on process rather than features.

### Neutral

- The backend still serves FastAPI's generated `/openapi.json` and interactive
  documentation. That output is now a comparison target, not the contract.
- If the contract and the implementation disagree, the resolution rule is fixed: the
  contract wins, and the code changes.
