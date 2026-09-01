---
summary: The Sezzle take-home brief asks for a React frontend and a backend microservice implementing four arithmetic operations, graded on correctness, clarity, maintainability, tests, and documentation, within a 2 to 4 hour budget.
tags: [assignment, requirements, source]
updated: 2026-09-01
---

# Source: Take-Home Assignment Brief

**Raw file**: [`../raw/2026-08-27-assignment-brief.md`](../raw/2026-08-27-assignment-brief.md)
**Received**: 2026-08-27 (Thursday)
**Deadline**: 2026-09-03 (Thursday)
**Role**: Software Engineer II with Accounting Experience (Brazil)

## Summary

Build a full-stack calculator: a React frontend consuming a backend Representational State
Transfer (REST) Application Programming Interface (API). Four required operations
(addition, subtraction, multiplication, division) with three optional ones
(exponentiation, square root, percentage). The brief weights process over feature count:
it explicitly says to prioritise correctness, clarity, and maintainability over extra
features, and caps the effort at roughly 2 to 4 hours.

## Key takeaways

1. **Documentation is graded, not incidental.** The README is named in the deliverables
   list with four mandated contents: setup instructions, how to run each layer, examples
   of API calls, and design decisions or assumptions. This drives the README structure in
   [`../../README.md`](../../README.md).
2. **Prompts are an explicit deliverable.** "Share any prompts that you used in your work"
   is a stated instruction, which is why [`../13-prompt-record.md`](../13-prompt-record.md) exists as a
   first-class file rather than an afterthought.
3. **Go is "preferred", not required.** The exact wording is a preference. That single word
   is what makes a reasoned departure defensible, and it is the hinge of
   [ADR-0002](../decisions/0002-python-fastapi-instead-of-go.md).
4. **Edge cases are named in the brief.** "Division by zero, invalid data" appears in the
   functional requirements, so the error model is graded surface area, not polish. See
   [ADR-0005](../decisions/0005-error-model-and-status-codes.md).
5. **The role is accounting-flavoured.** The job title carries "with Accounting
   Experience". A calculator that renders `0.1 + 0.2` as `0.30000000000000004` would be a
   pointed failure in that context, which is what makes the numeric strategy load-bearing.
   See [ADR-0004](../decisions/0004-exact-decimal-arithmetic.md).

## Deliverables checklist

| Deliverable | Where it is satisfied |
|---|---|
| Git repository with frontend and backend code | Repository root |
| README: setup instructions | [`README.md`](../../README.md) § Setup |
| README: how to run frontend and backend | [`README.md`](../../README.md) § Running |
| README: examples of API calls | [`README.md`](../../README.md) § API usage |
| README: design decisions and assumptions | [`README.md`](../../README.md) § Design decisions, plus [`../decisions/`](../decisions/) |
| Unit tests, both layers | [`README.md`](../../README.md) § Tests and coverage |
| Coverage report | [`README.md`](../../README.md) § Tests and coverage |
| Dockerfile to run both together (optional) | [`architecture.md`](../architecture.md) § 7 |
| Prompts used | [`13-prompt-record.md`](../13-prompt-record.md) |

## Open questions and ambiguities

Gaps the brief leaves open. Most have since been decided by the author and are stated as
decisions; only the last remains an assumption
([`../architecture.md`](../architecture.md) § 11.3).

- **"Percentage" is undefined.** It could mean the unary `a / 100`, the binary "`a` percent of
  `b`", or the keypad behaviour where `%` is context-sensitive to the pending operation.
  **Decided**: the binary form, `percent(a, b) = a / 100 * b`.
- **No precision or rounding requirement is given.** Silence plus an accounting-flavoured role
  was read as a reason to choose deliberately rather than to ignore the question. **Decided**:
  full `decimal` precision end to end, with rounding to two decimal places at display time
  only, never in the contract.
- **No operand bound is given.** **Decided**: operands are bounded and the contract declares
  the bound.
- **No behaviour is given for a negative base with a fractional exponent.** **Decided**: a
  domain error, since the real-valued result does not exist.
- **"Microservice" is used loosely.** The brief describes a single backend service. **Still an
  assumption**, and the only one left: read as "a separate backend process the frontend calls
  over Hypertext Transfer Protocol (HTTP)", not as a mandate for multiple services.
