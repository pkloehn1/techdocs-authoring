# Style guide: selection and core rules

Which canonical guide to adopt, and the highest-agreement rules that hold across
all of them. For the canonical invariants (voice defaults, link text), see
`../SKILL.md`; this file is the detail layer.

## Pick a primary guide by audience

| Audience signal | Primary guide | Why |
| --- | --- | --- |
| Developers, APIs, code samples, CLIs | Google developer documentation style guide | Built for technical/developer docs and code-forward content. |
| Software UI, help, error and UI text, broad product | Microsoft Writing Style Guide | Warm, plain, UX-writing oriented; strong on UI and messaging. |
| Consumer product docs, onboarding | Apple Style Guide | Polished consumer voice and product-naming conventions. |

Google itself recommends adopting an established guide (Microsoft or Google)
rather than writing a bespoke one. Do that.

## Layer, don't blend

- **One primary technical guide.** Pick a single guide from the table and make
  it the default.
- **Chicago or AP for grammar edge cases only** — punctuation, citation, number
  style the primary guide leaves open. Do not import their whole voice.
- **A thin local override layer** on top: the minimum-viable set is voice,
  terminology, formatting, and who owns review. Grow it only from real review
  friction, never speculatively.

Never blend two technical guides inside one document — the reader feels the
seam.

## Voice and tone defaults

These are the convergent Google + Microsoft rules:

- **Second person** ("you"), **imperative mood** for steps ("Run the command").
- **Active voice.** Use passive only when the actor is unknown or deliberately
  de-emphasized, and treat that as the documented exception.
- **Present tense**, contractions allowed, and start sentences with a verb where
  you can.

## Brevity: bigger ideas, fewer words

- Front-load keywords so a section is findable by skim and by search.
- Prune low-value openers: "you can", "there is / there are", "in order to",
  "simply", "basically", "please note".
- Cut nominalizations — hidden verbs buried in `-tion` / `-ment` nouns
  ("perform a validation of" → "validate").
- Keep sentences short; set a maximum sentence length and hold to it.

This is the same economy that Strunk's *Elements of Style* and a grade-9
readability target encode. If your repository already adopts those, this is the
same baseline — not a competing one. Defer any numeric line- or sentence-length
**limit** to your repo's lint configuration.

## Mechanical conventions (deterministic)

- **Sentence case** for headings and titles — never Title Case.
- **No terminal punctuation** on headings or short list items.
- **Serial (Oxford) comma** in lists.
- **Code font** for identifiers, commands, paths, and values; **bold** for UI
  elements the reader clicks.
- **Descriptive link text** — the link names its destination; never "click
  here" or a bare URL.
- Numbered lists for ordered steps; `-` bullets for unordered sets.

## Screenshots and media

- **Prefer text and code over screenshots.** Screenshots go stale, are not
  searchable, and carry an accessibility cost.
- When a screenshot is genuinely necessary: add a **caption** and **alt text**,
  **crop to the relevant region**, and note the **product version** captured.
- **Alt text** describes the content/function for screen readers; decorative
  images get empty alt text.
- **Never rely on color alone** to carry meaning in a diagram or callout — pair
  it with a label, shape, or text.

## Versioning and deprecation of pages

- Mark a version-scoped page with a **top-of-page banner** stating which
  product/release it applies to.
- When a page is superseded, add a **deprecation notice with a migration
  pointer** — a link to the page that replaces it — instead of deleting it
  silently.
- **Retire** outdated pages rather than leaving orphaned stale content; redirect
  or link forward so no reader lands on a dead end. This is the same
  single-source-of-truth discipline as "link, don't duplicate."

## Sources

- Google developer documentation style guide — <https://developers.google.com/style>
- Microsoft Writing Style Guide — <https://learn.microsoft.com/style-guide/welcome/>
- Apple Style Guide — <https://support.apple.com/guide/applestyleguide/>
