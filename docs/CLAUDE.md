# Wiki Schema

<purpose>
Documentation layer for `sezzle-calculator`, a take-home technical assessment submitted to
Sezzle for the role "Software Engineer II with Accounting Experience (Brazil)".

Two audiences, in priority order:

1. **A Sezzle evaluator**, reading for a few minutes, deciding whether the author reasons
   well about trade-offs. This reader starts at the root `README.md` and follows links.
2. **An agent or a future maintainer**, needing to answer "why is it built this way?"
   without opening every file. This reader starts at `index.md`.

The documentation is itself a graded deliverable. It is sized to a 2 to 4 hour exercise:
dense enough to show engineering judgement, short enough to be read in full.
</purpose>

<structure>
- `raw/` (immutable sources; currently the transcribed assignment brief)
- `index.md` (catalog, the front door for agents)
- `log.md` (chronological record of documentation operations)
- `sources/` (one summary page per raw source)
- `architecture.md` (the entire structured layer: a deliberately collapsed arc42)
- `decisions/` (Architecture Decision Records, `NNNN-kebab-title.md`)

Outside `docs/`, the root carries:

- `README.md` (setup, run, Application Programming Interface examples, design decisions), a
  graded deliverable
- `LICENSE` (MIT)
- `13-prompt-record.md` (chronological record of prompts used, an explicit deliverable). It
  lives inside `docs/` but is a graded deliverable, so `README.md` must link it from both the
  documentation table and the design-decisions section. Never let those links rot.
</structure>

<arc42-binding>
The structured layer follows arc42, but **collapsed into the single file
`architecture.md`** rather than 12 section files. This is a deliberate scaling decision,
not an oversight: a calculator with two containers and no external systems would leave
most of the 12 files empty, and an evaluator on a time budget should not navigate a folder
of stubs.

The mapping from arc42 sections to this wiki:

| arc42 section | Where it lives here | Notes |
|---|---|---|
| 1 Introduction and Goals | `architecture.md` § 1 | Includes the requirement-to-implementation trace table |
| 2 Constraints | `architecture.md` § 2 | Technical, organizational, conventions |
| 3 Context and Scope | `architecture.md` § 3 | Container diagram only, see below |
| 4 Solution Strategy | `architecture.md` § 4 | Table of quality goal to approach to ADR |
| 5 Building Block View | `architecture.md` § 5 | Level 1 containers, Level 2 backend components |
| 6 Runtime View | `architecture.md` § 6 | One sequence diagram, success and error path |
| 7 Deployment View | `architecture.md` § 7 | Docker Compose topology |
| 8 Crosscutting Concepts | `architecture.md` § 8 | Numeric handling, error model, validation, testing |
| 9 Architecture Decisions | `decisions/` + index in `architecture.md` § 9 | Full rationale lives in the ADR files |
| 10 Quality Requirements | `architecture.md` § 10 | Tied to the assignment's grading axes |
| 11 Risks and Technical Debt | `architecture.md` § 11 | Two separate lists, plus open assumptions |
| 12 Glossary | Dropped | Every term was one a competent reviewer already knows. Acronyms are expanded inline on first use instead |

**Deliberate omissions**, all three recorded in the documents rather than left silent:

- **No C4 system context diagram.** One actor, zero external systems, so it would restate
  the container diagram with less information. Noted in `architecture.md` § 3.
- **No glossary.** Every candidate term is one a competent reviewer already knows. Acronyms
  are expanded inline on first use instead.
- **No stakeholder table.** One author and one evaluator, which is a sentence in § 1.

**Length ceiling on `architecture.md`: roughly 1,500 words.** A long architecture document
for a calculator reads as over-engineering, which is the one impression this submission
cannot afford. If a section needs to grow, cut another or move the content into an ADR.

Rules that still apply:

- **ADRs are separate files.** Never inline a decision's rationale into `architecture.md`.
  Section 9 is an index that links out.
- **Section 9 is generated from `decisions/`.** When an ADR is added or its status
  changes, regenerate the table rather than editing it independently.
- **Triage level is arc42 "essential plus lean".** Tables over prose, diagrams over walls
  of text, links over duplication. Do not add thorough-level content.
</arc42-binding>

<conventions>
- **Guiding principles.** [`../.claude/rules/principles.md`](../.claude/rules/principles.md)
  states DRY, KISS and separation of concerns as the compass, with a tie-break order. Do not
  paraphrase it into the documentation: that would itself duplicate knowledge. Link to it and
  state only the consequence specific to the document at hand.
