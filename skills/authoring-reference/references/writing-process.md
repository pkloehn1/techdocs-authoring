# The writing process

How to get from a blank page to an approved doc. Draws on the Air Force
*Tongue and Quill* (AFH 33-337) and the docs-as-code review loop.

## A pre-publish self-check

Before you publish, the draft should be:

- **Focused** — it covers the issue, the whole issue, and nothing but the issue.
- **Organized** — a structure the reader can follow.
- **Clear** — one reading is enough.
- **Pitched at the audience** — written for whoever actually reads it.
- **Well supported** — claims are backed by logic and evidence.

## The seven steps

1. **Analyze** the purpose and the audience.
2. **Research** the facts.
3. **Support** your ideas with evidence and examples.
4. **Organize** — outline before drafting.
5. **Draft** — get it down; do not edit yet.
6. **Edit** — a distinct, mandatory pass (see below). Do not edit while
   drafting; the two modes fight each other.
7. **Get feedback** and approval — and push for real review, not a rubber stamp.

This is the same loop as plan → research → structure → draft → edit → review.

## Lead with the bottom line

State the main point, recommendation, or required action in the first sentence
or paragraph, then support it. Distill the draft to the one sentence you would
keep if allowed only one — "what is the big idea, and why does it matter?" — and
make that the title or opening line.

## Short, constrained formats

For commit bodies, ticket fields, and summary blocks, order the content as:
bottom line, then impact, then next steps, then details. The reader gets the
decision first and the supporting detail last.

## The editing pass

Edit, as a separate step, for:

- **Clarity** — one unambiguous reading. Convert passive sentences to *actor +
  active verb*; replace jargon with plain words.
- **Conciseness** — aggressive word economy; cut filler and hidden-verb nouns.
- **Correctness** — spelling, grammar, punctuation, and factual accuracy.

## Structure before prose

Fix layout, headings, and task flow first; polish wording second. Frame the
piece as introduction, body, and conclusion, and add transitions so the reader
always knows where you are leading them. A paragraph is the unit of composition:
one coherent thought per paragraph.

## Audience profiling

An operator, an end user, a developer, and a consumer each need different depth,
tone, and style guide. Name the audience first (step 1); it drives every later
choice — including which guide you pick in
[style-guide.md](style-guide.md).

## Worked example

A failure mode and its fix, end to end:

- **Before:** a "Getting started" page opens with three paragraphs on the
  project's history and architecture, then buries the install command in the
  middle.
- **Problem:** it mixes explanation into a tutorial, and the reader can't find
  the first action.
- **Restructure:** move the history to an explanation page; lead the tutorial
  with the outcome and the first command.
- **After:** the reader runs step 1 within seconds; the page holds one Diataxis
  mode.
- **Durable rule:** classify the mode and lead with the action before drafting,
  so the opening is the task and the "why" lives elsewhere.

## Sources

- *The Tongue and Quill*, AFH 33-337 — <https://www.af.mil/Portals/1/documents/tonguequill/afh33-337.pdf>
- Google Technical Writing courses — <https://developers.google.com/tech-writing>
