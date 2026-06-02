# techdocs-authoring

A Claude Code plugin that adds a **technical-writer subagent** and a
**documentation-authoring reference skill** — portable, vendor-neutral, and
conformant with the open [Agent Skills](https://agentskills.io) specification.

It is built for *writing and reviewing* technical docs: picking a canonical
style guide, classifying each doc with the Diataxis four-mode model, applying
templates and reviewer checklists for READMEs, how-tos, tutorials, reference,
ADRs, runbooks, and release notes, single-sourcing content, running a disciplined
writing process, and making docs serve both humans and AI agents. The subagent
drafts and reviews in its own context, so doc-heavy work doesn't flood your main
session.

## What's inside

| Component | Name | Purpose |
|---|---|---|
| Subagent | `technical-writer` | Drafting/review persona with a scoped tool allow-list; preloads the reference skill and works in its own context |
| Skill | `authoring-reference` | Portable writing craft — style-guide selection, Diataxis, templates/checklists, single-sourcing, the writing process, and dual human+AI-agent docs (progressive disclosure via `references/`) |

The skill conforms to the open [Agent Skills](https://agentskills.io)
specification, so it is portable to other skills-compatible agents.

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

## Versioning

Releases follow [SemVer](https://semver.org) via the `version` field in
`.claude-plugin/plugin.json`. Bump it to ship an update; see `CHANGELOG.md`.

## License

[MIT](LICENSE).
