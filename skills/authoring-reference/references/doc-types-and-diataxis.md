# Doc types and the Diataxis model

Diataxis is the primary axis: it tells you which *kind* of document you are
writing and keeps each page coherent. Use it to classify before you draft.

## Diataxis: four modes on two axes

The two axes are **action ↔ cognition** (doing vs. knowing) and **acquisition ↔
application** (learning vs. working).

| Mode | Axis position | Serves | The reader wants |
| --- | --- | --- | --- |
| **Tutorial** | action + acquisition | learning by doing | "teach me, hold my hand" |
| **How-to guide** | action + application | a real task | "help me do this specific thing" |
| **Reference** | cognition + application | lookup | "tell me the facts, exactly" |
| **Explanation** | cognition + acquisition | understanding | "help me understand why" |

## One mode per page

The most common documentation failure is mixing modes — a tutorial that drifts
into reference tables, a reference page that starts explaining rationale. Every
page **declares one mode and holds it**; reviewers reject cross-quadrant
content (see the invariants in `../SKILL.md`). When a page wants to be two
modes, it is two pages — split it and cross-link.

## Mode-by-mode rules

- **Tutorial** — learning-oriented and author-owned. Reproducible, no choices or
  alternatives, minimal explanation, guaranteed success, written for a beginner.
  The author makes every decision so the learner can't get lost.
- **How-to guide** — task-oriented. Addresses one real goal, assumes competence,
  may branch for conditions, written for a practitioner under time pressure.
  **Always ships a verification step** (how to confirm the goal was achieved),
  then a Troubleshooting section and Next steps.
- **Reference** — information-oriented. Austere, exhaustive, neutral; mirrors the
  product or code surface. It **describes and never instructs or explains**.
  Generate it from source (OpenAPI, docstrings) where possible to prevent drift.
- **Explanation** — understanding-oriented. Discursive; gives context,
  rationale, alternatives, and trade-offs. This is the home for the "why" that
  the other three modes deliberately omit.

## A note on genres

Common engineering artifacts map onto the modes — they are not a competing
taxonomy:

- README → a how-to-shaped front door (orient + install + first use).
- Tutorial / getting-started → tutorial.
- API docs, configuration reference, CLI reference → reference.
- ADR, design doc, concept guide → explanation.
- Runbook → a how-to under operational constraints (verification, rollback,
  escalation).
- Release notes / changelog → reference (a dated record of what changed).

Pick the mode first; the genre then selects the template in
[templates-and-checklists.md](templates-and-checklists.md).

## Sources

- Diataxis framework — <https://diataxis.fr/>
