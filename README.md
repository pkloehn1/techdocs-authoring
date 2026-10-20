# techdocs-authoring

A Claude Code plugin that adds a **technical-writer subagent**, a
**documentation-authoring reference skill**, and a **short-form gate hook**.
The content is portable, vendor-neutral, and conformant with the open
[Agent Skills](https://agentskills.io) specification.

It is built for *writing and reviewing* technical docs: picking a canonical
style guide, classifying each doc with the Diataxis four-mode model, applying
templates and reviewer checklists for READMEs, how-tos, tutorials, reference,
ADRs, runbooks, release notes, and the five short-form artifacts an engineer
writes daily (commit message, issue body, change-request description, review
comment, code comment), single-sourcing content, running a disciplined writing
process, and making docs serve both humans and AI agents. The subagent drafts
and reviews in its own context, so doc-heavy work doesn't flood your main
session.

## What's inside

| Component | Name | Purpose |
|---|---|---|
| Subagent | `technical-writer` | Drafting/review persona with a scoped tool allow-list; preloads the reference skill and works in its own context |
| Skill | `authoring-reference` | Portable writing craft — style-guide selection, Diataxis, templates/checklists, single-sourcing, the writing process, and dual human+AI-agent docs (progressive disclosure via `references/`) |
| Hook | `short_form_gate.py` (`PreToolUse`) | Holds the first short-form write of each session against that artifact's checklist; see [Short-form gate](#short-form-gate) |

The skill conforms to the open [Agent Skills](https://agentskills.io)
specification, so it is portable to other skills-compatible agents. The hook is
Claude Code only.

## Short-form gate

A loaded skill is not a consulted one: in measured sessions the checklists for
short-form prose were never opened, while the writing they govern shipped. The
gate puts the checklist in front of the draft before the write runs.

The first write of each artifact kind in a session is denied, with that
artifact's skeleton and checklist as the reason. Claude checks the draft against
it, revises, and sends the call again. That retry and every later write of the
kind pass, with the checklist attached as context.

| Write | Checklist returned |
| --- | --- |
| `git commit` in a Bash or PowerShell command | Commit message |
| `gh issue create`; `gh issue edit` with title or body | Issue body |
| `gh pr create`; `gh pr edit` with title or body | Change-request description |
| `gh pr comment`; `gh pr review` with a body | Review comment |
| `gh issue comment` | Short, constrained formats |
| GitLab MCP: create or update an issue, or patch its description | Issue body |
| GitLab MCP: create or update a merge request | Change-request description |
| GitLab MCP: merge-request notes, threads, and draft notes | Review comment |
| GitLab MCP: issue notes | Short, constrained formats |

An update that sets no title, description, body, or patch (labels, state,
milestone) is not gated, and neither is `git commit --no-edit`. GitLab MCP means
any MCP server whose name contains `gitlab`.

The checklist is read from this plugin's own
[`templates-and-checklists.md`](skills/authoring-reference/references/templates-and-checklists.md)
and [`writing-process.md`](skills/authoring-reference/references/writing-process.md)
on every call, so the gate never disagrees with the skill. If the hook cannot
read the checklist, has no session id, cannot record its state, or fails in any
way, the write goes through.

To change the gate, set `TECHDOCS_SHORT_FORM_GATE` in the `env` block of your
Claude Code settings:

| Value | Behaviour |
| --- | --- |
| unset | Deny the first write of each kind; attach the checklist after |
| `remind` | Attach the checklist to every write; never deny |
| `off` | Do nothing |

Disabling the plugin with `/plugin disable techdocs-authoring` removes the hook
together with the skill and the subagent.

## Install

```text
/plugin marketplace add pkloehn1/techdocs-authoring
/plugin install techdocs-authoring
```

Or test locally without installing:

```bash
claude --plugin-dir /path/to/techdocs-authoring
```

Then delegate to it (e.g. "use the technical-writer agent to draft the
deployment runbook") or open the reference with
`/techdocs-authoring:authoring-reference`.

## Prerequisites

- **None hard.** A docs-as-code workflow (Markdown in version control, reviewed
  by pull request) is assumed.
- **Optional:** `WebFetch` / `WebSearch` for pulling canonical style-guide pages
  while writing.
- **For the short-form gate:** Python 3 on `PATH` as `python3` or `python`, and
  a POSIX shell (Git Bash on Windows). Without them the hook errors and every
  write goes through ungated. On Windows, a `python3` App Execution Alias that
  points at the Microsoft Store shadows a real `python`; turn the alias off.

## Relationship to your repository's docs standards

This plugin carries portable **craft**; your repository keeps its
**enforcement**. The skill never restates repo-specific rules — line-length
limits, numbered-heading validation, diagram linting, pre-commit/CI wiring, or
repo paths — and defers those numbers and tools to your repo. Where a craft
principle here overlaps one your repo already adopts (Strunk-style economy, a
grade-9 readability target, single-source-of-truth), they are the same baseline,
not competing rules. Adopt the skill alongside your existing standards, not in
place of them.

## Security & scope

- The content is **vendor-neutral** and ships **no secrets**.
- The subagent has a **scoped tool allow-list** so it can author and review docs
  and run the project's Markdown linters, but cannot reach infrastructure or
  mutation tooling. It authors prose only — it does not edit code, config, or CI.
  The allow-list is `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash(git:*)`, and
  the doc linters `Bash(pre-commit:*)`, `Bash(markdownlint:*)`,
  `Bash(markdownlint-cli2:*)`, `Bash(npx:*)`, `Bash(vale:*)`, plus `WebFetch` and
  `WebSearch`.
- The hook runs locally with the standard library only. It reads the tool call
  and this plugin's reference files, writes one small file per session under
  the system temp directory (`techdocs-authoring-gate/`), and makes no network
  calls.

## Versioning

Releases follow [SemVer](https://semver.org) via the `version` field in
`.claude-plugin/plugin.json`. Bump it to ship an update; see `CHANGELOG.md`.

## License

[MIT](LICENSE).
