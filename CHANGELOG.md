# Changelog

All notable changes to this plugin are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org).

## [0.3.1](https://github.com/pkloehn1/techdocs-authoring/compare/v0.3.0...v0.3.1) (2026-10-09)


### Build and CI

* **release:** put docs, tests and CI work in the changelog ([ac51fa4](https://github.com/pkloehn1/techdocs-authoring/commit/ac51fa4c6342e79e8e4b3642b9dc103c5eeabf4e))
* **release:** put docs, tests and CI work in the changelog ([bffba5d](https://github.com/pkloehn1/techdocs-authoring/commit/bffba5dd171716ca61b1db9758a9993514ec88ca))

## [0.3.0](https://github.com/pkloehn1/techdocs-authoring/compare/v0.2.0...v0.3.0) (2026-10-09)


### Features

* finish the short-form artifact set and enforce one artifact list ([932073e](https://github.com/pkloehn1/techdocs-authoring/commit/932073e67a2508fa84767efbd236dd0779e28976))
* **validate:** make the artifact list one source and enforce the rest agree ([8b80014](https://github.com/pkloehn1/techdocs-authoring/commit/8b80014463d3220c7669dbaac78769af11e46c14))

## [0.2.0](https://github.com/pkloehn1/techdocs-authoring/compare/v0.1.0...v0.2.0) (2026-06-03)


### Features

* initial techdocs-authoring plugin — technical-writer agent + authoring-reference skill ([ea69516](https://github.com/pkloehn1/techdocs-authoring/commit/ea695168e8060a1d9ef804a6dafa1f8290ebf85a))

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