- **Current-state documents are rewritten; chronological records are appended to and never
  revised.** `log.md` and `13-prompt-record.md` report what was true at a moment. When a decision
  is superseded, update every current-state document and leave those two alone, repointing only
  their link targets so nothing breaks. Rewriting them to match today would make them false.
- **Markdown only.** No AsciiDoc.
- **No em dashes in prose.** Use a period, comma, colon, or parentheses. This applies to
  every file in this repository, including the root `README.md`.
- **Expand every acronym on first use** within each file, with the short form in
  parentheses after it. Files are read individually, so "first use" resets per file.
- **Diagrams are Mermaid** in fenced code blocks. Never ASCII art. C4 diagrams use the
  `C4Container` / `C4Component` / `C4Deployment` directives; runtime flows use plain
  `sequenceDiagram` where C4 shapes add nothing. Validate at https://mermaid.live before
  committing.
- **Frontmatter** on every wiki page, in YAML: `summary` (one or two sentences, a plain
  factual claim, required, this is what an agent reads to decide whether to open the
  file), `tags`, `updated` (ISO date). ADRs additionally carry `number`, `title`,
  `status`, `date`, `supersedes`, `superseded_by`.
- **Links** are relative Markdown links. Every page must be reachable from `index.md`.
- **Citations**: a claim traceable to the assignment cites
  [`sources/assignment-brief.md`](sources/assignment-brief.md), which in turn points at
  the raw file. Do not cite `raw/` directly from a wiki page.
- **Placeholder marker**: content that cannot exist until the code does is marked with a
  blockquote at the start of a line, `> **TODO** ...`. Visible on purpose, so an unfilled
  placeholder is obvious in the rendered README rather than hidden in an HTML comment.
  Before submission the check in `<lint-workflow>` must return nothing.
</conventions>

<ingest-workflow>
Sources are rare in this repository (the assignment brief, plus any clarification received
from Sezzle). When one arrives:

1. Transcribe it into `raw/` if it is not already a file. Strip personal identifiers: this
   repository is public.
2. Read it fully and discuss 3 to 5 takeaways before writing.
3. Write or update `sources/<slug>.md`.
4. Update the affected parts of `architecture.md`, citing the source page.
5. If the source changes a decision, add or supersede an ADR. Never edit an accepted ADR's
   decision in place: supersede it, so the reasoning history survives.
6. Update `README.md` if the source changes a graded deliverable.
7. Update `index.md`, then append `## [YYYY-MM-DD] ingest | <source title>` to `log.md`.
</ingest-workflow>

<query-workflow>
1. Read `index.md`.
2. For "why" questions, read the relevant ADR first: that is where rationale lives.
3. For "how does it work" questions, read `architecture.md`.
4. Synthesize, citing pages inline.
5. Append `## [YYYY-MM-DD] query | <question>` to `log.md`.
</query-workflow>

<lint-workflow>
Both shell checks below are written to avoid matching their own text, so they can actually
reach zero. Do not "simplify" them back into a plain search for the literal marker: this
file would then always match itself and the check would be permanently red.

1. No placeholders remain (blocking before submission):
   `grep -rn '^> \*\*TODO\*\*' README.md docs/`
2. Every assignment deliverable in `sources/assignment-brief.md` maps to a README section
   and to a row in the trace table in `architecture.md` § 1.
3. Architecture Decision Record numbering is contiguous, no duplicates, no ADR left in
   `Proposed` at submission time.
4. Section 9 of `architecture.md` matches the contents of `decisions/`.
5. Every Mermaid block parses.
6. Every page is reachable from `index.md`.
7. No em dashes: `grep -rnP '\x{2014}' README.md docs/` returns nothing.
8. Append `## [YYYY-MM-DD] lint | <N findings>` to `log.md`.
</lint-workflow>

<domain-notes>
**Standing decisions, already settled. Document them, do not re-open them.**

- Frontend: React with TypeScript, built by Vite, components from shadcn/ui on Radix with
  Tailwind v4, generated into `src/components/ui/` and owned here rather than imported
  ([ADR-0006](decisions/0006-shadcn-ui-component-library.md)). Node 22.21. The interface is a
  calculator keypad, operable by tap and by physical keyboard. Its input state machine holds
  input state only: the frontend performs no arithmetic, and every evaluation is one HTTP
  request for one binary operation.
