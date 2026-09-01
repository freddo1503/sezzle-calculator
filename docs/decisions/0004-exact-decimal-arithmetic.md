---
number: 4
title: Exact decimal arithmetic with decimal.Decimal, transported as JSON strings
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: Arithmetic uses Python's decimal.Decimal rather than IEEE-754 binary floats, and operands and results cross the wire as JSON strings so the frontend cannot silently reintroduce binary rounding error.
tags: [numerics, accounting, api, decimal]
updated: 2026-09-01
---

# ADR-0004: Exact decimal arithmetic with `decimal.Decimal`, transported as JSON strings

## Context

The assignment specifies no numeric type, no precision, and no rounding behaviour
([source](../sources/assignment-brief.md)). The silence is the interesting part.

The role is "Software Engineer II **with Accounting Experience**". In that context the
canonical failure is well known and instantly recognisable:

```
0.1 + 0.2 = 0.30000000000000004
```

This is not a bug. It is the correct IEEE-754 binary floating-point result: neither `0.1`
nor `0.2` has an exact representation in base 2, so the sum carries representation error
that surfaces at the seventeenth significant digit. Any calculator built on `float64` (or
on JavaScript `number`, which is the same type) will display it unless something is done
deliberately.

A submission for an accounting-adjacent role that displays that string has answered a
question the evaluator was probably asking on purpose. Silence in the brief is read here as
an invitation to choose deliberately and justify it, not as permission to skip the
question.

Second force, easy to miss: **the choice is not only about the backend's arithmetic, it is
about the whole round trip.** Exactness computed on the server can be destroyed on the
client. See the transport argument below.

Decision criteria:

1. Decimal values a human types must behave the way that human expects.
2. Exactness must survive the journey to the screen, not just the computation.
3. Where exactness is mathematically impossible (division producing a repeating expansion,
   irrational roots), the behaviour must be defined, documented, and predictable.
4. No unnecessary dependency.

## Decision

Perform all arithmetic with Python's standard-library `decimal.Decimal`, and transport
operands and results as **JSON strings** rather than JSON numbers.

### Arithmetic

`decimal` implements base-10 arithmetic in which addition, subtraction, and multiplication
are exact within the context precision. `Decimal("0.1") + Decimal("0.2")` is exactly
`Decimal("0.3")`.

Context configuration, both of which are the module defaults and are adopted explicitly
rather than inherited implicitly:

