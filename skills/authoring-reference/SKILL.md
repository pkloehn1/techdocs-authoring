---
name: authoring-reference
description: >-
  Use when writing, structuring, or reviewing any README, how-to, tutorial,
  reference, ADR, runbook, release notes, or AI-agent-readable docs. Reference
  knowledge and an authoring playbook for technical documentation: picking a
  canonical style guide, the Diataxis four-mode model (tutorial/how-to/
  reference/explanation), copy-paste templates and reviewer checklists,
  single-sourcing and content reuse, a writing process that leads with the
  bottom line, and writing docs that serve both humans and AI agents.
license: MIT
compatibility: >-
  Vendor- and tool-neutral. Defaults to the Microsoft / Google / Apple style
  guides selected by audience, and assumes a docs-as-code workflow (Markdown in
  version control, reviewed by pull request). No linter or build tool is
  required to use it. This skill carries portable writing craft; your repository
  owns its own enforcement (line-length limits, heading-number validation,
  lint/CI wiring, repo paths).
metadata:
  author: pkloehn1
  version: "0.1.0"
allowed-tools: Read Grep Glob Bash(git:*) Bash(pre-commit:*) Bash(markdownlint:*) Bash(markdownlint-cli2:*) Bash(npx:*) Bash(vale:*) WebFetch WebSearch
---

# Documentation authoring reference

Reference and playbook for writing and reviewing technical documentation. This
file is the index; load a reference file only when a task needs it (progressive
disclosure).

- Pick a canonical style guide and the highest-agreement mechanical rules
  (voice, mechanics, screenshots/media) → [references/style-guide.md](references/style-guide.md)
- The Diataxis four-mode model and how to choose one mode per page
  → [references/doc-types-and-diataxis.md](references/doc-types-and-diataxis.md)
- Copy-paste section skeletons + reviewer checklists for the seven core
  artifacts (README, how-to, tutorial, reference, ADR, runbook, release notes)
  → [references/templates-and-checklists.md](references/templates-and-checklists.md)
- When and how to reuse content (single-sourcing, DITA tiers, change-impact)
  → [references/single-sourcing-and-reuse.md](references/single-sourcing-and-reuse.md)
- The authoring pipeline — outline, draft, then a separate editing pass
  → [references/writing-process.md](references/writing-process.md)
- Writing docs that serve both humans and AI agents
  → [references/docs-for-humans-and-agents.md](references/docs-for-humans-and-agents.md)

## Operating principles

1. **Name the audience and the single goal first.** Decide who reads this and
   what they must be able to do afterward before writing a sentence.
2. **Lead with the bottom line.** Open with the outcome, recommendation, or
   required action; put warnings before background.
3. **One Diataxis mode per page.** Each doc is a tutorial, how-to, reference, or
   explanation — never a blend. Split a doc that mixes modes.
4. **Adopt, don't invent, a style guide.** Pick one canonical guide by audience;
   extend it with a thin local layer; never blend two guides mid-document.
5. **Structure before prose.** Fix layout, headings, and task flow first; edit
   for clarity, conciseness, and correctness in a separate pass.
6. **Reuse with intention.** Single-source only when multiple outputs or
   audiences justify it; otherwise stay linear. Link to one authoritative
   source rather than copy.
7. **Verify by use.** A doc is done when someone who did not write it can
   complete the task; tie factual claims to evidence.

## Universal invariants

These are the canonical rules. Other files and the `technical-writer` agent
reference this list rather than restating it.

- **Modes never mix in one page.** A tutorial that drifts into reference tables
  or background theory is two documents; reviewers reject cross-quadrant
  content.
- **Reference describes; it never instructs or explains.** How-tos and tutorials
  instruct; explanation gives the "why." Keep them apart.
- **Every how-to and runbook ships a verification step** — how to confirm the
  goal was achieved — and every runbook also ships rollback and escalation.
- **ADRs are immutable once accepted.** You supersede an ADR with a new one and
  cross-link them; you do not edit the decided record.
- **Cross-guide-safe defaults:** second person, active voice, present tense,
  sentence-case headings, the serial comma, descriptive link text (never "click
  here").
- **Don't duplicate; link.** One authoritative location per fact or procedure;
  no version-suffixed copies (`-v2`, `-new`, `-legacy`).

## Boundary: craft vs. repo enforcement

This skill carries portable writing **craft**. Your repository owns its
**enforcement** — line-length limits (e.g. an MD013 character cap), numbered-
heading validation, diagram linting, pre-commit / CI lint wiring, and the actual
repo paths. Follow your repo's enforced limits where they exist; this skill
defers the numbers and the tooling to it and never restates them. Where a
mechanical rule here overlaps a craft principle your repo already adopted
(Strunk-style economy, a grade-9 readability target, single-source-of-truth),
treat them as the same shared baseline, not competing rulesets.

## Quick entry point

Starting or reviewing a doc:

1. **Classify.** Name the audience, the single goal, and the Diataxis mode.
2. **Template.** Pull the matching skeleton + reviewer checklist from
   [references/templates-and-checklists.md](references/templates-and-checklists.md).
3. **Draft, then edit.** Outline and draft; then run the editing pass (clarity,
   conciseness, correctness) from
   [references/writing-process.md](references/writing-process.md) as a separate
   step.
4. **Verify.** Run the project's Markdown linters (`pre-commit`, `markdownlint`,
   or `vale`) to catch line-length and other findings, then confirm the reader
   can complete the task, every link resolves, and the page holds exactly one
   mode.
