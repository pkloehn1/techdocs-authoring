# Single-sourcing and content reuse

When and how to reuse content instead of copying it — and how to do it without
silently breaking other deliverables. This elaborates the single-source-of-truth
principle (one authoritative location; link, don't duplicate); it does not
replace it.

## Reuse is conditional, not the default

Single-source content only when one of these holds:

- **Multiple outputs** from one source (web + PDF + in-product help).
- **Multiple audiences** sharing chunks (operator + end user).
- **Product variants** (editions, platforms, tiers) sharing most content.
- **Frequent updates** to facts repeated in many places.
- **Large repetitive sets** where hand-syncing is error-prone.

Absent those, a simple linear document wins. Premature reuse adds machinery that
costs more than the duplication it removes.

## Principles for reusable content

- **Reuse only with intention.** Reuse a chunk when it adds clarity or removes a
  real syncing burden — not reflexively.
- **Keep it simple.** A newcomer should be able to predict what publishes where.
- **One chunk, one job.** A warning warns; a prerequisite defines prerequisites.
  Don't make a chunk do two things.
- **Stand-alone topics.** Each topic answers one question and is safe to reuse
  out of its original context.

## A graduated reuse model

Split content by topic type — concept, task, and reference (the typing scheme
that DITA, the Darwin Information Typing Architecture, formalizes). Then reuse
with the lightest mechanism that works, lowest risk to highest:

1. **Variables** — product names, versions, UI labels. Cheapest, safest.
2. **Snippets** — shared warnings, prerequisites, or procedures.
3. **Conditional profiling** — show/hide by audience, platform, or tier.
4. **Templates / styles** — shared structure and presentation.

Adopt the **lowest tier that solves the problem**. Most needs are met by
variables and a few snippets.

## Change-impact: the high-risk warning

Conditional profiling and snippets are the highest-power and highest-risk tiers:

- **Over-profiling** produces output nobody can predict or test.
- An **unintended edit to a shared snippet silently breaks every deliverable**
  that includes it.

Before editing shared content:

- Surface **which deliverables** the snippet or variable feeds (its blast
  radius).
- Resist **speculative** snippet creation — make a chunk reusable when a second
  real consumer appears, not before.
- Keep reuse under **version control with traceability and rollback**.
- **Align terminology early**; divergent terms make later reuse impossible.

## When a content management system is justified

A component content management system manages topic-level reuse, profiling, and
multi-output publishing at scale. It is justified only when the graduated model
above is genuinely outgrown — many outputs, many variants, and a team
maintaining them. For a docs-as-code repository, version-controlled Markdown with
a few variables and snippets is usually the right level.

## Sources

- Diataxis (topic-oriented authoring) — <https://diataxis.fr/>
- DITA / single-sourcing overview — <https://www.oasis-open.org/committees/dita/>