- **Precision: 28 significant digits.**
- **Rounding: `ROUND_HALF_EVEN`** (banker's rounding). Ties round to the nearest even
  digit, which avoids the systematic upward bias of always rounding halves away from zero.
  This is the conventional choice in financial contexts and the reason it is the module
  default.

Operations that cannot be exact are correctly rounded to the context precision:

- **Division** with a repeating expansion, for example `1 / 3`, yields 28 significant
  digits. This is a real limit and is documented rather than hidden.
- **Square root** via `Decimal.sqrt()`, correctly rounded to context precision.
- **Exponentiation** is exact only when the exponent is integral and the result fits the
  precision. A negative base requires an integral exponent; a negative base with a
  fractional exponent is a domain error, since the real-valued result does not exist
  (handled per [ADR-0005](0005-error-model-and-status-codes.md)).

### Rounding is display only, never in the contract

The API returns the exact value. The frontend rounds to two decimal places for presentation
alone, and nothing rounded ever re-enters a calculation.

Rounding inside the contract was considered and rejected: at two decimal places it would make
`1 / 8` return `0.12`, `sqrt(2)` return `1.41`, and `1 / 3` followed by times three return
`0.99` rather than `1`. Each of those is a correct rounding of a value the caller never asked
to have rounded, and the last one is the tell: a calculator that rounds inside the contract
cannot chain operations without drifting.

The consequence for the client is a boundary that must not leak: the keypad's input state
machine chains on the exact value returned, never on the string displayed. Computation owns
the value, presentation owns its appearance.

### Transport, and why it is the load-bearing half

Operands and results cross the wire as JSON strings:

```json
{ "operation": "add", "operands": ["0.1", "0.2"] }
{ "result": "0.3" }
```

The reason is specific and decisive. The JSON grammar itself places no limit on numeric
precision, but essentially every JavaScript client parses JSON numbers into `number`, which
is an IEEE-754 double. So a response of

```json
{ "result": 0.3 }
```

is re-parsed by the browser into a binary double, and the exactness the backend just took
care to preserve is destroyed at the last hop, by the client, silently. Returning a string
and rendering it verbatim is what makes the guarantee reach the screen.

The corresponding rule on the frontend: **never coerce the result to `Number` for
display.** Parsing to a number for formatting would reintroduce precisely the error this
decision exists to prevent. The result string is rendered as received.

Inputs are strings for the symmetrical reason: a request body containing `0.1` as a JSON
number has already been through a client-side double before it is serialised.

## Alternatives considered

- **IEEE-754 binary floats** (`float` in Python, `float64` in Go, `number` in JavaScript).
  Rejected. Fast, universal, zero ceremony, and correct for scientific work. But it
  displays `0.30000000000000004` for the single most recognisable test a reviewer of an
  accounting-flavoured submission could type. Choosing it would mean either not having
  considered the question or having answered it wrongly.
- **Integer minor units (store everything in cents).** Rejected. This is the right answer
  for a money-typed domain, where every value has a currency and a fixed scale of two. It
  is wrong here: this is a general-purpose calculator with no currency in its domain, and
  the operand `2.5` is not "250 cents". Square root and exponentiation have no sensible
  meaning under fixed-scale integers.
- **Rational arithmetic (`fractions.Fraction`).** Rejected, though it is the only option
  that makes `1 / 3` genuinely exact. Denominators grow without bound across chained
  operations, square root leaves the rationals entirely, and displaying `1/3` to a
  calculator user requires converting to a decimal expansion anyway, which reintroduces the
  same rounding decision one layer later.
- **A decimal library on top of a Go or Node backend.** Rejected as part of
  [ADR-0002](0002-python-fastapi-instead-of-go.md). The standard-library availability of
  `decimal` is one of the inputs to that decision.

## Consequences

### Positive

- `0.1 + 0.2` returns exactly `0.3`. The behaviour matches what a person entering decimal
  digits expects, which is the whole point of a calculator.
- Exactness survives to the rendered pixel, because the string transport prevents the
  client from undoing it.
- No third-party dependency: `decimal` is in the standard library, which is the
  standard-library-first rule in
  [`.claude/rules/principles.md`](../../.claude/rules/principles.md) applied where it matters
  most here. A third-party fixed-point package would have to earn its place against a module
  that already does correctly rounded base-10 arithmetic.
- Rounding behaviour is stated (`ROUND_HALF_EVEN` at 28 digits) rather than emergent, so it
  is testable and reviewable.
- It gives a clean, high-value test suite: `0.1 + 0.2 == 0.3` is a one-line test that
  demonstrates the property directly.

### Negative

- **String operands are unconventional** and look odd to a reader who has not read this
  ADR. Cross-referenced from the README to reduce that surprise.
- **Slower than binary floats**, by roughly an order of magnitude. Entirely irrelevant at
  this scale, noted for completeness.
- **The frontend carries a discipline it must not break**: never `Number(result)`. That is
  an invariant enforced by review and by test, not by the type system.
- **Exactness has a boundary that must be explained.** `1 / 3` is 28 digits, not a third,
  and `sqrt(2)` is irrational. The guarantee is exact decimal arithmetic where it is
  mathematically available, correctly rounded where it is not. Overstating it would be
  worse than the limit itself.

### Neutral

- Precision and rounding are set explicitly at 28 and `ROUND_HALF_EVEN` even though these
  are the module defaults, so the values are visible in the code and in this document
  rather than inherited silently.
- Operand magnitude is bounded on input, so that expressions like `9E+999999 ** 9E+999999`
  fail as a validated domain error instead of consuming unbounded time and memory. The
  resulting error maps per [ADR-0005](0005-error-model-and-status-codes.md).

## References

- Python `decimal` module: https://docs.python.org/3/library/decimal.html
- IEEE 754 floating point, background: https://docs.python.org/3/tutorial/floatingpoint.html
- General Decimal Arithmetic specification: https://speleotrove.com/decimal/
