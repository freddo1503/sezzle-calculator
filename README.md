<!--
  SUBMISSION CHECKLIST, remove this comment before sending the repository link.

  Every unfinished section below is marked with a visible "> **TODO**" blockquote, on
  purpose: an unfilled placeholder should be obvious in the rendered page, not hidden.

  Before submitting, this must return nothing:
      grep -rn '^> \*\*TODO\*\*' README.md PROMPTS.md docs/

  Section order is not arbitrary. It maps one-to-one onto the assignment's required
  README contents: setup, how to run each layer, API examples, design decisions and
  assumptions, plus tests and coverage from the deliverables list.
-->

# Sezzle Calculator

A full-stack calculator: a React keypad calling a Python backend service that performs
**exact decimal arithmetic**. Built as a take-home technical assessment.

`0.1 + 0.2` returns exactly `0.3`, not `0.30000000000000004`. That is a deliberate design
choice, and it is [argued in full](docs/decisions/0004-exact-decimal-arithmetic.md).

| | |
|---|---|
| **Frontend** | React, TypeScript, Vite, shadcn/ui on Radix with Tailwind |
| **Backend** | Python, FastAPI, `uv` |
| **Contract** | `openapi.yaml`, hand-authored, both layers held to it |
| **Arithmetic** | `decimal.Decimal`, 28 significant digits, banker's rounding |
| **Full architecture** | [`docs/architecture.md`](docs/architecture.md) |
| **Decisions** | [`docs/decisions/`](docs/decisions/), nine records |
| **Prompts used** | [`docs/13-prompt-record.md`](docs/13-prompt-record.md), an assignment deliverable |