- Backend: Python with FastAPI, dependencies managed by `uv`.
- **API-first** ([ADR-0007](decisions/0007-api-first-openapi-contract.md)): `openapi.yaml` at
  the repository root is hand-authored and is the source of truth. The backend implements it;
  frontend types are generated from it. Continuous integration fails on drift. Never describe
  FastAPI's generated `/openapi.json` as making the project API-first: it is the comparison
  target, not the contract.
- **Everything wire-shaped is generated** ([ADR-0008](decisions/0008-generate-all-wire-types.md)):
  backend Pydantic models via `datamodel-code-generator`, frontend types, client and Zod
  schemas via Orval. Never document a hand-written request or response type. `openapi-typescript`
  and `openapi-fetch` were considered and dropped; do not reintroduce them.
- Toolchain ([ADR-0009](decisions/0009-toolchain.md)): `uv` and `pnpm` for packages, Ruff and
  Biome for lint and format, `ty` for Python types. Never write `npm`; it is `pnpm`, with
  `pnpm install --frozen-lockfile` and `pnpm-lock.yaml`.
- Working method: contract, then generated types, then tests, then implementation. The
  arithmetic engine is written test-first. Commits are one logical change each. Describe this
  as intended discipline, never as a guarantee about every commit.
- **Development is host-native.** `just dev` installs and runs both layers on the host, with no
  container and no build. Docker Compose is a separate recipe with two jobs only: the
  one-command assembled run, and hosting the single Playwright smoke test. Never describe
  Docker as the development environment.
- **Same-origin by construction.** The frontend calls a relative path, proxied to the backend in
  both paths. The backend has no Cross-Origin Resource Sharing configuration. Any text
  describing CORS headers on the backend is stale and wrong.
- All three "optional" operations are implemented. Continuous integration gates are listed once
  in `architecture.md` § 7.1; link there rather than restating them.
- The API path is `POST /api/calculate`. The `/api` prefix is what the proxies route on; never
  document a bare `/calculate`.
- Mantine was the component library and was replaced by shadcn/ui. Current-state documents say
  shadcn/ui; `log.md` and `13-prompt-record.md` are chronological records and keep the historical
  mention, since rewriting them would misrepresent what happened.
- **No `Co-Authored-By` trailers on commits, ever**, and no note about AI assistance in the
  README. Commits are authored by Frédéric alone; transparency about tooling is delivered
  through `13-prompt-record.md`, which is the graded channel for it.
- **Standard library first**, per
  [`../.claude/rules/principles.md`](../.claude/rules/principles.md). Link to that rule and
  state the local consequence; never paraphrase it into a document.
- **Rounding is display only.** The API returns the exact value; the frontend rounds to two
  decimal places for presentation. The keypad chains on the exact value, never on the rounded
  string. Any text implying the contract rounds is wrong.
- Coverage is reported, never gated. No blocking threshold anywhere.
- **The frontend holds no business rules; its role is to display data.** Validation comes from
  the generated Zod schemas, error wording from the backend's `message`, and arithmetic semantics
  from the backend. Never document a hand-written frontend check, a frontend error-string table,
  or a frontend rule about what an operation means. Display formatting (the two-decimal rounding)
  is presentation, not a rule, and is the one thing that legitimately lives there.
- `openapi.yaml`, `orval.config.ts` and the `justfile` are written by the author, not by this
  agent. Document, reference and diagram them; do not create them.
- The Python choice departs from the assignment's stated "Go is preferred". This is the
  single most likely thing an evaluator will challenge. It is argued head-on in
  [ADR-0002](decisions/0002-python-fastapi-instead-of-go.md) and surfaced in the README's
  design-decisions section rather than buried. Any future edit that softens or hides this
  deviation is a regression.
- `just` is the single source of truth for commands. Developers, continuous integration,
  and agents all invoke `just <recipe>`. Documentation must show `just` recipes as the
  primary invocation, with the raw underlying command shown only where it aids
  understanding.
- Docker and Docker Compose run the full stack.
- The repository is public. Never document a credential, a token, or the identity of
  individual Sezzle staff.

**Sizing rule.** Effort budget for the whole exercise is 2 to 4 hours. Before adding a
page, ask whether an evaluator reading for five minutes is better served by it. If not, do
not add it. Growth of this wiki is a smell, not progress.
</domain-notes>
