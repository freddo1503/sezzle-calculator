<!--
  Append a new entry at the bottom for every substantive prompt, while the work is
  happening. Reconstructing this file from memory at the end produces a tidier document
  and a less honest one.

  Copy the template under "Entry template" and fill every field. The "Changes made to the
  output" field is the important one: it is the difference between using a tool and
  accepting whatever it produced.

  Before submitting, this must return nothing:
      grep -rn '^> \*\*TODO\*\*' README.md docs/
-->

---
summary: Chronological record of every prompt used to build this repository, reproduced verbatim for the author's own prompts and condensed for longer intermediate briefs. Sharing the prompts is an explicit deliverable of the assignment.
tags: [prompts, deliverable, process]
updated: 2026-09-01
---

# 13. Prompt record

An appendix to the collapsed arc42 in [`architecture.md`](architecture.md). Numbered 13
because arc42 runs to 12 and its section 12, the glossary, was deliberately dropped;
reusing 12 would misname this page.


The assignment says: "Use any AI tooling you would like" and "Share any prompts that you
used in your work." This file is that record.

**Tooling**: Claude Code (Anthropic's command-line coding tool), with a documentation plugin
implementing Andrej Karpathy's "LLM Wiki" pattern.

**Two tiers of fidelity, and why.** The author's own prompts are reproduced verbatim,
including French ones with a bracketed English gloss where the meaning matters, because
those are the real human instructions the assignment asks to see. Longer intermediate briefs
passed between agents run to many hundreds of words each; those are marked `(condensed)`,
with substance preserved and length cut. Nothing is reworded after the fact to look better.

---

## Entry template

```markdown
## NNN. Short title

| | |
|---|---|
| **Date** | YYYY-MM-DD |
| **Phase** | Documentation, backend, frontend, tests, or infrastructure |
| **Author** | Frédéric, or an intermediate agent brief |
| **Fidelity** | Verbatim, or condensed |

**Prompt**

> The prompt text.

**What it produced**

What came back, in terms of files and decisions.

**Changes made to the output**

What was corrected, rejected, or rewritten by hand, and why. Write "accepted as produced"
only when that is true.
```

---

## 001. Create the repository for the assessment

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Setup |
| **Author** | Frédéric |
| **Fidelity** | Verbatim, with one redaction |

**Prompt**

> next https://app3.greenhouse.io/tests/[REDACTED] let's create a github repo for this exam

The Greenhouse test identifier is redacted because this repository is public and that
token addresses the author's individual assessment instance. Nothing else is altered.

**What it produced**

The public GitHub repository `freddo1503/sezzle-calculator`, empty, with the default branch
renamed to `main` before any commit.

**Changes made to the output**

Accepted as produced.

## 002. Documentation before any code

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Documentation |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> before any code let's init a docs with @docs-modus:doc-maintainer (agent)

**What it produced**

The instruction to scaffold the documentation layer first, delegated to a documentation
agent. This is the decision that made the architecture and the decision records precede the
implementation, which in turn is what made the API-first contract in
[ADR-0007](decisions/0007-api-first-openapi-contract.md) possible: the contract could be
authored before there was any code to derive it from.

**Changes made to the output**

Accepted as produced.

## 003. Scaffold the documentation layer

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Documentation |
| **Author** | Intermediate agent brief |
| **Fidelity** | Condensed |

**Prompt**

> Initialise the documentation layer for an empty repository. Documentation only: no
> application code, no build configuration, no package manifests.
>
> The repository will become a take-home assessment for a Sezzle "Software Engineer II with
> Accounting Experience (Brazil)" application. [The full assignment brief was supplied
> verbatim here; it is transcribed in `docs/raw/2026-08-27-assignment-brief.md`.] Deadline
> Thursday 2026-09-03, effort budget 2 to 4 hours, so the documentation must be
> proportionate: an evaluator reads it in a few minutes. Do not produce a sprawling wiki.
>
> Decisions already made, to be documented rather than re-opened. Frontend: React and
> TypeScript with Vite. Backend: Python and FastAPI managed with `uv`, deliberately
> departing from the brief's preferred Go because Python is my strongest language and the
> assignment weights correctness and maintainability over stack conformance. That deviation
> must be argued head-on in a decision record and surfaced in the README, since it is the
> single most likely thing an evaluator will question. `just` is the single source of truth
> for commands. Docker and Docker Compose are available.
>
> Produce: a `docs/` structure with an index traversable without opening every file;
> decision records for the choices that carry risk, at minimum the Python-instead-of-Go
> departure, the API shape (one generic `POST /calculate` versus one endpoint per operation,
> pick one and argue it), the numeric strategy (exact decimal arithmetic versus IEEE-754
> floats, load-bearing because the role is accounting-flavoured and `0.1 + 0.2` must not
> display `0.30000000000000004`), and the error model mapping validation failures, division
> by zero, square root of a negative, and overflow to JSON and HTTP status codes; an
> architecture overview with a C4-style container view as a Mermaid diagram plus a quality
> section tied to what the assignment grades; a README skeleton whose sections map one-to-one
> onto the assignment's required contents, with clear placeholders for what only exists once
> the code does; and a `PROMPTS.md` skeleton, since sharing prompts is an explicit
> deliverable.
>
> Diagrams are Mermaid, never ASCII art. No em dashes in prose. Expand every acronym on first
> use. Markdown throughout.

