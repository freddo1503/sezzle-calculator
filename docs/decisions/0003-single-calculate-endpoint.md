---
number: 3
title: A single generic POST /api/calculations endpoint rather than one endpoint per operation
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: The API exposes one POST /api/calculations endpoint taking the operation as a discriminated field, giving a uniform error model and a single validation surface, at the cost of less self-describing URLs.
tags: [api, rest, design]
updated: 2026-09-01
---

# ADR-0003: A single generic `POST /api/calculations` endpoint rather than one endpoint per operation

## Context

The assignment says the backend should "expose endpoints for calculator operations"
([source](../sources/assignment-brief.md)). Plural, and otherwise unspecified. Both shapes
below satisfy it literally.

The operation set is four required (addition, subtraction, multiplication, division) plus
three optional (exponentiation, square root, percentage). The set is open: an evaluator
may reasonably wonder how a new operation would be added.

The operations are not uniform in arity. Square root is unary; the rest are binary. Any
design has to handle that.

A calculation is also not a resource. Nothing is stored, nothing is retrieved by
identifier, and no state changes. This is a remote procedure call wearing HTTP clothes,
which means textbook Representational State Transfer (REST) resource modelling gives less
guidance here than usual.

Decision criteria:

1. One uniform error contract, because the error model is graded surface area
   (the brief names division by zero and invalid data explicitly).
2. Minimum duplicated validation logic.
3. Adding an operation should be a small, safe change.
4. The frontend should need one typed client function, not seven.

## Decision

Expose a single endpoint:

```
POST /api/calculations
Content-Type: application/vnd.api+json

{ "data": { "type": "calculations",
            "attributes": { "operation": "divide", "operands": ["1", "3"] } } }
```

The `operation` field is a closed enumeration. The request body is modelled as a
discriminated union keyed on `operation`, so arity and per-operation rules are enforced by
the schema rather than by hand-written branching: `sqrt` accepts exactly one operand, the
binary operations accept exactly two.

Operands are transported as JSON strings, not JSON numbers. That is a consequence of
[ADR-0004](0004-exact-decimal-arithmetic.md) and is argued there.

The reasoning:

**A uniform error contract falls out of a single entry point.** Every failure, whether
schema-level or arithmetic, leaves through one handler and one response shape
([ADR-0005](0005-error-model-and-status-codes.md)). With seven endpoints, keeping error
responses identical becomes a convention that has to be maintained and tested per route.
Here it is structural.

**Validation is written once.** Operand parsing, magnitude bounds, and arity are declared
in one place. Per-operation endpoints would either duplicate that or need a shared helper
that recreates this design with extra routing.

**Adding an operation becomes a data change.** A new enumeration member and a new entry in
the operation registry, with no new route, no new handler, and no new error plumbing. The
brief grades maintainability, and this is the axis where the difference is visible.

**The frontend gets one client function.** `calculate(operation, operands)` typed once,
against one response type.

## Alternatives considered

- **One endpoint per operation** (`POST /add`, `POST /divide`, `POST /sqrt`). Rejected,
  and it is a genuinely close call. It gives self-describing URLs, a named operation per
  entry in the generated OpenAPI document, natural per-operation request schemas, and it
  reads as more conventional HTTP. It loses on the criteria above: seven copies of the
  error contract to keep consistent, validation logic duplicated or indirected, and a new
  route plus handler plus tests for every new operation. For an operation set this
  homogeneous, the repetition buys presentation rather than capability.
- **`GET /api/calculations?operation=add&a=1&b=2`.** Rejected. Calculations are safe and
  idempotent, so GET is semantically defensible and would even be cacheable. But operands
  in a query string invite type coercion at every hop (proxies, logs, browser history), the
  URL-encoding of decimal strings and signs is fiddly, and exact-decimal transport
  (ADR-0004) is harder to guarantee. Correctness beats cacheability for an operation whose
  cost is nanoseconds.
- **A single endpoint taking an expression string** (`{"expression": "1 + 2 * 3"}`).
  Rejected as scope creep. It requires a tokeniser, a parser, and precedence handling, none
  of which the brief asks for, against an explicit instruction to prioritise correctness
  over extra features.

## Consequences

### Positive

- One error contract, structurally guaranteed rather than maintained by convention.
- One validation surface, therefore one place to test it thoroughly.
- New operations are additive and low-risk.
- The frontend client is a single function against a single response type.

### Negative

- **URLs are less self-describing.** `POST /api/calculations` conveys nothing about what is being
  computed; the intent is in the body. A reader of an access log sees only that a
  calculation happened.
- **The generated OpenAPI document shows one operation, not seven.** The discriminated
  union does keep the per-operation request schemas visible and named in the schema
  section, so the information is present, but it is less prominent than seven named
  endpoints would be.
- **It is the less conventional choice**, so it needs this justification. An evaluator
  expecting resource-per-operation may read it as unusual before reading the rationale.

### Neutral

- **The document format is JSON:API** ([ADR-0010](0010-jsonapi-document-format.md)), so the
  discriminated union now lives at `data.attributes.operation` and the path is the plural
  `calculations`. The argument below is unaffected: still one endpoint, still one union, still
  one validation surface.
- **Reinforced by [ADR-0007](0007-api-first-openapi-contract.md)**: a single endpoint with a
  discriminated union is markedly cheaper to hand-author and keep current as an OpenAPI
  contract than seven endpoints would be.
- The endpoint is a POST despite being side-effect free. This is deliberate: a request body
  is the right place for typed operands (see the GET alternative above), and POST is the
  conventional method for a request body.
- **Optional, not part of this decision**: a `GET /operations` endpoint returning the
  supported operation set with each one's arity would make the API self-describing and let
  the frontend build its keypad from the backend. It is noted here as a natural extension
  and deliberately left out of scope, since the brief asks for correctness over extra
  features.
