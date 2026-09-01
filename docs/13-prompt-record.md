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

**Two kinds of prompt.** Most entries are free-text messages the author sent unprompted. A few
are answers he typed into a structured multiple-choice question, as custom text rather than as a
chosen option, and each of those names the question it was answering. Without that a reader would
meet an answer as though it were a spontaneous instruction and could not tell what it responded
to. Decisions he took by selecting an offered option are recorded in
[`log.md`](log.md) rather than here, since a list of option labels would bury the messages that
are genuinely his words.

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

Two of the decisions recorded here were the author's, taken against a recommendation. Go was
recommended for the backend and he chose Python, which is the departure
[ADR-0002](decisions/0002-python-fastapi-instead-of-go.md) exists to argue. Removing the
verbatim assignment brief from this public repository was also recommended; he heard the concern
and kept it, which is why it is still in [`raw/`](raw/).

The scaffolding itself was accepted as produced.

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

The component library was the author's call against a recommendation: hand-rolled styles were
recommended and he chose a library.

One factual error in the brief was caught rather than carried through. Mantine was justified
partly on avoiding an extra build step, but its documented setup requires
`postcss-preset-mantine` and `postcss-simple-vars`, so the objection being raised against
Tailwind applied to Mantine as well. The decision record stated the build step instead of
repeating the assumption.

The word ceiling this brief set on `architecture.md` was wrong from the start, having been fixed
without subtracting the Mermaid source that the same brief had frozen. It was contested three
times with the arithmetic before being retired and replaced by a rule. Separately, a costed menu
of five cuts was declined in full, and one item, the § 9 decision table, was later reinstated
once [`../.claude/rules/principles.md`](../.claude/rules/principles.md) existed and made that
duplication a rule violation rather than a matter of taste.

## 006. API-first, with frontend types generated from the specification

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> for example we will be api first design , frontend type will be generated from specs

**What it produced**

[ADR-0007](decisions/0007-api-first-openapi-contract.md). `openapi.yaml` became the contract and
the source of truth, authored before either layer existed.

The record had to confront a difficulty rather than paper over it: FastAPI works the other way
round by default, deriving the document from Pydantic models, and publishing `/openapi.json` does
not make a project API-first. A specification generated from the code agrees with the code by
construction, so it can never catch a mistake. The continuous integration check that compares the
generated document against the committed contract and fails on drift is what makes the contract
enforceable rather than merely declared.

**Changes made to the output**

No changes. The output was accepted as produced.

## 007. Every type generated from the contract

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> all types must be generated from openapi (this also allow to changes prog languages easily)

**What it produced**

[ADR-0008](decisions/0008-generate-all-wire-types.md). No type describing the wire format is
hand-written on either side: Pydantic models from `datamodel-code-generator`, and the frontend's
types, client and Zod schemas from Orval.

The parenthetical is the load-bearing part and it is drawn out rather than left implicit. Because
both sides are generated from one contract, the implementation language becomes an exchangeable
detail, which is the strongest available answer to the objection that this should have been
written in Go: a Go port regenerates its own types from the same file and reimplements the
arithmetic engine, while the contract, the frontend and the contract tests are untouched. A
cross-reference was added to [ADR-0002](decisions/0002-python-fastapi-instead-of-go.md) saying
so, without softening its statement that the submission still shows no Go.

**Changes made to the output**

Writing the contract later surfaced a real error. Long justifications had been written into the
schema descriptions, and Orval inlines every description verbatim into the generated Zod file, so
the reasoning was being duplicated into generated output. The descriptions are now terse and
point at the decision records instead. It was found by running both generators against the
contract rather than assuming they would cope, which also confirmed that `prefixItems` survives
as `tuple[Operand, Exponent]` in Pydantic and `zod.tuple([...])` in Zod.

## 008. Toolchain

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Infrastructure |
| **Author** | Frédéric |
| **Fidelity** | Verbatim, including the original wording |

**Prompt**

> we will use use Orval and zod, biome and ty

**What it produced**

[ADR-0009](decisions/0009-toolchain.md), and the frontend half of
[ADR-0008](decisions/0008-generate-all-wire-types.md). Orval replaced `openapi-typescript` and
`openapi-fetch`, generating the types, a typed client and Zod schemas from the same contract.
Biome replaced the conventional ESLint and Prettier pair. `ty` became the Python type checker
alongside `uv` and Ruff.

The Zod part changed the architecture rather than the tooling. Generated TypeScript types are
erased at build time, so runtime validation at the boundary is what turns the contract from a
compile-time convention into something a violating backend cannot slip past unnoticed.

**Changes made to the output**