> **Note on the backend language.** The assignment states that Go is preferred. This
> submission uses Python, deliberately. The reasoning, and what that choice costs, is in
> [ADR-0002](docs/decisions/0002-python-fastapi-instead-of-go.md) and summarised under
> [Design decisions](#design-decisions-and-assumptions) below. It is placed here rather
> than buried, because it is the first thing a reader deserves to know.

---

## Prerequisites

| Tool | Purpose |
|---|---|
| [`uv`](https://docs.astral.sh/uv/) | Python version, virtual environment, and backend dependencies |
| [`pnpm`](https://pnpm.io/) with [Node.js](https://nodejs.org/) 22 or later | Frontend toolchain and dependencies |
| [`just`](https://just.systems/) | Command runner. Every command in this README is a `just` recipe |
| Docker and Docker Compose | Only for the assembled run and the end-to-end smoke test. **Not needed for development** |

`uv` installs the required Python version itself, so no system Python setup is needed. The
frontend uses Tailwind v4 (the `tailwindcss` package with the `@tailwindcss/vite` plugin),
which shadcn/ui is built on. The install recipe handles it.

> **TODO** Confirm the minimum Node, pnpm and Docker Compose versions actually exercised.

## Setup

```bash
git clone https://github.com/freddo1503/sezzle-calculator.git
cd sezzle-calculator
just dev
```

**One command takes a clean clone to a running application.** `just dev` installs both layers
(`uv sync` and `pnpm install --frozen-lockfile`) and runs them on the host: the backend with
reload, the frontend on the Vite development server. No container is involved and nothing is
built.

A developer, continuous integration, and an AI agent all enter through the same `just`
recipes, so there is no second, undocumented way to build or test this project.

> **TODO** Confirm the recipe names against the `justfile`, and list every environment
> variable or state explicitly that none is required.

## Running

### Development, host-native

```bash
just dev
```

> **TODO** Fill in the frontend and backend URLs and the interactive API documentation URL.

### The assembled stack, Docker Compose

Builds images and runs the whole thing with no toolchain installed, which is also what the
end-to-end smoke test runs against. The frontend is a production build served statically.

> **TODO** Fill in the Compose recipe name and the served URL once the `justfile` exists.

### One layer at a time, the fast inner loop

```bash
just backend
just frontend
```

The frontend never holds an absolute backend address: it calls a same-origin relative path
that the Vite development server proxies to the backend, and that the static file server
proxies in the Compose stack. There is no cross-origin configuration and no base URL to set.

> **TODO** Fill in the per-layer URLs and the proxied API path once both layers exist.

## API usage

One endpoint. The reasoning for a single generic endpoint rather than one per operation is
in [ADR-0003](docs/decisions/0003-single-calculate-endpoint.md).

```
POST /api/calculate
Content-Type: application/json
```

| Operation | Value of `operation` | Operands |
|---|---|---|
| Addition | `add` | 2 |
| Subtraction | `subtract` | 2 |
| Multiplication | `multiply` | 2 |
| Division | `divide` | 2 |
| Exponentiation | `power` | 2 (base, exponent) |
| Square root | `sqrt` | 1 |
| Percentage | `percent` | 2 (`a` percent of `b`, a binary operator on the keypad) |

Three domain rules the contract fixes: `percent(a, b) = a / 100 * b`; operands are bounded, so
an oversized one fails as `OPERAND_OUT_OF_RANGE`; and a negative base with a fractional exponent
is a domain error, since the real-valued result does not exist.

The contract is hand-authored in `openapi.yaml` at the repository root
([ADR-0007](docs/decisions/0007-api-first-openapi-contract.md)), and every wire type on both
sides is generated from it
([ADR-0008](docs/decisions/0008-generate-all-wire-types.md)).

**Operands and results are JSON strings, not JSON numbers.** This is deliberate: a JSON
number is parsed by browsers into an IEEE-754 double, which would silently destroy the
exactness the backend just computed. See
[ADR-0004](docs/decisions/0004-exact-decimal-arithmetic.md).

### A successful calculation

```bash
curl -X POST http://localhost:8000/api/calculate \
  -H 'Content-Type: application/json' \
  -d '{"operation": "add", "operands": ["0.1", "0.2"]}'
```

```json
{ "result": "0.3" }
```

### Division by zero

```bash
curl -X POST http://localhost:8000/api/calculate \
  -H 'Content-Type: application/json' \
  -d '{"operation": "divide", "operands": ["1", "0"]}'
```

```json
{
  "error": {
    "code": "DIVISION_BY_ZERO",
    "message": "Division by zero is undefined.",
    "details": { "operation": "divide", "operand_index": 1 }
  }
}
```

Returned with HTTP 422, not 400. The request is well-formed and understood; it simply
cannot be computed. The argument, with the relevant part of RFC 9110, is in
[ADR-0005](docs/decisions/0005-error-model-and-status-codes.md).

### Invalid input

```bash
curl -X POST http://localhost:8000/api/calculate \
  -H 'Content-Type: application/json' \
  -d '{"operation": "add", "operands": ["1", "abc"]}'
```

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Operand is not a valid decimal number.",
    "details": { "operand_index": 1 }
  }
}
```

### Error codes

Every failure returns the same envelope. The client branches on `code` for behaviour and
renders the backend's `message` for the user; it holds no error strings of its own.

| Code | HTTP | Meaning |
|---|---|---|
| `MALFORMED_REQUEST` | 400 | The body could not be parsed as JSON |
| `VALIDATION_ERROR` | 422 | The body parsed but failed schema validation |
| `UNKNOWN_OPERATION` | 422 | `operation` is not a supported value |
| `WRONG_OPERAND_COUNT` | 422 | Wrong number of operands for the operation |
| `INVALID_OPERAND` | 422 | An operand is not a valid decimal number |
| `OPERAND_OUT_OF_RANGE` | 422 | An operand exceeds the permitted magnitude |
| `DIVISION_BY_ZERO` | 422 | Division by zero |
| `NEGATIVE_SQRT` | 422 | Square root of a negative number |
| `UNDEFINED_RESULT` | 422 | The result is mathematically undefined |
| `RESULT_OVERFLOW` | 422 | The result exceeds the decimal context range |

The authoritative enumeration lives in `openapi.yaml`; this table documents it and does not
define it.

> **TODO** Run every example above against the finished service and paste the real
> responses. Reconcile this table against the enumeration in `openapi.yaml`, and add the
> interactive OpenAPI documentation URL.

## Design decisions and assumptions

Full rationale, including rejected alternatives, is in
[`docs/decisions/`](docs/decisions/). Summary:

### Python and FastAPI, though the assignment prefers Go

The brief says Go is *preferred*, not required. Within a 2 to 4 hour budget, the graded
qualities (correctness, clarity, maintainability, tests) are best served by working in the
author's strongest language. Two further reasons: Python's standard library provides exact
decimal arithmetic with no dependency, which the numeric decision below leans on, and
FastAPI derives request validation, JSON responses, and API documentation from type
declarations.

**What this costs, stated plainly**: this submission provides no evidence of Go
proficiency. If that matters to the role, this artefact cannot demonstrate it. The API
contract is language-agnostic and the tests describe the contract rather than the
implementation, so a Go port would not touch the frontend. Full argument, including the
case *for* Go, in [ADR-0002](docs/decisions/0002-python-fastapi-instead-of-go.md).

### Exact decimal arithmetic instead of floating point

Binary floating point makes `0.1 + 0.2` produce `0.30000000000000004`. For an
accounting-adjacent role that is the wrong answer to a question worth asking. Arithmetic
uses `decimal.Decimal` at 28 significant digits with `ROUND_HALF_EVEN` (banker's
rounding), and values cross the wire as strings so the browser cannot undo the exactness
when parsing. [ADR-0004](docs/decisions/0004-exact-decimal-arithmetic.md).

### The frontend holds no business rules

Its role is to display data. Validation uses the Zod schemas generated from the contract, never
hand-written checks or a local list of operations. Error wording comes from the backend's
`message`, not a string table in the client. And arithmetic semantics stay out: pressing equals
twice does nothing, because repeat-on-equals is a rule about what an operation means when
reapplied, and the only two places to put it are a layer that may not hold rules or an API that
would have to keep session state. The behaviour is absent rather than misplaced.
[`docs/architecture.md`](docs/architecture.md) § 2 and § 8.3.

### Full precision in the API, rounding only on screen

The API returns the exact value; the frontend rounds to two decimal places for display alone.
Rounding inside the contract was rejected because it would make `1/8` return `0.12`, `sqrt(2)`
return `1.41`, and `1/3` then times three return `0.99` instead of `1`. The keypad therefore
chains on the exact value returned, never on the rounded string on screen, which is what stops
a chained calculation drifting. Percentage is `percent(a, b) = a / 100 * b`, so
`percent(20, 50)` is `10`.

### One endpoint, not one per operation

`POST /api/calculate` with the operation as a field of a discriminated union. This buys one
uniform error contract, one validation surface, and a new operation as a data change
rather than a routing change. It costs self-describing URLs.
[ADR-0003](docs/decisions/0003-single-calculate-endpoint.md).

### One error envelope, machine-readable codes

Every failure returns the same shape with a stable `code`. 400 only when the request
cannot be parsed, 422 for anything well-formed that cannot be computed (including division
by zero), and 500 reserved strictly for genuine bugs.
[ADR-0005](docs/decisions/0005-error-model-and-status-codes.md).

### API-first: the contract is the source of truth

`openapi.yaml` is hand-authored and committed before either layer exists. The backend
implements it, the frontend's TypeScript types are generated from it, and continuous
integration fails if either drifts. This runs against FastAPI's grain, which normally
derives the specification from the code; a specification generated from the implementation
agrees with it by construction and so can never catch a mistake. The drift check is what
makes the contract real rather than a claim.
[ADR-0007](docs/decisions/0007-api-first-openapi-contract.md).

### Every wire type is generated, on both sides

No type describing the wire format is hand-written anywhere. Backend Pydantic models come from
`datamodel-code-generator`; the frontend's types, HTTP client and Zod schemas come from Orval.
Both are generated from `openapi.yaml` and committed, and continuous integration fails if
either is stale. A consequence worth naming: the implementation language becomes exchangeable,
so a Go port would regenerate its types from the same contract and reimplement the arithmetic
engine, leaving the contract, the frontend and the contract tests untouched.
[ADR-0008](docs/decisions/0008-generate-all-wire-types.md).

### The response is validated at runtime, not just at compile time

Generated TypeScript types are erased at build time: they constrain what the frontend sends and
check nothing about what it receives. Orval's Zod schemas validate the actual response against
the contract at the boundary, so a backend that violates the contract fails loudly and locally
instead of surfacing as a rendering bug somewhere else. It costs bundle weight and a validation
pass per response, and it is the only place the contract is tested against reality rather than
against a generator.

### shadcn/ui, generated into the repository rather than imported

A keypad's hard part is not the grid of buttons, it is focus handling, accessible names for
symbol-labelled keys, and physical keyboard support. Radix primitives supply those. The
decisive property is that shadcn/ui is not a dependency: components are copied into
`src/components/ui/` and owned here, so the component code reads as ours rather than as our
composition of someone else's library. The cost is that Tailwind returns to the stack, which
is a reversal, and that adding a component is a one-time generation step outside `just`.
[ADR-0006](docs/decisions/0006-shadcn-ui-component-library.md).

### Method: contract, then tests, then implementation

The arithmetic engine is written test-first (red, green, refactor), being pure functions
with no input or output. API tests derive from the contract. Commits are kept to one logical
change each, since the public history is part of what an evaluator sees. This is the
intended discipline, not a claim about every commit.

### Assumptions

One thing remains genuinely assumed rather than decided: **"microservice"** is read as one
backend process the frontend calls over HTTP, not as a mandate for several services. It is a
reading of the brief's wording, and being wrong about it would not change the system.

Everything else the brief left open has since been decided and is stated above as a decision:
percentage semantics, operand bounds, the negative-base exponent rule, and precision with
display-only rounding. See [`docs/architecture.md`](docs/architecture.md) § 11.3.

### Deliberately out of scope

Not requested by the brief, which asks for correctness over extra features: calculation
history, operator precedence (the keypad evaluates one binary operation per press, so
`2 + 3 * 4` follows keypad order), authentication, rate limiting, and persistence. The full
list, with reasons, is in [`docs/architecture.md`](docs/architecture.md) § 11.2.

## Tests and coverage

```bash
just test
just coverage
```

The highest-value tests are on the arithmetic engine, which is pure functions with no
knowledge of HTTP: each operation, the exactness property (`0.1 + 0.2` is exactly `0.3`),
and each domain error. The API tests verify the contract (status codes, error codes,
envelope shape). The frontend tests cover the keypad's input state machine (a second equals does
nothing, operator-after-operator replaces the pending operator), rendering, and that the
backend's error `message` is what reaches the user.

**One end-to-end test**, in Playwright against the Compose stack: type `0.1`, `+`, `0.2`, `=`,
and assert the display reads exactly `0.3`. The unit tests prove each hop in isolation; this is
the only artefact that proves the exactness claim survives the whole composition, from the
engine through the contract, the generated client, the runtime validation and the rendering. A
larger end-to-end suite is deliberately out of scope.

Coverage is published as a fact and **no threshold blocks anywhere**: the brief asks for a
coverage report, not a target, and a number reported without one having been aimed at is worth
more than a number a gate forced upward.

GitHub Actions runs on every push. Five gates block and one advises, listed once in
[`docs/architecture.md`](docs/architecture.md) § 7.1.

> **TODO** Paste the actual coverage numbers for both layers, name the test runners, and
> state where the coverage report is written. Coverage is reported as a fact, not
> presented as a target that was aimed at.

## Project structure

```
sezzle-calculator/
├── openapi.yaml        The contract. Hand-authored, the source of truth for both layers
├── orval.config.ts     Frontend generation: types, HTTP client, Zod schemas
├── backend/            Python, FastAPI. The arithmetic engine and the API
├── frontend/           React, TypeScript, Vite. Everything wire-shaped is generated
│   └── src/components/ui/   shadcn/ui components, generated and owned here
├── e2e/                One Playwright smoke test against the Compose stack
├── docs/               Architecture and decision records
├── .github/workflows/  Continuous integration. Gates listed in docs/architecture.md § 7.1
├── justfile            Every command in this README
├── compose.yaml        The assembled stack, for the one-command run and the smoke test
├── pnpm-lock.yaml      Frontend lockfile
├── PROMPTS.md          Prompts used, an assignment deliverable
└── README.md
```

> **TODO** Reconcile with the real tree once both layers exist.

## Documentation

| Document | Contents |
|---|---|
| [`docs/index.md`](docs/index.md) | Documentation catalog, and a table of common questions with where each is answered |
| [`docs/architecture.md`](docs/architecture.md) | Goals, constraints, container and component diagrams, runtime view, deployment, quality scenarios, risks, glossary |
| [`docs/decisions/`](docs/decisions/) | Nine Architecture Decision Records |
| [`docs/13-prompt-record.md`](docs/13-prompt-record.md) | Chronological record of the prompts used to build this repository. **An explicit deliverable of the assignment** |

## Licence

[MIT](LICENSE), copyright 2026 Frédéric Ferrera.
