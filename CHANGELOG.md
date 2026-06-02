# Changelog

All notable changes to this plugin are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org).

## [0.1.0] - 2026-06-02

### Added
- `technical-writer` subagent: a documentation drafting/review persona with a
  scoped tool allow-list (`Read`, `Write`, `Edit`, `Grep`, `Glob`,
  `Bash(git:*)`, `WebFetch`, `WebSearch`), preloading the reference skill and
  working in its own context.
- `authoring-reference` skill (open Agent Skills format) with progressive
  disclosure:
  - `references/style-guide.md` — canonical style-guide selection, voice and
    mechanical conventions, screenshots/media, versioning and deprecation.
  - `references/doc-types-and-diataxis.md` — the Diataxis four-mode model and
    one-mode-per-page discipline.
  - `references/templates-and-checklists.md` — section skeletons + reviewer
    checklists for README, how-to, tutorial, reference, ADR, runbook, and
    release notes.
  - `references/single-sourcing-and-reuse.md` — conditional reuse, DITA tiers,
    and change-impact discipline.
  - `references/writing-process.md` — the Tongue and Quill writing process: a
    pre-publish self-check, the seven steps, leading with the bottom line, and a
    separate editing pass for clarity, conciseness, and correctness.
  - `references/docs-for-humans-and-agents.md` — dual-audience docs, the
    skill/tool/subagent/plugin separation, and agent-readable structure.
- CI: manifest-driven SemVer release via release-please, structural validation
  of the plugin/skill/agent frontmatter, and CodeQL scanning of GitHub Actions
  workflows.
