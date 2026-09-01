---
number: 5
title: One JSON error envelope, 422 for every rejected calculation, machine-readable codes
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
superseded_in_part_by: 10
summary: Every failure returns one error document carrying a stable machine-readable code, with 400 for unparseable requests, 422 for anything well-formed that cannot be computed, and 500 reserved strictly for genuine bugs. The envelope's shape was later replaced by JSON:API in ADR-0010; the status-code reasoning stands.
tags: [api, errors, http, validation]
updated: 2026-09-01
---

# ADR-0005: One JSON error envelope, 422 for every rejected calculation, machine-readable codes

## Context

The brief names error handling twice: the backend must "validate input and handle edge
cases (division by zero, invalid data)", and the frontend must do "input validation and
error handling" ([source](../sources/assignment-brief.md)). Edge cases are called out by
name, so this is graded surface area rather than polish.

The failures that actually occur fall into two groups that are easy to conflate:

1. **Schema failures.** Body is not JSON, `operation` is not a known value, `operands` is
   missing, an operand is not a parseable decimal, wrong number of operands for the
   operation.
2. **Domain failures.** The request is perfectly well-formed and still cannot be computed:
   division by zero, square root of a negative number, a negative base raised to a
   fractional exponent, results that overflow the configured decimal context.

Two forces shape the response format:

- **FastAPI already has an opinion.** Pydantic validation failures produce HTTP 422 with a
  `detail` array of error objects. Domain failures raised in application code would
  naturally produce something else. Left alone, the API would ship two different error
  shapes, and the frontend would need to handle both.
- **The frontend has to branch on the failure.** "Cannot divide by zero" needs a different
  message from "enter a valid number". Branching on human-readable English prose is
  fragile and untranslatable, so the distinction has to be machine-readable.

Decision criteria:

1. Exactly one error shape on the wire, whatever the cause.
2. The frontend branches on a stable identifier, never on prose.
3. Status codes carry honest semantics.
4. A 500 must always mean "we have a bug", so that it stays a usable alerting signal.

## Decision

### One envelope

> **Superseded in shape by [ADR-0010](0010-jsonapi-document-format.md), not in reasoning.**
> This record originally specified a house envelope,
> `{"error": {"code", "message", "details"}}`, with an invented `operand_index` convention for
> naming the offending operand. JSON:API replaced that shape. Everything else in this record
> stands: the status-code argument below is untouched, and so is the rule that clients branch on
> `code` and never on human-readable text. The superseded shape is described here rather than
> deleted, because the reasoning that produced it is what JSON:API then satisfied better.

Every non-2xx response, without exception, is a JSON:API error document:

```json
{
  "errors": [
    {
      "status": "422",
      "code": "DIVISION_BY_ZERO",
      "title": "Division by zero",
      "detail": "Division by zero is undefined.",
      "source": { "pointer": "/data/attributes/operands/1" }
    }
  ]
}
```

`code` is a stable enumeration for programmatic branching, and it is now a member the
specification defines rather than one we invented. `title` and `detail` are human-readable and
owned by the server, so the client renders them as they arrive and holds no string table of its
own. `source.pointer` is an RFC 6901 JSON Pointer naming the offending value exactly, which
replaces the `operand_index` convention this record used to define.

Uniformity is achieved by installing an exception handler for FastAPI's
`RequestValidationError` that translates Pydantic's native `detail` array into this shape.
Without that handler the API would emit two shapes; with it, the single entry point of
[ADR-0003](0003-single-calculate-endpoint.md) means every failure passes through one funnel.
JSON:API additionally forbids `data` and `errors` from coexisting, so the mutual exclusion this
record wanted is now guaranteed by the format rather than by our own discipline.

### Status codes

| Status | When | Example codes |
|---|---|---|
| `400 Bad Request` | The request body could not be parsed at all | `MALFORMED_REQUEST` |
| `415 Unsupported Media Type` | The request did not use `application/vnd.api+json`. Required by JSON:API | `UNSUPPORTED_MEDIA_TYPE` |
| `422 Unprocessable Content` | The request parsed, but cannot be processed: schema violations **and** domain failures | `VALIDATION_ERROR`, `UNKNOWN_OPERATION`, `INVALID_OPERAND`, `WRONG_OPERAND_COUNT`, `DIVISION_BY_ZERO`, `NEGATIVE_SQRT`, `UNDEFINED_RESULT`, `OPERAND_OUT_OF_RANGE`, `RESULT_OVERFLOW` |
| `500 Internal Server Error` | Never deliberately. An unhandled exception means a bug | `INTERNAL_ERROR` |

