# Evals

Two sets, two jobs. Neither grades prose by taste: the output evals assert on
things a grader can check, and the trigger evals produce a rate.

| File | Measures | Run by |
| --- | --- | --- |
| `evals.json` | Whether the skill improves the writing | `skill-creator`'s `run_eval.py`, benchmark mode |
| `trigger-evals.json` | Whether the description pulls the skill in | `skill-creator`'s `run_loop.py` |

## Measure whether the skill helped

Benchmark mode runs each eval with and without the skill and reports both pass
rates, so a change is defended by a delta rather than by assertion.

```bash
python scripts/run_eval.py \
  --skill-path skills/authoring-reference \
  --evals skills/authoring-reference/evals/evals.json \
  --runs-per-configuration 3
```

A change to the skill is worth keeping when `with_skill` beats `without_skill`
on pass rate across runs. An assertion that passes in both configurations is
not measuring the skill and belongs in the qualitative list below.

## Measure the trigger rate

```bash
python skills/authoring-reference/evals/run_trigger_evals.py \
  --eval-set skills/authoring-reference/evals/trigger-evals.json \
  --skill-path skills/authoring-reference
```

Ten queries should trigger and ten should not. The negatives are near-misses
that share vocabulary with the skill — Diataxis, markdownlint, README, style
guide, release — because a negative set of obviously unrelated queries measures
nothing. The run splits 60/40 stratified, repeats each query three times, and
reports both halves so a description cannot be tuned against the set it is
scored on.

`skill-creator`'s own `run_loop.py` is the tool to prefer, and it also rewrites
the description rather than only measuring it. It cannot run on Windows:
`run_eval.py` waits on the `claude -p` pipe with `select.select`, which accepts
only sockets there. Filed as
[claude-plugins-official#6381](https://github.com/anthropics/claude-plugins-official/issues/6381).
`run_trigger_evals.py` exists for that reason, mirrors the same detection, and
should be retired when the upstream fix lands.

### Three ways this measurement lies

Each of these produced a confident, uniform zero that looked like a weak
description:

- **A session hook that loads the skill.** The subprocess receives the whole
  guidance, so the model never needs the Skill tool. The runner isolates
  `CLAUDE_CONFIG_DIR` to a throwaway directory holding only credentials; the
  header line reports `config: isolated` when it did.
- **Detection that gives up on the first unrelated tool.** A run that inspects
  the repository before reaching for the skill is a genuine trigger, and
  upstream's rule scores it as a miss. The runner ignores every tool except the
  one it is looking for and decides at the `result` event.
- **The model.** The same query triggered 100% on the CLI default
  (`claude-opus-5-5`) and 0% on `claude-opus-5`. Record the model with any rate
  quoted from this set, and do not compare rates across models.

A run that produces no verdict counts as **unmeasured** and is excluded, rather
than counting as a miss — a harness failure must not read as a result.

## Where the output evals came from

Each one reproduces a failure that happened, not a hypothetical:

| Eval | The failure it reproduces |
| --- | --- |
| 1 | A change-request description that invented sections a three-section template did not define |
| 2 | A fifteen-line comment added beside three-line neighbours |
| 3 | An acceptance criterion that could not be true on the day its issue closed |
| 4 | A commit body that listed changed files and narrated the session instead of saying why |
| 5 | A comment that paraphrased its loop, beside a regular expression with none — the one case that earns a what |
| 6 | A getting-started page that opened with history and buried the first command |

## Reviewed qualitatively, not asserted

Three things matter and resist a checkable assertion. Read them in the viewer
rather than scoring them:

- Whether an added comment matches the *voice* of its neighbours, beyond
  matching their length.
- Whether a rewritten page reads as one mode to someone who did not write it.
- Whether discipline holds late in a long session rather than only in the first
  few turns. This is the open question behind the persistence section, and a
  single-run eval cannot answer it; compare an early and a late run of the same
  eval in one session.
