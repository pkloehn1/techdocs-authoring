#!/usr/bin/env python3
"""Measure how often a skill description pulls the skill in.

skill-creator's own `run_loop.py` does this and is the tool to prefer. It
cannot run on Windows: it waits on the `claude -p` pipe with `select.select`,
which accepts only sockets there, so every query fails with WinError 10038
before a model is reached. Upstream issue: see evals/README.md.

This runner reproduces that measurement with a reader thread instead of
`select`, so it is portable. Detection mirrors `run_eval.py` exactly - the same
stream events, the same Skill-or-Read tool names, the same early exit on a
third tool - because a different rule would produce a number that cannot be
compared with upstream's.

    python run_trigger_evals.py --eval-set trigger-evals.json \
        --skill-path .. --model claude-opus-5

Stdlib only, and it writes nothing outside the scratch project it creates.
"""

import argparse
import json
import os
import queue
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def parse_skill(skill_path: Path) -> tuple[str, str]:
    """Return the skill's name and description from its frontmatter."""
    text = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    block = text.split("---", 2)[1]
    found = re.search(r"^name:\s*(.+)$", block, re.M)
    if not found:
        raise SystemExit(f"{skill_path}/SKILL.md has no name in its frontmatter")
    name = found.group(1).strip()

    folded = re.search(r"^description:\s*(>-|\|)?\s*\n((?:[ \t]+.+\n?)+)", block, re.M)
    if folded:
        description = " ".join(line.strip() for line in folded.group(2).splitlines())
    else:
        inline = re.search(r"^description:\s*(.+)$", block, re.M)
        if not inline:
            raise SystemExit(f"{skill_path}/SKILL.md has no description in its frontmatter")
        description = inline.group(1).strip()
    return name, description.strip()


def reader(stream, sink: queue.Queue) -> None:
    """Drain a pipe line by line. A thread replaces select, which Windows
    refuses on anything but a socket."""
    try:
        for line in iter(stream.readline, b""):
            sink.put(line)
    finally:
        sink.put(None)


def detect(stream, marker: str, still_running=lambda: True) -> bool | None:
    """Scan a stream-json run for an invocation of the skill named by marker.

    Returns True on an invocation, False when the run finished without one, and
    None when the stream ended with no verdict.

    Upstream's version abandons a run as soon as it sees a tool that is not
    Skill or Read. A one-shot run routinely inspects the repository first, so
    that rule scores a genuine invocation on turn five as a miss. Every tool but
    the one being looked for is ignored here instead.
    """
    accumulated = ""
    pending = False
    for raw in stream:
        if not still_running():
            return None
        try:
            event = json.loads(
                (raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw).strip())
        except (json.JSONDecodeError, AttributeError):
            continue

        kind = event.get("type")
        if kind == "stream_event":
            se = event.get("event", {})
            se_type = se.get("type", "")
            if se_type == "content_block_start":
                block = se.get("content_block", {})
                pending = (block.get("type") == "tool_use"
                           and block.get("name") in ("Skill", "Read"))
                accumulated = ""
            elif se_type == "content_block_delta" and pending:
                delta = se.get("delta", {})
                if delta.get("type") == "input_json_delta":
                    accumulated += delta.get("partial_json", "")
                    if marker in accumulated:
                        return True
            elif se_type == "content_block_stop":
                pending = False
        elif kind == "assistant":
            for item in event.get("message", {}).get("content", []):
                if item.get("type") != "tool_use":
                    continue
                data = item.get("input", {})
                if item.get("name") == "Skill" and marker in str(data.get("skill", "")):
                    return True
                if item.get("name") == "Read" and marker in str(data.get("file_path", "")):
                    return True
        elif kind == "result":
            return False
    return None


def isolated_config(source: Path | None) -> Path | None:
    """Build a config directory holding credentials and nothing else.

    Returns None when no credentials file is found, which leaves the caller to
    decide between an unisolated run and no run at all."""
    if source is None:
        source = Path.home() / ".claude"
    credentials = source / ".credentials.json"
    if not credentials.exists():
        return None
    target = Path(tempfile.mkdtemp(prefix="trigger-eval-config-"))
    shutil.copy2(credentials, target / ".credentials.json")
    return target