**Why division by zero is 422 and not 400.** This is the one status choice that deserves
its argument written down. RFC 9110 §15.5.21 defines 422 Unprocessable Content as the
server having understood the content type and found the syntax correct, but being unable to
process the contained instructions. That is exactly the situation: `{"operation": "divide",
"operands": ["1", "0"]}` is valid JSON, valid against the schema, and semantically
meaningful. Nothing about it is a *bad request*. It is a well-formed instruction that
cannot be carried out. 400, by contrast, means the server could not understand the request
at all, which would be a misdescription here.

**Why schema and domain failures share 422.** They are genuinely the same class under the
RFC's definition: understood, but not processable. Splitting them across 400 and 422 would
mean using 400 for requests the server understood perfectly, which contradicts its
definition. The distinction the frontend actually needs (which field to highlight, which
message to show) is carried by `code`, which is more precise than a status code could be
anyway.

**Why 500 is never used deliberately.** Reserving it means that a 500 in the logs is
unambiguously a defect. Every anticipated failure is enumerated above and handled. A
division by zero returning 500 would be a category error: the server did not fail, the
calculation is undefined.

### Frontend behaviour

The frontend renders the response's `title` and `detail` for the user and branches on `code` only for
behaviour, such as which input to highlight when `details` names a field. It holds no map from
code to text: the backend owns the wording, because a string table in the frontend would be a
rule living in the wrong layer. A new backend code therefore displays correctly without any
frontend change.

## Alternatives considered

- **400 for domain failures, 422 for schema failures.** The most common convention in the
  wild, and rejected on the RFC definitions above: a division by zero is not a request the
  server failed to understand. The split is also arbitrary in practice, since the frontend
  branches on `code` regardless.
- **200 OK with an error field in the body.** Rejected. It defeats HTTP status semantics,
  breaks every generic client, monitor, and proxy, and forces every consumer to inspect the
  body to know whether the call worked.
- **JSON:API error objects.** Not considered at the time and adopted later in
  [ADR-0010](0010-jsonapi-document-format.md), which is the outcome this record's reasoning was
  reaching for: one shape, a machine-readable code, and a standard way to point at the offending
  field.
- **RFC 9457 Problem Details for HTTP APIs** (`application/problem+json`, with `type`,
  `title`, `status`, `detail`, `instance`). Genuinely tempting: it is the standardised
  answer to this exact problem, and would be the right call on a production service with
  multiple consumers. Rejected here as disproportionate. It brings a content type, a `type`
  Uniform Resource Identifier registry, and vocabulary for one endpoint with one consumer.
  The envelope above carries the same information the frontend needs with materially less
  ceremony. Recorded so that the standard is visibly considered rather than unknown.
- **Leaving FastAPI's native validation shape as-is for schema errors.** Free, zero code.
  Rejected because it ships two error shapes, pushing the cost of the inconsistency onto
  the frontend and onto every test.

## Consequences

### Positive

- One response shape means one parser, one TypeScript type, and one error path in the
  frontend.
- `code` gives stable programmatic branching and makes messages freely rewritable and
  translatable.
- Status codes stay honest, so 500 remains a meaningful alerting signal.
- The error contract is small enough to test exhaustively: one test per code, which is what
  "unit tests covering key functionality" should mean for an API whose brief names edge
  cases explicitly.

### Negative

- **Writing the `RequestValidationError` handler is code that would otherwise not exist.**
  The uniformity is bought, not free.
- **Sharing 422 across schema and domain failures departs from common practice.** A
  reviewer expecting 400 for division by zero will notice, which is why the argument is
  written out above.
- **The code enumeration is a compatibility surface.** Once the frontend branches on
  `DIVISION_BY_ZERO`, renaming it is a breaking change.

### Neutral

- Pydantic's original validation detail is not discarded, it is mapped into `details` so
  the diagnostic information survives the translation.
- The code list is deliberately finite and closed. A failure that does not fit an existing
  code is a bug until a code is added for it.

## References

- RFC 9110 §15.5.21, 422 Unprocessable Content: https://www.rfc-editor.org/rfc/rfc9110.html#name-422-unprocessable-content
- MDN, 422 Unprocessable Content: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422
- FastAPI, handling errors: https://fastapi.tiangolo.com/tutorial/handling-errors/
- RFC 9457, Problem Details for HTTP APIs (considered, not adopted): https://www.rfc-editor.org/rfc/rfc9457.html
