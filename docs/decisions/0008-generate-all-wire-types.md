---
number: 8
title: Generate every wire type from the contract, on both sides, and validate at runtime
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: No type describing the wire format is hand-written on either side; backend Pydantic models and frontend types, client and Zod schemas are all generated from openapi.yaml, with runtime validation at the frontend boundary making the contract enforceable rather than merely declared.
tags: [api, contract, codegen, zod, validation]
updated: 2026-09-01
---

# ADR-0008: Generate every wire type from the contract, on both sides, and validate at runtime

## Context

[ADR-0007](0007-api-first-openapi-contract.md) established `openapi.yaml` as the source of
truth. That settles *authority*. It does not settle *reach*: a contract nothing derives from
is still a document that two hand-written implementations can quietly disagree with.

Every hand-written type describing the wire format is a second copy of knowledge that already
lives in the contract, and copies drift. This is the specific failure the design exists to
prevent, and it is the one case where the repository's DRY rule is settled and not
re-litigated (see [`.claude/rules/principles.md`](../../.claude/rules/principles.md)).

There is also a gap that generation alone does not close, and it is easy to miss. TypeScript
types are erased at build time. They constrain what the frontend *writes*, and check nothing
about what it *receives*.

## Decision

**No type describing the wire format is hand-written anywhere.**

**Backend.** Pydantic v2 models are generated from `openapi.yaml` with
[`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator), which
supports `oneOf` discriminated unions, exactly the shape
[ADR-0003](0003-single-calculate-endpoint.md)'s single endpoint requires.

**Frontend.** [Orval](https://orval.dev/) generates three artefacts from the same file: the
TypeScript types, a typed Hypertext Transfer Protocol (HTTP) client, and Zod schemas.
Configuration lives in `orval.config.ts` at the repository root using `defineConfig`, with
the Zod output given a distinct `fileExtension` (`.zod.ts`) so client and schema files do not
collide.

Generated output on both sides is committed, so a reader sees the types without running a
generator, and continuous integration regenerates both and fails if either is stale.

### Why Zod, and not types alone

This is the part that earns the decision rather than merely recording a tool.

Generated TypeScript types are erased at build time and enforce nothing at runtime. If the
backend ever violates the contract, it hands the frontend a shape TypeScript sincerely
believes is correct. The program continues, and the failure surfaces later and somewhere else,
as a rendering bug or an undefined field, far from its cause. That is the most expensive kind
of bug to diagnose.

Orval's generated Zod schemas close the hole: the frontend validates the actual response
against the contract at the boundary, and fails loudly and locally at the moment the contract
is broken.

The contract is therefore enforced at **four** points, not two:

| # | Point | Catches |
|---|---|---|
| 1 | Backend generated Pydantic models | An implementation that cannot express the contract |
| 2 | Continuous integration, `check-generated` plus the contract tests | A contract and an implementation that have diverged |
| 3 | Frontend compile-time types | A client that tries to send or read the wrong shape |
| 4 | Frontend runtime Zod validation | A backend that violates the contract in production |

Points 1 to 3 are checked against a generator. Point 4 is the only one checked against
reality.

### The consequence for the language choice

The author's rationale, in his terms: generating both sides from one contract makes the
implementation language an exchangeable detail.

Drawing that out, because it is the strongest available answer to the objection that this
project should have been written in Go: a Go port would regenerate its own types from the
same `openapi.yaml` and reimplement the arithmetic engine. The contract, the entire frontend,
and the contract tests would be untouched.

This does not make [ADR-0002](0002-python-fastapi-instead-of-go.md)'s stated cost false. That
submission still provides no evidence of Go proficiency, and nothing here changes it. What it
does change is the *shape* of the risk: the language choice stops being a bet and becomes a
reversible decision, with the reversal scoped to one layer behind a contract that already
exists. Those are materially different things, and both are true at once.

## Alternatives considered

- **`openapi-typescript` plus `openapi-fetch` for the frontend.** The option previously
  chosen, and a good one: runtime-free types and a 6 kB typed client with virtually no
  runtime. Rejected because "no runtime" is precisely the limitation. It gives points 1 to 3
  above and cannot give point 4. For a submission whose whole argument is that the contract is
  authoritative, the ability to detect a violated contract is worth the bundle it costs.
- **Hand-written types on either side.** Rejected outright: the copy that drifts, and the
  failure this design exists to prevent.
- **Generated types with hand-written runtime validation.** All of Zod's cost and none of its
  guarantee of matching the contract, since a hand-written validator is another copy that
  drifts.
- **A heavier full-client generator.** Rejected as disproportionate for one endpoint: more
  generated surface, an opinionated HTTP layer, and output that is awkward to read in review.

## Consequences

### Positive

- One authoritative statement of the wire format, with every downstream artefact derived.
- **It is what makes the "no business rules in the frontend" constraint achievable**
  ([`architecture.md`](../architecture.md) § 2). The frontend can validate input without holding
  any rule of its own, because the rules arrive as generated Zod schemas rather than as
  hand-written checks. The constraint reinforces this decision; this decision supplies the
  mechanism.
- A violated contract fails at the boundary, loudly and close to its cause.
- The implementation language becomes a replaceable layer rather than a foundation.
- Adding an operation means editing the contract and regenerating, not editing types in two
  languages.

### Negative

- **Zod schemas are shipped code**: bundle weight plus a validation pass on every response,
  paid to catch a class of bug a correct backend never produces. Accepted knowingly, because
  the alternative is that the central claim of this submission is never tested against
  anything but a generator.
- **Two generators to configure and keep working**, on a 2 to 4 hour budget.
- **Committed generated code can go stale.** Mitigated by `check-generated`, which regenerates
  everything and fails on any `git diff`.
- **Generated code is not idiomatic hand-written code**, and a reviewer skimming it may read
  it as such. It is committed anyway, because being able to read the types without running a
  generator is worth more.

### Neutral

- Generated artefacts are never edited by hand. A wanted change is made in `openapi.yaml`.