**What it produced**

The documentation layer: the wiki schema, index, log, architecture overview, the assignment
source summary, five decision records, and the two root deliverables `README.md` and this
file.

Two scoping judgements, both omissions made on purpose and recorded rather than left silent:
arc42 was collapsed from twelve section files into one `architecture.md`, and the C4 system
context diagram was dropped because a system with one actor and no external dependencies
produces a context diagram that restates the container diagram with less information.

Before the decision records were written, the technical claims were verified against primary
sources rather than asserted: the Python `decimal` documentation for default precision,
rounding mode, and exception names; the FastAPI documentation for validation-error handling;
and RFC 9110 with MDN for the 400 versus 422 distinction the error model turns on.

**Changes made to the output**

> **TODO** Fill in after reviewing the generated documentation. Record what was rewritten or
> rejected. If genuinely nothing was changed, say so, but reread the decision records against
> the code once it exists before believing it.

## 004. Interrogate the architecture before building

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> you must ask question to refine architecture and tech stack and methodology approach

**What it produced**

A round of questions on the interface, the component library, the working method, and the
scope extras, answered by the author. The answers became decisions A to E in entry 005 and
two new decision records,
[ADR-0006](decisions/0006-shadcn-ui-component-library.md) and
[ADR-0007](decisions/0007-api-first-openapi-contract.md).

This prompt is the reason the architecture was interrogated rather than assumed. Without it
the interface would have shipped as a two-field form and the contract would have been a
by-product of the implementation.

**Changes made to the output**

Accepted as produced.

## 005. Product decisions, and the API-first addendum

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture and documentation |
| **Author** | Intermediate agent brief, relaying Frédéric's answers |
| **Fidelity** | Condensed |

**Prompt**

> Product decisions, all from Frédéric. (A) The interface is a calculator keypad, not a
> two-field form: digits, decimal point, the four operators, equals, clear, the optional
> operations, and physical keyboard input. This invalidates the documented assumption that
> the context-sensitive percent was skipped because the brief describes no pending-operation
> state machine, since a keypad needs that state machine regardless. Replace it: the client
> holds an input state machine (operand buffer, pending operator, accumulated left operand,
> and a replace-on-next-digit flag), with chained equals and operator-after-operator named.
> Percentage stays the binary `a percent of b` and appears as a binary operator, not the
> context-sensitive postfix percent; document that as a named simplification with its reason.
> Critically, the state machine holds input state only: every evaluation is still one HTTP
> call for one binary operation, ADR-0003 is untouched, and the frontend still performs no
> arithmetic. Say so explicitly, because a reviewer seeing a keypad will wonder whether the
> client started computing.
>
> (B) Frontend component library: Mantine, chosen over Material UI and Chakra for TypeScript
> support, accessible defaults, and weight. New decision record: what it buys (accessible
> focus and keyboard interaction we would otherwise write and test ourselves, responsive
> primitives, theming), what it costs (a dependency, a bundle, and an evaluator now judging
> our composition rather than our CSS), and the rejected alternatives including hand-rolled
> CSS, which was the strongest counter-argument.
>
> (C) Methodology: test-driven development with atomic commits, since the public history is
> part of what an evaluator sees. Red, green, refactor, commit. Do not overclaim: describe it
> as the intended discipline, not a guarantee about every commit.
>
> (D) Scope: Docker Compose, GitHub Actions running tests and coverage on push, and all three
> optional operations, all accepted. Move Docker Compose from "optional" to in scope wherever
> the docs hedge.
>
> (E) Addendum, from Frédéric: "we will be api first design, frontend type will be generated
> from specs". This outranks C's framing. The OpenAPI document is the contract and the source
> of truth, not a by-product. Confront the honest difficulty rather than papering over it:
> FastAPI is code-first by default, deriving the specification from Pydantic models, which is
> the opposite of what was asked, and its generated `/openapi.json` does not make the project
> API-first on its own. What does: `openapi.yaml` committed at the root and authored first; a
> backend that implements it; a continuous integration check comparing FastAPI's generated
> document against the committed contract and failing on drift, which is the single most
> important element because it is what makes the contract enforced rather than aspirational;
> and frontend types generated from the committed contract with `openapi-typescript` plus
> `openapi-fetch`, committed, with a staleness check. Give it the weight of ADR-0002 and
> ADR-0004, with rejected alternatives including code-first with a generated spec (the
> strongest counter-argument on this budget), hand-written frontend types, and a full client
> generator.
>
> Then trim `architecture.md` to 1,200 to 1,500 words, keeping all diagrams, with the new
> material counting against that target.

