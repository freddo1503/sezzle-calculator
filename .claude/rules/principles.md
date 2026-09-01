# Guiding Principles

Three principles are the compass for every decision in this repository: **DRY**, **KISS**, and **separation of concerns**. They are not decoration. When a choice is not obvious, they decide it, and when they disagree with each other, the tie-break at the bottom of this file decides.

## Don't Repeat Yourself (DRY)

DRY is about **knowledge**, not about text. Every piece of knowledge has one authoritative representation. Two blocks of code that look alike but change for different reasons are not duplication, and merging them is a mistake that couples two things which were right to be apart.

In this repository that principle has one dominant application: **`openapi.yaml` is the single authoritative statement of the wire contract.** Everything downstream is generated from it, never written by hand:

| Knowledge | Single source | Derived from it |
|---|---|---|
| Wire contract | `openapi.yaml` | Backend Pydantic models, frontend types, frontend client, Zod schemas |
| Arithmetic behaviour | The engine's pure functions | Everything the API and the interface report |
| Commands | `justfile` | What a developer runs, what continuous integration runs |

Consequences that follow, and that are not negotiable:

- No type describing a request or a response is hand-written, on either side.
- No error code is written twice. The enumeration lives in the contract.
- Continuous integration fails when a generated artefact drifts from its source. A single source of truth that nothing enforces is a comment, not a constraint.
- A command that appears in the README appears as a `just` recipe. Documentation that restates a command instead of naming a recipe has duplicated knowledge.

### Standard library first

A dependency is knowledge borrowed from outside the repository, and every one of them is a thing to install, audit, update and explain. **Reach for the standard library before reaching for a package**, on both sides.

This is why `decimal.Decimal` carries the arithmetic rather than a third-party fixed-point package: it ships with Python, it is correctly rounded base-10 arithmetic with a configurable context, and it needs no defence beyond naming it.

A dependency earns its place when it does something the standard library does not do at all, or does something the standard library does badly enough to be a source of defects. Generating types from the contract qualifies, because hand-writing them is the failure this design exists to prevent. A helper that saves five lines does not qualify.

## Keep It Simple (KISS)

The assignment budget is 2 to 4 hours and its own instruction is to prioritise correctness, clarity and maintainability over extra features. Simplicity here is not a style preference, it is the grading criterion.

- Prefer the boring construction. A reviewer reads this once, quickly, and every clever line spends their attention.
- Do not build for requirements nobody stated. Calculation history, expression parsing with operator precedence, authentication and persistence are all out of scope, and their absence is a decision, not an omission.
- An abstraction earns its place when it has a second caller, not when a second caller is imagined.
- If a decision needs a long defence, it is probably the wrong decision. The exception is a decision that departs from the brief, which needs its defence written down precisely because it is surprising.
- Simple is not the same as short. A guard clause that names an edge case beats a dense expression that handles it silently.

## Separation of concerns

Each unit knows one thing and is ignorant of the rest. This is what makes the code testable, which the assignment grades explicitly.

The boundaries in this repository, and what each side must not know:

- **The arithmetic engine knows nothing about HTTP.** It takes decimals and returns decimals or raises domain errors. It has no request object, no status code, no framework import. This is what lets the operations be tested exhaustively as pure functions.
- **The HTTP layer knows nothing about arithmetic.** It validates, delegates, and maps domain errors onto the error envelope. It never computes.
- **The input state machine knows nothing about arithmetic.** It tracks what has been typed, which operator is pending, and whether the display holds a result. It never evaluates anything; it decides when to ask the backend.
- **The interface knows nothing about how the backend computes.** It knows the contract, and only the contract.
- **The interface holds no business rules. Its role is to display data.** Validation rules arrive as schemas generated from the contract, error wording arrives in the response, and arithmetic semantics stay in the backend. Formatting a value for display is presentation, not a rule: a business rule changes what the answer is, a formatting choice changes only how it is shown.

A test that needs the whole stack running to check one arithmetic edge case is evidence that a boundary has leaked.

## When the principles disagree

They will. DRY pushes toward factoring shared code out, and separation of concerns pushes toward letting two layers each own their version of it. The tie-break, in order:

1. **Separation of concerns wins over DRY** when factoring would make two layers share a type or a helper that would then have to change for two unrelated reasons. Coupling is more expensive than a small repetition.
2. **KISS wins over DRY** when removing a repetition costs an abstraction that has exactly one caller. Wait for the second caller.
3. **DRY wins outright for the wire contract.** This case is settled and is not re-litigated: duplicating the contract is the specific failure this design exists to prevent.

When a decision is made this way and a competent reviewer could reasonably have gone the other direction, it becomes an Architecture Decision Record in `docs/decisions/`. Otherwise it is just a choice, and it does not need a file.