`ty` is in beta, and the continuous integration step that runs it was deliberately made
non-blocking so that a beta regression cannot turn this public repository red while an evaluator
is looking at it. Tests, coverage, the contract drift check and the generated-artefact freshness
checks all continue to block. That is a decision shaped by the submission's context rather than
by engineering preference alone, and the record says so rather than presenting a non-blocking
type check as ordinary practice.

## 009. DRY, KISS and separation of concerns as the compass

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Process |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> DRY, KISS and separation of concern are the compass (add to .claude/rules in the projects

**What it produced**

[`../.claude/rules/principles.md`](../.claude/rules/principles.md), stating the three principles
with a tie-break order for when they conflict and a rule about which decisions earn a record. The
documentation links to it and never paraphrases it, since restating its content would be the
duplication it names.

It later settled a question that had until then been a matter of taste. Section 9 of
[`architecture.md`](architecture.md) held a table of decision records that
[`index.md`](index.md) already carried with better descriptions. Once this file existed that was
a rule violation rather than a preference, and the table became a pointer.

**Changes made to the output**

No changes. The output was accepted as produced.

## 010. Package managers, and the justfile as environment setup

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Infrastructure |
| **Author** | Frédéric |
| **Fidelity** | Verbatim, including the original wording |

**Prompt**

> uv tu manage python package, pnpm for frontend, justfiles to setup dev env

The third word reads as "to".

**What it produced**

`pnpm` replaced npm throughout, recorded in [ADR-0009](decisions/0009-toolchain.md) as a routine
choice rather than an argued one, since a reviewer would not reasonably contest it.

The more consequential half was the framing of `just`: not a table of command aliases but how the
environment is provisioned. A developer, continuous integration and an agent all enter through the
same recipes, so there is no second, undocumented way to build or test the project.

**Changes made to the output**

No changes. The output was accepted as produced.

## 011. One command to set up and run everything

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Infrastructure |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> `just dev` in the repo setup all, package installation, docker build and run  (docker compose)

**What it produced**

`just dev` as the single documented entry point, taking a clean clone to a running application. At
this point that meant installing both layers, building the images and starting the stack through
Docker Compose.

**Changes made to the output**

Superseded two prompts later by entry 013, which removed Docker from development entirely. Nothing
of this shape reached the repository: the Compose-based development arrangement was never written,
so there were no bind mounts, no anonymous `node_modules` volume and no rebuild-or-not table to
delete afterwards. The design was narrowed before it was built rather than accumulated and then
cut back.

## 012. Would every code change rebuild the image?

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Infrastructure |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> I don't want to rebuild the docker images everytimes a changes a line of code. I guess i will use docker to run e2e tests locally, or dev in the container if possible ? enlight me in this decision

This is a question rather than an instruction, and the record treats it as one.

**What it produced**

The premise was corrected. Bind mounts mean a code change never triggers a rebuild, because the
container reads the file from the host; only a dependency manifest, a lockfile or a Dockerfile
does. On this project that is a handful of times in total. A development container was recommended
against under KISS: one author, on Linux, with `uv` and `pnpm` already providing isolation, so it
would add a file to explain and a layer between editor and code for a benefit that needs a team to
be worth anything.

**Changes made to the output**

The decision that followed was the author's own, not an instruction he was given. Having heard the
correction, he chose to drop Docker from development altogether (entry 013), which nobody had
proposed.

## 013. Drop Docker from development

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Infrastructure |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> ok then let's do not use docker for dev

**What it produced**

This supersedes entry 011, and it did so before anything was written. Development became
host-native through `just dev`, with no container involved and nothing built, and Docker Compose
was narrowed to two jobs: the one-command assembled run and hosting the end-to-end smoke test.
The bind mounts, the anonymous `node_modules` volume and the rebuild-or-not table that entry 011
would have required were therefore never authored, only ever discussed.

It also forced a better answer on origins: with no container in development, the frontend
calls a same-origin relative path proxied to the backend in both paths, so the backend needs
no Cross-Origin Resource Sharing configuration at all. That is
[`architecture.md`](architecture.md) § 8.5, and it removes the problem rather than configuring
around it.

**Changes made to the output**

No changes. The output was accepted as produced.

## 014. Reconsider the component library

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Frontend |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> let's use another frontend compononent frameworks

**What it produced**

Four options were put forward and shadcn/ui was chosen, replacing Mantine.
[ADR-0006](decisions/0006-shadcn-ui-component-library.md) was rewritten rather than amended,
because the argument changed shape: shadcn/ui generates component source into the repository
instead of importing it, which dissolves the concession the Mantine record had to make about an
evaluator judging our composition of a library rather than our own code.

**Changes made to the output**

Mantine had been proposed and the author asked for a different framework, so this entry records
an override rather than a refinement.

One instruction was declined. Every mention of Mantine anywhere was to become shadcn/ui;
`log.md` and this file were left historical instead, on the grounds that a chronological record
saying shadcn/ui was chosen before it was chosen is simply false. The refusal was endorsed and
became a standing rule for the repository: current-state documents are rewritten, chronological
records are appended to and never revised.

Two smaller corrections. The `/api` path prefix was chosen after the documents were written and
applied across eighteen references. And the instruction to research the current tooling rather
than write from recollection is why
[ADR-0006](decisions/0006-shadcn-ui-component-library.md) describes Tailwind v4 with the Vite
plugin rather than the older PostCSS arrangement.

## 015. Leave nothing assumed

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

This is where the author corrected a design error that would otherwise have gone through.
Rounding inside the contract and rounding at display time were put to him as alternatives with
their consequences: contract rounding would make `1/8` return `0.12`, `sqrt(2)` return `1.41`,
and `1/3` then times three return `0.99`. He chose display-only rounding. Had he chosen
otherwise, the exactness argument that
[ADR-0004](decisions/0004-exact-decimal-arithmetic.md) rests on would have been undermined by
the submission's own rounding policy.

## 016. Prefer the standard library

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture |
| **Author** | Frédéric |
| **Fidelity** | Verbatim, typed as a custom answer |
| **Answering** | A structured question asking how `percent(a, b)` should be defined |

**Prompt**

> use python native library when possible

**What it produced**

An honest oddity worth recording: it did not answer the question it was given. The Python
standard library has no notion of percentage, so the semantics of `percent(a, b)` remained open
and had to be put to him again before they were settled. What it did settle was something broader
that nobody had asked about.

A standing rule in [`../.claude/rules/principles.md`](../.claude/rules/principles.md), which
records that a dependency is knowledge borrowed from outside the repository and that the
standard library is reached for first. It reinforces
[ADR-0004](decisions/0004-exact-decimal-arithmetic.md), where `decimal.Decimal` was already
chosen partly because it ships with Python and needs no third-party fixed-point package.

**Changes made to the output**

No changes. The output was accepted as produced.

## 017. Keep the prompt record inside the documentation

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Documentation |
| **Author** | Frédéric |
| **Fidelity** | Verbatim, typed as a custom answer |
| **Answering** | A structured question on how visible artificial intelligence assistance should be in the public commit history, offering a root-level prompt record only, `Co-Authored-By` on every commit, or trailers where genuinely applicable |

**Prompt**

> prompt saved in our arc42 doc

**What it produced**

The answer took none of the three options and relocated the record instead, which is why this
file lives in `docs/` and why no commit in this repository carries a `Co-Authored-By` trailer:
transparency about tooling is delivered here, in the channel the assignment actually grades.

This file. The record moved from a standalone `PROMPTS.md` at the repository root into the
documentation as an appendix to the collapsed arc42, and the root file was deleted.

Because sharing the prompts is an explicit deliverable, the move traded findability for
coherence, so the link discipline compensates: the README names it as a deliverable and links
it from both the documentation table and the design-decisions section, and
[`index.md`](index.md) lists it.

**Changes made to the output**

No changes. The output was accepted as produced.

## 018. The frontend holds no business rules

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Architecture |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> frontend do not contain business rules, the roles of the frontend is to display data

**What it produced**

A constraint in [`architecture.md`](architecture.md) § 2 rather than a crosscutting concern, since
it governs what the frontend may contain and not merely how it is built. Three consequences were
derived from it rather than decided separately: validation rules reach the frontend as Zod schemas
generated from the contract and are never hand-written; error text comes from the response rather
than a table in the client; and the frontend decides no arithmetic semantics, so pressing equals
twice does nothing, because repeat-on-equals is a rule about what an operation means when
reapplied and neither layer may hold it.

It also required answering, in § 8.2, why the two-decimal display rounding is not a violation of
the constraint it sits next to: a business rule changes what the answer is, a formatting choice
changes only how it is shown.

**Changes made to the output**

No changes. The output was accepted as produced.

## 019. Atomic commits, grouped by logic

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Phase** | Process |
| **Author** | Frédéric |
| **Fidelity** | Verbatim |

**Prompt**

> atomic commit and grouped by logic (test, doc and code that are related belong to the same commit)

**What it produced**

The working method in [`architecture.md`](architecture.md) § 4 already said commits stay one
logical change each. This made the grouping explicit: related code, tests and documentation belong
in the same commit rather than being split into separate commits by file type.

**Changes made to the output**

It changed how the contract was committed. `openapi.yaml` went in together with the architecture
section it settles, rather than as a separate documentation commit afterwards.