**What it produced**

Two decision records ([ADR-0006](decisions/0006-shadcn-ui-component-library.md) and
[ADR-0007](decisions/0007-api-first-openapi-contract.md)), a rewritten architecture
document absorbing decisions A to E, a fifth Mermaid diagram showing the contract feeding
both layers with the continuous integration gates, and README revisions.

Two claims in the brief were checked against primary sources before being written down, and
one did not survive: `openapi-fetch` does document itself as "6 kb ... virtually zero
runtime", but Mantine does require a PostCSS build step
(`postcss-preset-mantine`, `postcss-simple-vars`), so the assumption that avoiding Tailwind
avoided extra build configuration was wrong. The decision record and the README state the
build step rather than repeating the assumption.

**Changes made to the output**

> **TODO** Fill in after review.

## 006. Drop Docker from development

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Infrastructure |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> ok then let's do not use docker for dev

**What it produced**

The removal of the container-based development environment that had just been specified.
Development became host-native through `just dev`, and Docker Compose was narrowed to two
jobs: the one-command assembled run and hosting the end-to-end smoke test. The bind mounts,
the anonymous `node_modules` volume and the rebuild-or-not table all disappeared with it.

It also forced a better answer on origins: with no container in development, the frontend
calls a same-origin relative path proxied to the backend in both paths, so the backend needs
no Cross-Origin Resource Sharing configuration at all. That is
[`architecture.md`](architecture.md) § 8.5, and it removes the problem rather than configuring
around it.

**Changes made to the output**

> **TODO** Fill in after review.

## 007. Reconsider the component library

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Frontend |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> let's use another frontend component frameworks

**What it produced**

Four options were put forward and shadcn/ui was chosen, replacing Mantine.
[ADR-0006](decisions/0006-shadcn-ui-component-library.md) was rewritten rather than amended,
because the argument changed shape: shadcn/ui generates component source into the repository
instead of importing it, which dissolves the concession the Mantine record had to make about an
evaluator judging our composition of a library rather than our own code.

**Changes made to the output**

> **TODO** Fill in after review.

## 008. Leave nothing assumed

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture |
| **Author** | Frédéric |
| **Fidelity** | Verbatim, including the original spelling |

**Prompt**

> anything else ? no assumption allowwed

**What it produced**

The open assumptions were put back to the author as questions rather than left documented as
guesses, and he ruled on each. Percentage semantics, precision and rounding, operand bounds,
coverage policy, and the licence stopped being assumptions and became decisions. The most
consequential ruling was that the API returns the exact value and rounding happens only at
display time, which created the boundary described in
[`architecture.md`](architecture.md) § 8.2.

This prompt is the reason [`architecture.md`](architecture.md) § 11.3 is now short: most of
what it used to hold has been decided.

**Changes made to the output**

> **TODO** Fill in after review.

## 009. Prefer the standard library

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> use python native library when possible

**What it produced**

A standing rule in [`../.claude/rules/principles.md`](../.claude/rules/principles.md), which
records that a dependency is knowledge borrowed from outside the repository and that the
standard library is reached for first. It reinforces
[ADR-0004](decisions/0004-exact-decimal-arithmetic.md), where `decimal.Decimal` was already
chosen partly because it ships with Python and needs no third-party fixed-point package.

**Changes made to the output**

> **TODO** Fill in after review.

## 010. Keep the prompt record inside the documentation

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Documentation |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> prompt saved in our arc42 doc

**What it produced**

This file. The record moved from a standalone `PROMPTS.md` at the repository root into the
documentation as an appendix to the collapsed arc42, and the root file was deleted.

Because sharing the prompts is an explicit deliverable, the move traded findability for
coherence, so the link discipline compensates: the README names it as a deliverable and links
it from both the documentation table and the design-decisions section, and
[`index.md`](index.md) lists it.

**Changes made to the output**

> **TODO** Fill in after review.
