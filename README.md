# techdocs-authoring

A Claude Code plugin that adds a **technical-writer subagent**, a
**documentation-authoring reference skill**, a **short-form gate hook**, and a
**Markdown line-length gate hook**.
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
| Hook | `markdown_lint_gate.py` (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`) | Holds Markdown edits to your repository's MD013 line length, and answers markdownlint findings with the fix guidance; see [Markdown line-length gate](#markdown-line-length-gate) |

The skill conforms to the open [Agent Skills](https://agentskills.io)
specification, so it is portable to other skills-compatible agents. The hooks
are Claude Code only.

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

## Markdown line-length gate

An over-long prose line is written at edit time and found at push time, by
which point the line-length guidance is a lookup nobody made. This gate
checks the edit itself, and answers a markdownlint finding wherever it shows
up.

| Trigger | What happens |
| --- | --- |
| `Write` or `Edit` of a `.md` or `.markdown` file | The text the call would leave is checked against your repository's MD013 settings. A call that adds a line over the limit is denied, with each line's number, length, and limit and the fix guidance as the reason. |
| Bash or PowerShell output with a markdownlint finding, such as `README.md:110:201 error MD013/line-length` | The fix guidance is attached to the result, whether the command passed (`PostToolUse`) or failed (`PostToolUseFailure`). |
| A prompt with a markdownlint finding in it, such as pasted linter output | The fix guidance is attached to the prompt (`UserPromptSubmit`). |

The limit is your repository's, never the plugin's. The hook looks for the
config the way your linter does:

1. MegaLinter, when `.mega-linter.yml` is at the repository root: its
   `MARKDOWN_MARKDOWNLINT_CONFIG_FILE` (default `.markdownlint.json`) at the
   root, then under `MARKDOWN_MARKDOWNLINT_RULES_PATH` or `LINTER_RULES_PATH`
   (default `.github/linters`).
2. markdownlint-cli2: `.markdownlint.jsonc`, `.json`, `.yaml`, or `.yml` in
   the file's directory or any parent up to the repository root.

It applies MD013 as markdownlint defines it: `line_length`,
`heading_line_length`, `code_block_line_length`, the `headings`, `tables`, and
`code_blocks` exemptions, `strict` and `stern`, the allowance for a long last
word such as a URL, `extends`, and `MD013: false`. A line the file already
had over the limit does not block an edit; only lines the call adds do.

The gate stays silent when no config is found, when the file carries an
inline `<!-- markdownlint-... -->` comment, when an `Edit`'s old string does
not match the file, or when the hook fails in any way. The guidance is read
from this plugin's
[`style-guide.md`](skills/authoring-reference/references/style-guide.md) on
every call.

To change the gate, set `TECHDOCS_MARKDOWN_LINT_GATE` in the `env` block of
your Claude Code settings:

| Value | Behaviour |
| --- | --- |
| unset | Deny an edit that adds an over-long line; attach the guidance to findings |
| `remind` | Attach the line list and guidance to the edit; never deny |
| `off` | Do nothing, for edits, tool output, and prompts |

Disabling the plugin with `/plugin disable techdocs-authoring` removes both
hooks together with the skill and the subagent.

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
- **For the hooks:** Python 3 on `PATH` as `python3` or `python`, and a POSIX
  shell (Git Bash on Windows). Without them the hooks error and every write
  goes through ungated. On Windows, a `python3` App Execution Alias that
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
- The hooks run locally with the standard library only and make no network
  calls. Both read the tool call and this plugin's reference files. The
  short-form gate writes one small file per session under the system temp
  directory (`techdocs-authoring-gate/`). The Markdown line-length gate also
  reads the Markdown file being edited and your repository's markdownlint and
  MegaLinter configs, and writes nothing.

## Versioning

Releases follow [SemVer](https://semver.org) via the `version` field in
`.claude-plugin/plugin.json`. Bump it to ship an update; see `CHANGELOG.md`.

## License

[MIT](LICENSE).
