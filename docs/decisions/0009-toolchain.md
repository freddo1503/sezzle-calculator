---
number: 9
title: Toolchain, uv and pnpm, Ruff and Biome, and ty as a non-blocking type check
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: One tool per job per layer (uv and pnpm for packages, Ruff and Biome for lint and format, ty for Python type checking), with ty's pre-1.0 status accepted by making its continuous integration step non-blocking so a beta regression cannot redden a public repository.
tags: [tooling, ci, lint, types]
updated: 2026-09-01
---

# ADR-0009: Toolchain, uv and pnpm, Ruff and Biome, and `ty` as a non-blocking type check

## Context

The toolchain has to be defensible in a public repository an evaluator will open, and cheap
to operate inside a 2 to 4 hour budget. Most of these choices are routine and would not be
contested. One is not, and it is the reason this record exists rather than a line in a README.

Two standing conventions apply. Commands live only in the `justfile`, so a developer,
continuous integration, and an agent all run the same recipes (the DRY rule for commands, see
[`.claude/rules/principles.md`](../../.claude/rules/principles.md)). And **versions are not
pinned**, by the author's standing convention. That second one is what turns a tool's maturity
into a live risk rather than a footnote.

## Decision

One tool per job, per layer.

| Job | Backend | Frontend |
|---|---|---|
| Packages and environment | `uv` | `pnpm` |
| Lint and format | Ruff | Biome |
| Type checking | `ty` | The TypeScript compiler |

**Biome** replaces the conventional ESLint and Prettier pair: one tool, one configuration
file, one pass, covering both linting and formatting. Ruff plays the same role on the backend.
Choosing a single tool per job on each side keeps the pipeline short and the configuration
surface small.

**`pnpm`** replaces npm, with `pnpm install --frozen-lockfile` and a `pnpm-lock.yaml`
lockfile. A routine choice, recorded here for completeness rather than argued.

Biome coexists with the Tailwind that [ADR-0006](0006-shadcn-ui-component-library.md) brings
in. Automatic class-name sorting is deliberately not configured: it is machinery this budget
does not justify.

### `ty`, and the risk that comes with it

[`ty`](https://docs.astral.sh/ty/) is Astral's Python type checker, from the makers of `uv`
and Ruff, documented as 10 to 100 times faster than mypy and Pyright. It fits a toolchain
already built on Astral tools, and the Pydantic v2 models here need none of the plugins whose
absence blocks `ty` on other projects.

**It is also pre-1.0, currently on a 0.0.x version line, and is not presented as settled
here.** Combined with the no-pinning convention, that produces a specific and quite plausible
failure: a breaking release between submission and evaluation turns continuous integration red
on a public repository while an evaluator is looking at it. A red pipeline is a far worse
signal than a slower type checker.

**The mitigation, and its reason:** the `ty` step in continuous integration is
**non-blocking**. Tests, coverage, the OpenAPI drift check, both generated-artefact freshness
checks, and the end-to-end smoke test all remain blocking. Type errors still appear in the job
output and locally through `just`, where they are useful.

This is not the usual practice of letting an unimportant check advise rather than gate. Type
checking matters. The step is non-blocking specifically because the tool is pre-1.0 and
unpinned, so the failure mode being defended against is the tool breaking, not the code being
wrong. If `ty` reaches a stable release, the honest follow-up is to make the step blocking and
supersede this record.

## Alternatives considered

- **mypy**, the mature default. The strongest counter-argument: stable, universally
  understood, and no pre-1.0 risk. Rejected on toolchain coherence and speed, with the
  non-blocking step as the concession that keeps the risk survivable. This is the closest call
  in this record.
- **Pyright.** Mature and stronger on typing-specification conformance than `ty` currently is.
  Rejected for the same coherence reason, and it brings a Node dependency into the backend.
- **ESLint plus Prettier.** The conventional pair. Two tools, two configurations, and a known
  interaction problem between linting and formatting that Biome avoids by doing both.
- **npm or Yarn.** No meaningful difference at this size; `pnpm` was already available.
- **Pinning versions** to eliminate the `ty` risk directly. Rejected because it contradicts a
  standing convention for the sake of one tool, and the non-blocking step addresses the same
  risk without a repository-wide exception.

## Consequences

### Positive

- One tool per job per layer, so a short pipeline and little configuration.
- A fast type checker whose failure cannot redden the repository.
- Toolchain coherence: `uv`, Ruff, and `ty` share maintainers and conventions.

### Negative

- **A type regression can merge**, because the step does not gate. Accepted: type errors are
  visible in the job output and locally, and the blocking gates cover correctness.
- **`ty` is pre-1.0**, so its behaviour may change under the project without warning.
- **Biome and `ty` are both less familiar** than the tools they replace, so a reviewer may
  have to look them up.

### Neutral

- Every tool is invoked through a `just` recipe, so swapping one changes the recipe and
  nothing else.
