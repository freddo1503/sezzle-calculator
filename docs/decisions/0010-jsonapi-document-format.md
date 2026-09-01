---
number: 10
title: JSON:API as the document format, and the strain of modelling a calculation as a resource
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: The contract follows JSON:API v1.1 for its media type, document structure and error objects, accepting that a calculation is an operation rather than a resource and that the specification defines no mechanism for operations of that kind.
tags: [api, contract, jsonapi, errors]
updated: 2026-09-01
---

# ADR-0010: JSON:API as the document format, and the strain of modelling a calculation as a resource

## Context

The contract needed a document format. Until now it used a house shape: a bare request object,
and a `{"error": {"code", "message", "details"}}` envelope invented for this project
([ADR-0005](0005-error-model-and-status-codes.md)).

A house format costs nothing to design and everything to explain. Every consumer has to read
our documentation to learn what an error looks like, and every convention inside it, such as an
`operand_index` naming the offending operand, is one we made up and must then police ourselves.

[JSON:API](https://jsonapi.org/format/) is a published specification for exactly this: media
type, document structure, and a defined error object.

**The honest difficulty, stated before the decision rather than after it.** JSON:API is
resource-oriented, built around fetching and modifying stored things. A calculation is not a
stored thing. It is an operation: a request-response evaluation with no persistence and nothing
to retrieve afterwards. The specification does not define a standardized mechanism for
operations of that kind, and its own frequently-asked-questions page says it is "still working
on a way for resources to advertise and detail non-standard actions they support".

So adopting it here is an accommodation, not a natural fit, and it should be judged as one.

## Decision

Follow JSON:API v1.1 for the document format, at
[`openapi.yaml`](../../openapi.yaml).

- **`POST /api/calculations`**, resource-oriented, because that is what JSON:API is.
- **Media type `application/vnd.api+json`** on every request and response. Orval emits it as the
  `Content-Type` header in the generated client.
- **Request** is a JSON:API document whose primary data is a new calculation with no `id`, which
  the specification permits for a resource originating at the client:
  `{"data": {"type": "calculations", "attributes": {"operation": "add", "operands": ["0.1", "0.2"]}}}`.
- **Response** is `200 OK` carrying the same resource with a server-assigned `id` and the
  computed `result`, with the operation and operands echoed back so the response is
  self-describing.
- **Errors** are a JSON:API `errors` array. Each object carries `status` as a string, our `code`,
  a `title`, a `detail`, and `source.pointer`, an RFC 6901 JSON Pointer.
- **415** is added for an unsupported media type, which the specification requires.
- New error code `UNSUPPORTED_MEDIA_TYPE`.

### Where the accommodation shows, named rather than smoothed over

**`200 OK`, not `201 Created`.** A resource-creation endpoint would normally return 201 with a
`Location` header. Nothing here is stored, so there is no location to point at and no `self`
link that would resolve. The `id` identifies an evaluation, not a retrievable record: no `GET`
will ever find it. That is a deviation from what a reader fluent in JSON:API expects, and it is
written into the contract's own description rather than left to be discovered.

**The ceremony.** Every request grows a `data` / `type` / `attributes` wrapper around what was
previously two fields. On a brief that says to prioritise correctness and clarity over extra
features, a reviewer could fairly call this over-engineering for a calculator, and that reading
would not be unreasonable.

### What it buys, which is real rather than consolation

- **`source.pointer` names the offending operand exactly**, as `/data/attributes/operands/1`,
  using a standard JSON Pointer instead of the `operand_index` convention we had invented. A
  client written by someone else already knows how to read it.
- **The error shape is a specification other people know**, not a house format that has to be
  learned from our documentation.
- **`data` and `errors` MUST NOT coexist**, per the specification. That is a structural
  guarantee, where the house envelope relied on a convention we would have had to state and then
  enforce ourselves.

## Alternatives considered

- **The previous house envelope**, `{"error": {"code", "message", "details"}}`. Simpler, smaller,
  and with no wrapper ceremony, and it is the thing this decision's cost is paid against. It is
  the right answer for an API with one consumer and no ambition to be recognised, which is
  arguably what this is. Rejected because every convention in it was ours to invent, document
  and police, and because pointing at an offending operand meant inventing an index convention
  when a standard one already exists.
- **RFC 9457 Problem Details for HTTP APIs.** Already considered and rejected in
  [ADR-0005](0005-error-model-and-status-codes.md) as disproportionate. Now doubly moot: JSON:API
  defines its own error objects, and running both would mean two error formats in one API.
- **Plain resource-oriented REST without JSON:API.** Gets the resource framing without the
  wrapper, but leaves the error shape and the field-pointing convention to be invented again,
  which is most of what was being bought.

## Consequences

### Positive

- One published, recognisable format for documents and errors.
- Offending fields are pointed at with RFC 6901 JSON Pointers rather than a private convention.
- The mutual exclusion of `data` and `errors` is guaranteed by the format.
- Generation is unaffected: `datamodel-code-generator` and Orval both handle the document
  schemas, and the discriminated union simply moved down to `data.attributes.operation`.

### Negative

- **A calculation is not a resource**, and the specification offers nothing for operations that
  are not. Everything above is an accommodation of that mismatch.
- **`200` instead of `201`** will read as wrong to someone who knows JSON:API but has not read
  why.
- **Wrapper ceremony** on a small brief, defensible as standards conformance and attackable as
  over-engineering. Both readings are available to an evaluator.
- **More surface to get right**: the media type, the 415 case, and the error array are three more
  things to implement and test than the house envelope needed.

### Neutral

- The status-code reasoning is untouched by this decision. 400 only for an unparseable body, 422
  for anything understood but not computable, 500 reserved for genuine bugs. See
  [ADR-0005](0005-error-model-and-status-codes.md).
- Clients still branch on `code` and never on human-readable text. `code` is now a member the
  specification defines rather than one we invented.

## References

- JSON:API v1.1: https://jsonapi.org/format/
- JSON:API frequently asked questions, on non-standard actions: https://jsonapi.org/faq/
- RFC 6901, JSON Pointer: https://www.rfc-editor.org/rfc/rfc6901.html
