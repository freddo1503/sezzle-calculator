---
summary: Append-only chronological record of documentation operations on this repository, one entry per init, ingest, query, or lint pass.
tags: [log]
updated: 2026-09-01
---

# Log

Append-only. Newest entries at the bottom.

Tail recent entries with:

```bash
grep "^## \[" docs/log.md | tail -5
```

## [2026-09-01] init | Documentation layer bootstrapped

Scaffolded the documentation layer for an empty repository, ahead of any code.

Created: `docs/CLAUDE.md` (schema), `docs/index.md`, `docs/log.md`,
`docs/architecture.md`, five ADRs in `docs/decisions/`, `docs/sources/assignment-brief.md`,
and the root deliverables `README.md` and `PROMPTS.md`.

Structural decision: arc42 collapsed into the single file `architecture.md` rather than 12
section files, and the C4 system context diagram omitted, both on proportionality grounds
for a 2 to 4 hour exercise. Both are recorded in `CLAUDE.md` and `architecture.md` § 3
rather than left silent.

## [2026-09-01] ingest | Take-Home Assignment Brief

Source: `raw/2026-08-27-assignment-brief.md`, transcribed from the assignment email of
2026-08-27 with sender and recipient identities stripped, since the repository is public.

Wrote `sources/assignment-brief.md` with the deliverables checklist and three ambiguities
(the meaning of "percentage", the absence of any precision requirement, and the loose use
of "microservice"). All three are carried into `architecture.md` § 11.3 as documented
assumptions.

Produced four substantive ADRs from the brief: the Python and FastAPI departure from the
preferred Go (0002), the single-endpoint API shape (0003), exact decimal arithmetic with
string transport (0004), and the error model with its status-code mapping (0005).

No contradictions found: this is the first source, so there is nothing yet to contradict.

## [2026-09-01] ingest | Product decisions A to E

Five product decisions taken by the author after a round of architecture questions, plus an
API-first addendum that reframed the working method.

Two new ADRs: [0006](decisions/0006-shadcn-ui-component-library.md) (Mantine over hand-rolled
styling) and [0007](decisions/0007-api-first-openapi-contract.md) (hand-authored
`openapi.yaml` as the source of truth, generated frontend types, drift check in continuous
integration). ADR-0003 gained a cross-reference line; its decision is unchanged.

One contradiction resolved, not silently overwritten: the § 11.3 assumption previously
justified skipping the context-sensitive percent on the grounds that the brief describes no
pending-operation state machine. A keypad requires that state machine regardless, so the
premise was void. The assumption is rewritten to keep percentage as a binary operator, now
justified by predictability and testability rather than by a false premise.

Also corrected: the incoming brief asserted that avoiding Tailwind meant no extra build step.
Mantine's documented setup requires PostCSS configuration, so ADR-0006 and the README record
the build step instead.

`architecture.md` cut from 3,553 words to its current size while absorbing all of decisions
A to E and a fifth diagram. The 1,200 to 1,500 word target was not reached; the shortfall and
a costed menu of further cuts were reported rather than resolved unilaterally.

## [2026-09-01] ingest | Decisions F to K

Generation, tooling, package managers and the development environment.

Two new ADRs: [0008](decisions/0008-generate-all-wire-types.md), every wire type generated
from the contract on both sides with Zod validating responses at runtime, and
[0009](decisions/0009-toolchain.md), the toolchain with `ty` non-blocking because it is
pre-1.0 and versions are unpinned. ADR-0002 and ADR-0007 gained cross-references; neither
decision changed.

Superseded within this batch, applied as final state rather than in sequence: decision F's
`openapi-typescript` and `openapi-fetch` were replaced by Orval before anything shipped, and
decisions I and J's Docker-based development environment was replaced by K's host-native
`just dev`. The bind mounts, the anonymous `node_modules` volume and the rebuild table were
therefore never written.

Contradictions resolved: § 8.5 documented Cross-Origin Resource Sharing on the backend, which
decision K makes wrong rather than merely dated, so it was replaced by same-origin proxying;
the § 2 constraint row that pointed at it was corrected; a README placeholder asked for the
frontend's API base URL, which no longer exists; and the technical-debt list claimed all
end-to-end testing was out of scope, which the one Playwright smoke test makes false.

`architecture.md` finished at 2,769 words against a 2,600 ceiling. Reported with a costed menu
rather than resolved by cutting mandated content.

## [2026-09-01] ingest | Decision L, shadcn/ui replaces Mantine, and the /api path prefix

ADR-0006 rewritten rather than amended, and its file renamed from
`0006-mantine-component-library.md` to `0006-shadcn-ui-component-library.md`. The decision is
now shadcn/ui on Radix primitives with Tailwind v4, generated into `src/components/ui/` and
owned by this repository.

