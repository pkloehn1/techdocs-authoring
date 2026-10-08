# Templates and checklists

One copy-paste skeleton plus one reviewer checklist per core artifact. Each is
labeled with its Diataxis mode. The skeletons show structure; fill them in your
repo's voice and conventions. The last five entries cover short-form artifacts
that belong to no mode.

## README (how-to-shaped front door)

```markdown
# Project name

One line: what it is and why it exists.

## Requirements
## Installation
## Usage
## Configuration
## Contributing
## License
```

Checklist:

- Prerequisites are explicit.
- Install and usage commands are copy-paste-ready.
- Examples are runnable as written.

## How-to guide (how-to mode)

```markdown
# How to <accomplish the goal>

Goal: one line.

## Prerequisites
## Steps
1. ...
## Verification
How to confirm the goal was achieved.
## Troubleshooting
## Next steps
```

Checklist:

- Exactly one goal.
- Warnings appear before the step they apply to.
- A **Verification** step states how to confirm success.
- Troubleshooting is present; the page ends with a next step.

## Tutorial (tutorial mode)

```markdown
# Tutorial: <what you'll build/learn>

By the end you will have: <outcome promise>.

## Prerequisites
## Step 1 — ...
   Checkpoint: <how to confirm this step worked>
## Step 2 — ...
   Checkpoint: ...
## What you learned
## Next tutorial
```

Checklist:

- Reproducible by a beginner with no outside choices.
- No branching or "you could also" alternatives.
- Each step has a checkpoint; success is guaranteed if followed.

## Reference (reference mode)

```markdown
# <Component> reference

## <Endpoint / command / setting>
- Description
- Parameters: name, type, required/optional, default, constraints
- Example request / invocation
- Example response / output
- Errors / status codes
- Auth, versioning, rate limits, idempotency (as applicable)
```

- **Prefer generation** from source (OpenAPI, docstrings) to prevent drift.
- **Hand-authored fallback** (the common case): keep the same fields, and add a
  review step that re-checks the reference against the actual surface every
  release.

Checklist:

- Exhaustive and neutral; describes, never instructs.
- Every parameter and every error/status code is listed.

## ADR — Architecture Decision Record (explanation mode)

```markdown
# ADR-NNNN: <the decision>

- Status: proposed | accepted | deprecated | superseded-by ADR-MMMM
- Date: YYYY-MM-DD
- Deciders: <names/roles>

## Context
The forces and constraints at play.

## Decision
"We will ..."

## Consequences
Positive, negative, and neutral outcomes.
```

Checklist:

- Status, Date, and Deciders are filled.
- Immutable once accepted: supersede with a new ADR and cross-link
  (`superseded-by` / `supersedes`); never rewrite the decided record.
- Consequences include the negatives, not only the wins.

## Runbook (how-to mode, operational)

```markdown
# Runbook: <operation>

- Severity / when to run
- Required access

## 1. Prerequisites
## 2. Procedure
   2.1 ...
## 3. Verification
## 4. Rollback
## 5. Escalation / contacts
```

Checklist:

- Steps are ordered, unambiguous, and idempotent (safe to re-run; check state
  before changing it).
- Verification, Rollback, and Escalation sections are present.
- Numbered headings are sequential. Note: numbered-heading **enforcement** (a
  validator/linter) is your repository's, not this skill's — match your repo's
  convention.

## Release notes / changelog (reference mode)

```markdown
# Changelog

## [X.Y.Z] - YYYY-MM-DD
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

Checklist:

- Follows [Keep a Changelog](https://keepachangelog.com/) section order and
  [SemVer](https://semver.org/) version bumps.
- Written for the reader (what changed and the impact), not raw commit subjects.
- A **Deprecated** section warns before a future **Removed**.

## Code comment (no mode)

A code comment never explains the code. It supplies the purpose an uninformed
reader cannot derive from reading the code inline.

Adopt the canonical rule rather than invent one.
[Google's code-review guidance](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
states it: comments "explain why some code exists, and should not be explaining
what some code is doing", and "if the code isn't clear enough to explain
itself, then the code should be made simpler". It names one exception, and that
exception is real — a regular expression or a complex algorithm earns a comment
saying what it does.

A script's header comment is its README and takes that checklist.

```text
<The reason, constraint, hazard, or meaning the code cannot show>.
<Link to the decision or issue, if one exists>.
```

Checklist:

- Adds what the identifiers cannot say: a reason, a constraint, a hazard, or
  what a literal means. A paraphrase of the code is deleted.
- Explains or describes; it never instructs the reader to act outside the code.
  Describing the code in imperative voice is still description. A step the
  reader must take belongs in a how-to, or in code that enforces it.
- Matches the length and voice of the comments beside it.
- Links to the issue or decision instead of retelling it, and carries no dates
  or ticket history.
- Changes in the same commit as the code it describes.
- Is prose, not commented-out code; version control keeps the old code.

## Review comment (no mode)

```text
<Blocking | Optional>: <the change you want>.
Why: <the consequence, or a link to the rule>.
Suggestion: <a concrete alternative, if you have one>.
```

Checklist:

- Opens with the requested change; the reason follows.
- Marks itself blocking or optional.
- Raises one point, anchored to the line or symbol it concerns.
- Addresses the code, not the author.
- Links to the rule instead of restating it.
- Asks a question only when the answer changes the verdict.

The three bodies below share the ordering in
[Short, constrained formats](writing-process.md#short-constrained-formats):
bottom line, impact, next steps, details.

## Commit message (no mode)

```text
<type>(<scope>): <subject, imperative, no trailing period>

<Why the change exists, and what it costs.>
<Link to the issue.>
```

Checklist:

- Says in the body what the diff cannot show: why the change exists.
- States the cost or the trade accepted, not only the win.
- Carries no file list, no account of the session, and no dates or build
  numbers.
- Links the issue rather than restating it.
- Describes the change, never the author's process.

## Issue body (no mode)

```text
## Problem
<What is wrong, and the evidence for it.>

## Cost
<What it breaks or risks while it stands.>

## Proposed
<The change, or the decision being asked for.>

## Acceptance criteria
- [ ] <Checkable the day the issue closes.>
```

Checklist:

- Opens with the problem and its evidence, not with the fix.
- Every criterion is checkable the day the issue closes; work that lands later
  is a deliverable instead.
- Takes the destination's template sections when it has one, and invents none.
- Quotes the artifact it describes rather than paraphrasing intent.
- Links related issues instead of restating them.

## Change-request description (no mode)

```text
<The destination template's sections, in its order.>

<Summary: the state the branch is in.>
<Linked issues: the closing keyword, or a plain reference.>
```

Checklist:

- Takes the template's sections only; invents none.
- States the branch as it stands, not the order the work happened in.
- Derives the commit list from the repository rather than typing it.
- Claims to close an issue only when that issue's criteria are met; otherwise
  references it.
- Names what reviewers must check that the pipeline cannot.
