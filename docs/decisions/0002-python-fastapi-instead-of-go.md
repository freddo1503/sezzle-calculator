---
number: 2
title: Python and FastAPI for the backend instead of the preferred Go
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: The backend is Python with FastAPI rather than the assignment's preferred Go, trading a demonstration of Go proficiency for higher quality on the axes the assignment actually grades within a 2 to 4 hour budget.
tags: [backend, stack, deviation]
updated: 2026-09-01
---

# ADR-0002: Python and FastAPI for the backend instead of the preferred Go

## Context

The assignment states, under Constraints: "Frontend: React (TypeScript preferred).
Backend: Go is preferred" ([source](../sources/assignment-brief.md)).

It also states: "Spend ~2-4 hours. Prioritize correctness, clarity, and maintainability
over extra features."

These two instructions pull against each other for this particular author. The relevant
forces:

- **The wording is "preferred", not "required".** The frontend constraint names React
  flatly and marks TypeScript as preferred; the backend names Go as preferred. Read
  strictly, React is the only hard technology constraint in the brief. A preference invites
  a reasoned departure. It does not invite an unexplained one.
- **Language proficiency is not uniform.** Python is the author's strongest language. Go is
  not. Over a 2 to 4 hour window there is no time to converge: the first hours in a weaker
  language are spent on syntax, idiom, tooling, and test ergonomics rather than on the
  qualities being graded.
- **The graded axes are explicit.** Correctness, clarity, maintainability, tests,
  documentation. Notably, "demonstrates Go" is not among them.
- **The role is accounting-flavoured**, and exact decimal arithmetic is therefore
  load-bearing (see [ADR-0004](0004-exact-decimal-arithmetic.md)). The two languages differ
  in what they offer here out of the box.

Decision criteria, in priority order:

1. Maximise quality on the stated grading axes within the budget.
2. Make the numeric strategy in ADR-0004 straightforward rather than incidental.
3. Keep the deviation visible and argued, never silent.

## Decision

Build the backend in Python with FastAPI, dependencies and virtual environment managed by
`uv`, and argue the departure openly in this ADR and in the README's design-decisions
section.

The reasoning:

**Working in the strongest available language is the highest-leverage way to satisfy the
stated priorities.** The brief asks for correctness, clarity, and maintainability inside a
fixed budget. Those are exactly the properties that degrade first when an engineer works
in an unfamiliar language under time pressure. Choosing Go would optimise for matching a
stated preference while actively degrading the four things the brief says it is grading.

**Exact decimal arithmetic is in the Python standard library.** `decimal.Decimal` provides
correctly rounded base-10 arithmetic with a configurable context, with no third-party
dependency. Go's standard library offers `math/big` (arbitrary-precision integers,
rationals, and binary floats) but no fixed-point decimal type, so the equivalent in Go
means either a third-party package such as `shopspring/decimal`, or `big.Rat` with its own
display problems. For a submission where the numeric choice is the substantive engineering
argument (ADR-0004), having it be a standard-library one-liner is a real advantage.

**FastAPI collapses three graded requirements into framework behaviour.** Request
validation, JSON serialisation, and API documentation are handled by Pydantic models and
generated OpenAPI output. The brief asks separately for input validation, JSON responses,
and API usage documentation. Getting them from declared types rather than hand-written
code leaves more of the budget for tests and for the error model.

**The deviation is disclosed prominently rather than hidden.** It is named in the README's
design-decisions section, near the top, not buried. The intent is that an evaluator meets
the reasoning before they meet the surprise.

## Alternatives considered

- **Go with the standard library `net/http`, or a router such as `chi` or Gin.** Rejected
  on budget, not on merit. This is the option that matches the brief exactly, and it is the
  strongest argument against this ADR. Under a longer budget it would win, because
  conforming to a stated preference has real value and Go is a good fit for a small
  arithmetic service. It loses here only because the delivered artefact would be
  measurably weaker on the graded axes within 2 to 4 hours, and because decimal arithmetic
  would need a dependency or a workaround.
- **TypeScript on both ends (Node with Express or Fastify).** A single language across the
  stack, shared types between frontend and backend, and a plausible reading of "React
  preferred" extended to the server. Rejected because JavaScript numbers are IEEE-754
  doubles, so exact decimal arithmetic requires a library and careful discipline at every
  boundary. That works against ADR-0004 in a role where the numeric behaviour is the point.
  It also departs from the stated preference just as much as Python does, without Python's
  compensating advantage.
- **Go for the service with the arithmetic core in another language.** Rejected outright as
  disproportionate: two runtimes and an interop boundary for a calculator is exactly the
  over-engineering the brief warns against.

## Consequences

### Positive

- The delivered backend is idiomatic and well tested, because it is written in a language
  the author uses fluently. The graded qualities benefit directly.
- Exact decimal arithmetic comes from the standard library, keeping ADR-0004 simple.
- Input validation, JSON responses, and generated API documentation follow from Pydantic
  type declarations rather than hand-written plumbing.
- The submission demonstrates something the Go path would not: reading a constraint
  precisely, weighing a trade-off, and defending it in writing. For a Software Engineer II
  role that is a relevant signal in its own right.

### Negative

These are the real costs, stated plainly rather than minimised.

- **The submission provides no evidence of Go proficiency.** If Go competence is something
  this hiring process needs to assess, this artefact cannot do it, and no argument in this
  file changes that. That is the central risk being accepted.
- **A stated preference presumably reflects the team's actual stack.** If so, "can work in
  our stack" is a real hiring question that goes unanswered here.
- **The deviation can be read uncharitably**, as not reading the brief, or as avoiding
  discomfort. The mitigation is that it is disclosed and argued rather than passed over in
  silence, but a reviewer is entitled to weigh it against the submission.
- **Reviewer attention is finite.** Some of it will go to evaluating this decision instead
  of the code.

### Neutral

- Python and Go are both entirely capable of this service. Nothing in the assignment's
  functional requirements is easier or harder in either.
- Because the API contract is language-agnostic (see
  [ADR-0003](0003-single-calculate-endpoint.md)), the backend could be reimplemented in Go
  behind the same contract without touching the frontend. The tests describe the contract,
  not the implementation.
- **[ADR-0008](0008-generate-all-wire-types.md) sharpens this.** With every wire type on both
  sides generated from `openapi.yaml`, a Go port regenerates its own types from that same file
  and reimplements the arithmetic engine; the contract, the entire frontend, and the contract
  tests are untouched. This does not make the negative consequence above any less true, and it
  is not offered as a softening of it: the submission still shows no Go. What changes is the
  shape of the risk. The language choice is a reversible decision scoped to one layer rather
  than a bet on the whole submission, and those are materially different things.
