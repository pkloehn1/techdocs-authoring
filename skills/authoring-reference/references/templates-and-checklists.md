# Templates and checklists

One copy-paste skeleton plus one reviewer checklist per core artifact. Each is
labeled with its Diataxis mode. The skeletons show structure; fill them in your
repo's voice and conventions. The last two entries cover short-form artifacts
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

A code comment sits beside the code it explains, so the code is the context.
Say only what the code cannot.

```text
<The constraint, reason, or hazard the code cannot show>.
<Link to the decision or issue, if one exists>.
```

Checklist:

- States why, never what; the identifiers already say what.
- Does one job: explain a reason, or describe an interface. A comment that
  also instructs the caller is two comments.
- Matches the length and voice of the comments beside it.
- Links to the issue or decision instead of retelling it, and carries no dates
  or ticket history.
- Changes in the same commit as the code it describes.
- Deletes commented-out code; version control keeps it.

## Review comment (no mode)

```text
<Blocking | Optional>: <the change you want>.
Why: <the consequence, or a link to the rule>.
Suggestion: <a concrete alternative, if you have one>.
```

Checklist:

- Opens with the requested change; the reason follows.
- Marks itself blocking or optional.
- Raises one point and names the line or symbol it concerns.
- Addresses the code, not the author.
- Links to the rule instead of restating it.
- Asks a question only when the answer changes the verdict.
