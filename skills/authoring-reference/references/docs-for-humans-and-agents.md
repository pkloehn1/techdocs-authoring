# Docs for humans and AI agents

Increasingly, docs are read by AI agents as well as people. The good news: the
same progressive-disclosure discipline that makes a strong SKILL.md makes strong
agent-readable docs — a short, trigger-rich, front-loaded summary; a
deterministic structure; one-level-deep links; and explicit when-to-use and
when-not.

## Skill vs. tool vs. subagent vs. plugin

Doc authors need this map to place knowledge in the right home:

- **Tool (including MCP)** — a capability the model *calls* to take an action or
  fetch data. It is a function, not documentation.
- **Skill** — packaged procedural knowledge that teaches *how* to do something.
  It is model-invoked by its name + description and uses progressive disclosure
  (a lean entry file that links to detail). Durable "how we do X" belongs here.
- **Subagent** — an isolated context with its own prompt and tool scope for a
  delegated job; it returns only a summary, keeping bulk out of the main
  context.
- **Plugin** — a bundle that distributes skills, agents, commands, and MCP
  config together.

Rule of placement: capture a durable procedure as a **skill**; expose a new
action as a **tool/MCP**; delegate a context-heavy job to a **subagent**.

## Authoring agent-readable docs

- **Front-load a trigger-rich summary** that humans skim and agents match on:
  what this is and *when* to use it, with concrete triggers.
- **Separate facts from procedures.** Keep reference (stable facts) apart from
  how-to (steps). Agents retrieve and recombine them more reliably when they are
  not interleaved.
- **Show concrete input/output examples** — agents ground on examples.
- **Provide machine-discoverable entrypoints** — an
  [`llms.txt`](https://llmstxt.org/) index at the site root that points to the
  key docs, mirroring how a SKILL.md indexes its references.

## Conform to the open Agent Skills standard

If you are authoring a skill itself, follow the open
[Agent Skills](https://agentskills.io/) standard so it is portable:

- The skill **name equals its directory name**; `name` and `description` are
  required.
- The description states **what** and **when**, with concrete triggers.
- Keep the entry file lean (roughly under ~500 lines); push detail into
  one-level-deep reference files.
- Use standard fields for portability; keep any vendor extensions additive and
  gracefully degrading.

(For the canonical authoring invariants, see `../SKILL.md`.)

## Sources

- Agent Skills standard — <https://agentskills.io/>
- llms.txt — <https://llmstxt.org/>
