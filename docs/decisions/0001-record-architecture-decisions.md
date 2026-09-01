---
number: 1
title: Record architecture decisions
status: Accepted
date: 2026-09-01
supersedes: []
superseded_by: null
summary: Decisions with non-obvious rationale are recorded as numbered Architecture Decision Records so a reviewer can audit the reasoning without reverse-engineering it from the code.
tags: [process, adr]
updated: 2026-09-01
---

# ADR-0001: Record architecture decisions

## Context

This repository is a take-home assessment. The assignment asks for "design decisions and
assumptions" in the README, and grades on clarity and maintainability
([source](../sources/assignment-brief.md)).

A README section listing decisions works, but it flattens them: the reader gets the choice
without the alternatives, and without what the choice costs. For a submission whose whole
purpose is to demonstrate reasoning, the reasoning is the deliverable. It needs somewhere
to live that has room for it.

The exercise is capped at 2 to 4 hours, so the format has to be cheap to write.

## Decision

Record decisions that carry risk or need justification as Architecture Decision Records
(ADRs) in [`docs/decisions/`](.), one Markdown file per decision, numbered sequentially,
following the Nygard template extended toward Markdown Architectural Decision Records
(MADR) with an explicit "Alternatives considered" section.

The bar for writing one: a decision earns an ADR when a competent reviewer could
reasonably have chosen otherwise, or when the choice will be questioned. Routine choices
(a test-runner, a formatter, a directory name) do not get one.

The README's design-decisions section stays, but as a summary that links here. Full
rationale is never duplicated between the two.

## Consequences

### Positive

- The reviewer can audit reasoning directly, including what was rejected and why. Rejected
  alternatives are usually more informative about judgement than the accepted option.
- Each decision has a stable identifier that the architecture document and the README link
  to, so rationale is written once.
- Superseding rather than editing preserves the history of why a position changed.

### Negative

- Writing time that competes with implementation time, against a hard budget. Mitigated by
  keeping the count low: five ADRs, four of them substantive.

### Neutral

- Status workflow is `Proposed`, then `Accepted`, then `Deprecated` or `Superseded`. No
  ADR may remain `Proposed` at submission: an undecided decision is not a decision.