def triggered(query: str, name: str, description: str, root: Path,
              model: str | None, timeout: int,
              config_dir: Path | None = None) -> bool | None:
    """Run one query. True if the skill was invoked, False if not, None if the
    run never produced a verdict - a failure to measure is not a negative."""
    marker = f"{name}-skill-{uuid.uuid4().hex[:8]}"
    command_file = root / ".claude" / "commands" / f"{marker}.md"
    command_file.parent.mkdir(parents=True, exist_ok=True)
    indented = "\n  ".join(description.split("\n"))
    command_file.write_text(
        f"---\ndescription: |\n  {indented}\n---\n\n# {name}\n\n"
        f"This skill handles: {description}\n",
        encoding="utf-8")

    cmd = ["claude", "-p", query, "--output-format", "stream-json",
           "--verbose", "--include-partial-messages"]
    if model:
        cmd += ["--model", model]
    # CLAUDECODE guards an interactive terminal; a subprocess is not one.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    # A SessionStart hook that loads the skill hands the subprocess the whole
    # guidance, so the model never needs the Skill tool and every query scores
    # zero - a rate that reads the same whether the description works or not.
    # The throwaway config carries credentials and nothing else, so the only
    # skill-shaped thing on offer is the one being measured.
    if config_dir:
        env["CLAUDE_CONFIG_DIR"] = str(config_dir)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, cwd=root, env=env)
    lines: queue.Queue = queue.Queue()
    threading.Thread(target=reader, args=(process.stdout, lines),
                     daemon=True).start()

    verdict: bool | None = None
    deadline = time.time() + timeout
    try:
        stream = iter(lambda: lines.get(timeout=max(0.1, deadline - time.time())), None)
        verdict = detect(stream, marker, lambda: time.time() < deadline)
    except queue.Empty:
        verdict = None
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        command_file.unlink(missing_ok=True)
    return verdict


def split(eval_set: list[dict], holdout: float, seed: int = 42):
    """Stratify by should_trigger, as upstream does, so both halves carry
    positives and negatives."""
    rng = random.Random(seed)
    halves = []
    for want in (True, False):
        group = [e for e in eval_set if e["should_trigger"] == want]
        rng.shuffle(group)
        cut = int(len(group) * (1 - holdout))
        halves.append((group[:cut], group[cut:]))
    return halves[0][0] + halves[1][0], halves[0][1] + halves[1][1]


def rate(results: list[dict], want: bool) -> str:
    group = [r for r in results if r["should_trigger"] == want]
    if not group:
        return "n/a"
    correct = sum(r["rate"] if want else 1 - r["rate"] for r in group)
    return f"{correct / len(group):.0%}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--skill-path", required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--runs-per-query", type=int, default=3)
    ap.add_argument("--num-workers", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--holdout", type=float, default=0.4)
    ap.add_argument("--out", default=None, help="write the summary as JSON")
    ap.add_argument("--no-isolate", action="store_true",
                    help="keep the ambient config, hooks and plugins; the rate "
                         "then measures nothing if a hook preloads the skill")
    args = ap.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    name, description = parse_skill(Path(args.skill_path))
    train, test = split(eval_set, args.holdout) if args.holdout else (eval_set, [])

    if shutil.which("claude") is None:
        print("claude CLI not on PATH", file=sys.stderr)
        return 2

    config_dir = None if args.no_isolate else isolated_config(None)
    if not args.no_isolate and config_dir is None:
        print("No .credentials.json found, so the subprocess config cannot be "
              "isolated. Re-run with --no-isolate to accept an ambient config, "
              "knowing a hook that preloads the skill voids the result.",
              file=sys.stderr)
        return 2
    print(f"config: {'ambient' if config_dir is None else 'isolated'}")

    root = Path(tempfile.mkdtemp(prefix="trigger-eval-"))
    (root / ".claude" / "commands").mkdir(parents=True)
    try:
        def measure(entry: dict) -> dict:
            runs = [triggered(entry["query"], name, description, root,
                              args.model, args.timeout, config_dir)
                    for _ in range(args.runs_per_query)]
            scored = [r for r in runs if r is not None]
            return {
                "query": entry["query"],
                "should_trigger": entry["should_trigger"],
                "rate": (sum(scored) / len(scored)) if scored else 0.0,
                "unmeasured": len(runs) - len(scored),
            }

        with ThreadPoolExecutor(max_workers=args.num_workers) as pool:
            results = list(pool.map(measure, eval_set))
    finally:
        shutil.rmtree(root, ignore_errors=True)
        if config_dir:
            shutil.rmtree(config_dir, ignore_errors=True)

    by_query = {r["query"]: r for r in results}
    summary = {
        "skill": name,
        "runs_per_query": args.runs_per_query,
        "train": [by_query[e["query"]] for e in train],
        "test": [by_query[e["query"]] for e in test],
    }

    for label in ("train", "test"):
        rows = summary[label]
        if not rows:
            continue
        print(f"\n{label} ({len(rows)} queries)")
        for r in sorted(rows, key=lambda r: not r["should_trigger"]):
            want = "should" if r["should_trigger"] else "should NOT"
            flag = "ok " if (r["rate"] >= 0.5) == r["should_trigger"] else "MISS"
            note = f"  [{r['unmeasured']} unmeasured]" if r["unmeasured"] else ""
            print(f"  {flag} {r['rate']:>4.0%} {want:<10} {r['query'][:58]}{note}")
        print(f"  correct on should-trigger: {rate(rows, True)}")
        print(f"  correct on should-not:     {rate(rows, False)}")

    unmeasured = sum(r["unmeasured"] for r in results)
    if unmeasured:
        print(f"\n{unmeasured} run(s) produced no verdict and were excluded.")
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\nSummary written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
