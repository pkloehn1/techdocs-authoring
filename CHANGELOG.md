# Changelog

All notable changes to this plugin are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org).

## [0.5.0](https://github.com/pkloehn1/techdocs-authoring/compare/v0.4.0...v0.5.0) (2026-10-22)


### Features

* **hooks:** hold Markdown edits to the repository's MD013 line length ([01289ae](https://github.com/pkloehn1/techdocs-authoring/commit/01289ae4eac4bcaba018a3b25a6a48dff106c0cc))
* **hooks:** hold Markdown edits to the repository's MD013 line length ([fa7cb7a](https://github.com/pkloehn1/techdocs-authoring/commit/fa7cb7a35a66d616880d2c457c4ab11fc6695cd5))


### Documentation

* **readme:** say what the line-length gate checks and how to turn it down ([2398eb6](https://github.com/pkloehn1/techdocs-authoring/commit/2398eb6694eec5b9331ab4b191d3324f0cd23cfc))
* **skill:** add the fix for an MD013 line-length finding ([50bf62d](https://github.com/pkloehn1/techdocs-authoring/commit/50bf62dcc5bdc0f7546cc8d40ba062b531d71702))
* **skill:** tell the model a line-length denial carries its fix ([3fa50ce](https://github.com/pkloehn1/techdocs-authoring/commit/3fa50cea8bbcd6adeb8949e2d4e8a95b896e1bc4))

## [0.4.0](https://github.com/pkloehn1/techdocs-authoring/compare/v0.3.1...v0.4.0) (2026-10-20)


### Features

* **hooks:** hold the first short-form write of a session against its checklist ([7a5d507](https://github.com/pkloehn1/techdocs-authoring/commit/7a5d50795614d8e881be81dd29b06840300f9d69))
* **hooks:** hold the first short-form write of a session against its checklist ([08de6b3](https://github.com/pkloehn1/techdocs-authoring/commit/08de6b36603a9c2290021ec8df5664319f8e01ae))


### Documentation

* **readme:** say what the short-form gate denies and how to turn it down ([77a91a9](https://github.com/pkloehn1/techdocs-authoring/commit/77a91a9a7b91ad94131b8c56e5fc85a1442727f4)), closes [#7](https://github.com/pkloehn1/techdocs-authoring/issues/7)
* **skill:** tell the model a gate denial is the checklist arriving ([00cb5ed](https://github.com/pkloehn1/techdocs-authoring/commit/00cb5ed511c0df3993f8b66c6a58d16ac1b1ccff))

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
