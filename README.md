<!--
  Section order maps one-to-one onto the assignment's required README contents: setup, how to
  run each layer, API examples, design decisions and assumptions, plus tests and coverage.

  Unfinished content is marked with a visible "> **TODO**" blockquote, on purpose. Before
  submitting, this must return nothing:
      grep -rn '^> \*\*TODO\*\*' README.md docs/

  Keep this file short. Reasoning belongs in docs/decisions/, not here.
-->

# Sezzle Calculator

A full-stack calculator: a React keypad calling a Python service that performs **exact decimal
arithmetic**. `0.1 + 0.2` returns exactly `0.3`, not `0.30000000000000004`.

React, TypeScript, shadcn/ui and Vite on the front. Python, FastAPI and `uv` on the back. The
hand-authored [`openapi.yaml`](openapi.yaml) is the contract, and every wire type on both sides
is generated from it.

> **The backend is Python, though the assignment prefers Go.** That is deliberate, and what it
> costs is stated plainly in
> [ADR-0002](docs/decisions/0002-python-fastapi-instead-of-go.md). It is the first thing a reader
> deserves to know, so it is here rather than buried.

## Setup

```bash
git clone https://github.com/freddo1503/sezzle-calculator.git
cd sezzle-calculator
just dev
```

One command takes a clean clone to a running application: it installs both layers (`uv sync` and
`pnpm install --frozen-lockfile`) and runs them on the host. No container, nothing built.

Needs [`uv`](https://docs.astral.sh/uv/), [`pnpm`](https://pnpm.io/) with Node 22 or later, and
[`just`](https://just.systems/). Docker is needed only for the assembled run and the end-to-end
test, never for development.

> **TODO** Confirm recipe names against the `justfile`, and list any environment variables or
> state that none is required.

## Running

| Command | What it does |
|---|---|
| `just dev` | Both layers on the host. The documented entry point |
| `just backend`, `just frontend` | One layer at a time, the fast inner loop |
| Compose recipe | The assembled stack, no toolchain needed, and what the end-to-end test runs against |

The frontend calls a same-origin relative path proxied to the backend, so there is no
cross-origin configuration and no backend address to set.

> **TODO** Fill in the served URLs, the interactive API documentation URL, and the Compose recipe
> name once the `justfile` exists.

## API usage

One endpoint, `POST /api/calculations`, in [JSON:API](https://jsonapi.org/format/) documents.
Operations: `add`, `subtract`, `multiply`, `divide`, `power`, `percent`, `sqrt`.

**Operands and results are JSON strings, not numbers.** A JSON number is reparsed by the browser
into an IEEE-754 double, which would destroy the exactness the server just computed.

```bash
curl -X POST http://localhost:8000/api/calculations \
  -H 'Content-Type: application/vnd.api+json' \
  -d '{"data":{"type":"calculations","attributes":{"operation":"add","operands":["0.1","0.2"]}}}'
```

```json
{ "data": { "type": "calculations", "id": "018f3a2b-4c5d-7e8f-9a0b-1c2d3e4f5a6b",
            "attributes": { "operation": "add", "operands": ["0.1", "0.2"], "result": "0.3" } } }
```

Division by zero returns `422`, not `400`: the request is understood, it simply has no answer.

```json
{ "errors": [ { "status": "422", "code": "DIVISION_BY_ZERO",
                "title": "Division by zero", "detail": "Division by zero is undefined.",
                "source": { "pointer": "/data/attributes/operands/1" } } ] }
```

Clients branch on `code` and render the server's `title` and `detail`. The full code enumeration
is in [`openapi.yaml`](openapi.yaml); the reasoning is in
[ADR-0005](docs/decisions/0005-error-model-and-status-codes.md).

> **TODO** Run these against the finished service and paste the real responses.

## Design decisions and assumptions

Each links to the record that argues it, including what was rejected and why.

| Decision | Record |
|---|---|
| Python and FastAPI, though Go is preferred, with the cost stated | [ADR-0002](docs/decisions/0002-python-fastapi-instead-of-go.md) |
| One generic endpoint rather than one per operation | [ADR-0003](docs/decisions/0003-single-calculate-endpoint.md) |
| Exact decimal arithmetic, strings on the wire, rounding only on screen | [ADR-0004](docs/decisions/0004-exact-decimal-arithmetic.md) |
| 400 only for an unparseable body, 422 for anything understood but not computable | [ADR-0005](docs/decisions/0005-error-model-and-status-codes.md) |
| shadcn/ui generated into the repository rather than imported | [ADR-0006](docs/decisions/0006-shadcn-ui-component-library.md) |
| API-first: the hand-authored contract is the source of truth | [ADR-0007](docs/decisions/0007-api-first-openapi-contract.md) |
| Every wire type generated from it, both sides, validated at runtime by Zod | [ADR-0008](docs/decisions/0008-generate-all-wire-types.md) |
| Toolchain, with `ty` non-blocking because it is pre-1.0 | [ADR-0009](docs/decisions/0009-toolchain.md) |
| JSON:API, and the strain of modelling a calculation as a resource | [ADR-0010](docs/decisions/0010-jsonapi-document-format.md) |

**The frontend holds no business rules**; its role is to display data. Validation comes from the
generated Zod schemas, error text from the response, and arithmetic semantics from the backend,
so pressing equals twice does nothing.
[`docs/architecture.md`](docs/architecture.md) § 2.

**Assumptions.** One thing remains genuinely assumed rather than decided: "microservice" is read
as one backend process, not a mandate for several. Everything else the brief left open has been
decided and recorded. What was left out on purpose, and why, is in
[`docs/architecture.md`](docs/architecture.md) § 11.2.

## Tests and coverage

```bash
just test
just coverage
```

The highest-value tests are on the arithmetic engine, which is pure functions with no knowledge
of HTTP. One Playwright smoke test runs against the Compose stack and proves the exactness claim
survives every hop, which unit tests cannot. Coverage is published as a fact with **no blocking
threshold**: the brief asks for a report, not a target.

> **TODO** Paste the actual coverage numbers for both layers and name the test runners.

## Documentation

| Document | Contents |
|---|---|
| [`docs/index.md`](docs/index.md) | Catalog, and a table of common questions with where each is answered |
| [`docs/architecture.md`](docs/architecture.md) | Goals, constraints, diagrams, runtime, deployment, quality, risks |
| [`docs/decisions/`](docs/decisions/) | Ten Architecture Decision Records |
| [`docs/13-prompt-record.md`](docs/13-prompt-record.md) | Every prompt used to build this repository. **An explicit deliverable of the assignment** |

## Licence

[MIT](LICENSE), copyright 2026 Frédéric Ferrera.