The argument changed shape, not just the tool. The Mantine record had to concede that an
evaluator judges our composition of a library rather than our own code; because shadcn/ui
copies component source into the repository, that concession disappears and becomes the
centre of the new record. Mantine moves into the rejected-alternatives list.

Three costs recorded rather than glossed: Tailwind returns to the stack after being rejected
earlier, which is named as a reversal; `pnpm dlx shadcn add` is a generation step outside the
`just` recipes, resolved honestly as a one-time authoring action rather than part of the
build; and more configuration files are touched.

The API path gains an `/api` prefix throughout: `POST /api/calculate`, which is what the Vite
development server and the static file server route on under decision K's same-origin proxy.

Mantine survives deliberately in this log and in `PROMPTS.md`. Both are chronological records,
and editing them to say shadcn/ui would misrepresent what was decided when. Every other
document states the current decision only.

## [2026-09-01] ingest | Decision M, open assumptions closed

The author ruled on every open assumption, so most of § 11.3 became decisions and left the
table. Percentage semantics (`percent(a, b) = a / 100 * b`) and the operand bound moved to the
contract description in § 3.2, and precision moved to § 8.2.

The consequential ruling is precision. Arithmetic keeps full `decimal` precision end to end,
the API returns the exact value, and rounding to two decimal places happens at display time
only. Rounding inside the contract was put to the author with its consequences (`1/8` becoming
`0.12`, `sqrt(2)` becoming `1.41`, `1/3` then times three becoming `0.99`) and rejected on
exactly those grounds.

That creates a boundary worth naming: the input state machine chains on the exact value the
API returned, never on the rounded string displayed. Recorded in § 8.2 and
[ADR-0004](decisions/0004-exact-decimal-arithmetic.md), with a new quality scenario Q6 covering
it, since it is the only scenario that would catch the boundary leaking.

Also: coverage is reported and never gated; an MIT `LICENSE` was added; and the prompt record
moved from the root `PROMPTS.md` into `13-prompt-record.md` as an appendix to the collapsed
arc42, numbered 13 because arc42 runs to 12 and section 12 was deliberately dropped. Five
tier-one prompts were appended verbatim, including one with an original spelling error kept
intact, since verbatim means verbatim.

## [2026-09-01] ingest | Decision N, the frontend holds no business rules

Added to § 2 as a constraint rather than a crosscutting concern, since it governs what the
frontend may contain. Three consequences derived from it rather than decided separately:
validation comes from the contract's generated Zod schemas, error wording comes from the
backend's `message`, and arithmetic semantics stay out of the client entirely.

The concrete case that settles: pressing equals twice does nothing. Repeat-on-equals is a rule
about what an operation means when reapplied, which the constraint forbids in the frontend, and
the backend cannot hold it without session state that
[ADR-0003](decisions/0003-single-calculate-endpoint.md) rules out. The behaviour is absent
rather than misplaced.

Contradictions resolved: § 5.3 named "chained equals" as a case to handle, which the ruling
inverts; ADR-0005 said the frontend maps `code` to a localised message, and now the backend owns
the wording; § 11.2 justified having no internationalisation on the basis that the frontend
could translate later, which is no longer its to do; and the README told clients to branch on
`code` and never read `message`, when they must render `message` and branch on `code` only for
behaviour.

The rounding from decision M was addressed head on in § 8.2 rather than left to look like a
violation: a business rule changes what the answer is, a formatting choice changes only how it
is shown, and the chaining rule is the mechanism that keeps them apart.

New quality scenario Q7 asserts the property the constraint buys: an operation added to
`openapi.yaml` reaches the frontend with no hand-written frontend change.

Section 9 was cut to a pointer at `index.md` per the DRY rule, and the ceiling was raised to
2,800 words.

## [2026-09-01] lint | Assumptions table reduced to what is genuinely undecided

Applied the generalised rule that a decided assumption is no longer an assumption, to every row
of § 11.3 rather than to percentage alone.

Moved out, to where a reader meets them as properties of the system: percentage semantics,
operand bounds and the negative-base fractional-exponent rule to § 3.2, and precision with
display-only rounding to § 8.2. The same reduction was applied to the README's assumptions
table and to the open-questions list in `sources/assignment-brief.md`.

One row remains, and deliberately so: the reading of "microservice" as a single backend process.
Nobody ruled on it, it is an interpretation of the brief's wording rather than a decision about
the system, and being wrong about it would change nothing that was built.

The word ceiling on `architecture.md` was retired in favour of a rule: every paragraph earns its
place, duplication is the only automatic cut, and the count is reported for information.
