#!/usr/bin/env python3
"""PreToolUse hook: hold the first short-form write of a session against its checklist.

A reminder that arrives with the tool call comes after the text is composed, so
it can only change the next write, and a paraphrase of a checklist reads as the
checklist. This hook instead denies the first write of each artifact kind in a
session, with that artifact's skeleton and checklist as the reason, so the draft
is checked before it ships. Later writes of the kind pass with the checklist
attached. See pkloehn1/techdocs-authoring#7.

The checklists are read from this plugin's own references at call time and
never restated here, so the gate cannot drift from the skill.

Every failure path allows the write: no checklist, no session id, unwritable
state, or any exception. Blocking without the rules that justify it would only
cost a round-trip.

Set TECHDOCS_SHORT_FORM_GATE=remind to attach the checklist without denying,
or =off to silence the hook.

Stdlib only. Self-test::

    python hooks/short_form_gate.py --self-test
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

_SKILL = "techdocs-authoring:authoring-reference"
_REFERENCES = Path(__file__).resolve().parent.parent / "skills" / "authoring-reference" / "references"
_STATE_DIR = Path(tempfile.gettempdir()) / "techdocs-authoring-gate"

# Kind -> (label, reference file, heading prefix of its section).
_SECTIONS: dict[str, tuple[str, str, str]] = {
    "commit": ("commit message", "templates-and-checklists.md", "Commit message"),
    "issue": ("issue body", "templates-and-checklists.md", "Issue body"),
    "cr": ("change-request description", "templates-and-checklists.md", "Change-request description"),
    "review": ("review comment", "templates-and-checklists.md", "Review comment"),
    "note": ("issue comment", "writing-process.md", "Short, constrained formats"),
}

# GitLab MCP tool suffixes, enumerated: create_issue_link and the emoji tools
# carry no prose and must not match a pattern.
_GITLAB_TOOLS: dict[str, str] = {
    "create_issue": "issue",
    "update_issue": "issue",
    "update_issue_description_patch": "issue",
    "create_merge_request": "cr",
    "update_merge_request": "cr",
    "create_merge_request_note": "review",
    "update_merge_request_note": "review",
    "create_merge_request_thread": "review",
    "create_merge_request_discussion_note": "review",
    "update_merge_request_discussion_note": "review",
    "create_draft_note": "review",
    "update_draft_note": "review",
    "create_issue_note": "note",
    "update_issue_note": "note",
    "create_note": "note",
}

# An update that sets none of these (labels, state, milestone) writes no prose.
_PROSE_FIELDS = ("title", "description", "body", "patch")

# Searched anywhere in the command, because commits are often compound:
# `git add -- a && git commit -F m -- a`. The lookahead keeps commit-tree out.
_GIT_COMMIT = re.compile(r"\bgit(?:\s+-[Cc]\s+\S+)*\s+commit(?![\w-])")
_NO_EDIT = re.compile(r"\s--no-edit\b")

_GH_ALWAYS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgh\s+issue\s+create\b"), "issue"),
    (re.compile(r"\bgh\s+pr\s+create\b"), "cr"),
    (re.compile(r"\bgh\s+issue\s+comment\b"), "note"),
    (re.compile(r"\bgh\s+pr\s+comment\b"), "review"),
)
# These subcommands also change labels, state, or a verdict with no prose.
_GH_IF_PROSE: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgh\s+issue\s+edit\b"), "issue"),
    (re.compile(r"\bgh\s+pr\s+edit\b"), "cr"),
    (re.compile(r"\bgh\s+pr\s+review\b"), "review"),
)
_GH_PROSE_FLAG = re.compile(r"\s(?:-b|--body|-F|--body-file|-t|--title)(?=[\s=])")


def section(filename: str, heading: str, references: Path = _REFERENCES) -> str:
    """The `## <heading>...` section of *filename*, up to the next `## `, or empty."""
    try:
        lines = (references / filename).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    out: list[str] = []
    fenced = False
    for line in lines:
        if line.startswith("```"):
            fenced = not fenced
        # The issue skeleton's `## Problem` sits inside a fence and is not a heading.
        if line.startswith("## ") and not fenced:
            if out:
                break
            if line[3:].startswith(heading):
                out.append(line)
        elif out:
            out.append(line)
    return "\n".join(out).strip()


def _command_kind(command: str) -> str:
    if _GIT_COMMIT.search(command):
        return "" if _NO_EDIT.search(command) else "commit"
    for pattern, kind in _GH_ALWAYS:
        if pattern.search(command):
            return kind
    for pattern, kind in _GH_IF_PROSE:
        if pattern.search(command) and _GH_PROSE_FLAG.search(command):
            return kind
    return ""


def artifact_kind(tool_name: str, tool_input: dict[str, Any]) -> str:
    """The short-form artifact this call writes, or empty when it writes none."""
    if tool_name in {"Bash", "PowerShell"}:
        return _command_kind(str(tool_input.get("command", "")))
    parts = tool_name.split("__")
    if len(parts) != 3 or parts[0] != "mcp" or "gitlab" not in parts[1].lower():
        return ""
    kind = _GITLAB_TOOLS.get(parts[2], "")
    if not kind or tool_input.get("dry_run"):
        return ""
    if parts[2].startswith("update_") and not any(tool_input.get(f) for f in _PROSE_FIELDS):
        return ""
    return kind


def first_of_kind(session_id: str, kind: str, state_dir: Path = _STATE_DIR) -> bool:
    """Record *kind* for *session_id*; True only when this is its first write and the record stuck."""
    if not session_id:
        return False
    path = state_dir / (re.sub(r"[^A-Za-z0-9_-]", "_", session_id) + ".json")
    try:
        seen = set(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        seen = set()
    if kind in seen:
        return False
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sorted(seen | {kind})), encoding="utf-8")
    except OSError:
        return False  # Without a record the retry would be denied too.
    return True


def decide(payload: dict[str, Any], references: Path = _REFERENCES, state_dir: Path = _STATE_DIR) -> dict[str, Any] | None:
    """The hook response for *payload*, or None to stay silent."""
    mode = os.environ.get("TECHDOCS_SHORT_FORM_GATE", "").strip().lower()
    if mode == "off":
        return None
    tool_input = payload.get("tool_input")
    kind = artifact_kind(str(payload.get("tool_name", "")), tool_input if isinstance(tool_input, dict) else {})
    if not kind:
        return None
    label, filename, heading = _SECTIONS[kind]
    checklist = section(filename, heading, references)
    if not checklist:
        return _context(f"Before sending a {label}, check it against its checklist in {_SKILL}.")
    if mode != "remind" and first_of_kind(str(payload.get("session_id", "")), kind, state_dir):
        return _deny(
            f"First {label} this session. Check the draft line by line against this checklist "
            f"from {_SKILL}, revise every line it fails, then send the call again. Later "
            f"{label}s pass with the checklist attached.\n\n{checklist}"
        )
    return _context(f"{label.capitalize()} checklist ({_SKILL}):\n\n{checklist}")


def _context(text: str) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}


def _deny(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def _unfenced_headings(body: str) -> int:
    count, fenced = 0, False
    for line in body.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        count += line.startswith("## ") and not fenced
    return count


def _self_test() -> int:
    """Run the built-in cases against scratch state; non-zero on any failure."""
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            failures.append(name)

    def denied(r: Any) -> bool:
        return bool(r) and r["hookSpecificOutput"].get("permissionDecision") == "deny"

    def text(r: Any) -> str:
        out = r["hookSpecificOutput"] if r else {}
        return out.get("permissionDecisionReason", "") + out.get("additionalContext", "")

    # The live references: a renamed heading must fail here, not silently fail open.
    for kind, (_, filename, heading) in _SECTIONS.items():
        body = section(filename, heading)
        check(f"live section for {kind} found", body.startswith(f"## {heading}"))
        check(f"live section for {kind} holds one heading", _unfenced_headings(body) == 1)
    check("issue section reaches past its fenced skeleton", "Checklist:" in section("templates-and-checklists.md", "Issue body"))

    os.environ.pop("TECHDOCS_SHORT_FORM_GATE", None)
    with tempfile.TemporaryDirectory() as scratch:
        state = Path(scratch) / "state"

        def run(tool: str, tool_input: dict[str, Any], session: str = "s1", refs: Path = _REFERENCES) -> Any:
            return decide({"tool_name": tool, "tool_input": tool_input, "session_id": session}, refs, state)

        commit = {"command": "git add -- a.md && git commit -F m.txt -- a.md"}
        first = run("Bash", commit)
        check("first commit denied", denied(first))
        check("denial carries the commit checklist", "Says in the body what the diff cannot show" in text(first))
        second = run("Bash", commit)
        check("second commit passes with the checklist", not denied(second) and "why the change exists" in text(second))
        check("another session is gated separately", denied(run("Bash", commit, session="s2")))
        check("PowerShell commit gated", denied(run("PowerShell", {"command": "git -C repo commit -m x"}, session="s3")))
        check("git add alone silent", run("Bash", {"command": "git add -- a.md"}) is None)
        check("commit-tree silent", run("Bash", {"command": "git commit-tree HEAD^{tree}"}) is None)
        check("commit --no-edit silent", run("Bash", {"command": "git commit --amend --no-edit"}) is None)
        check("commitment in prose silent", run("Bash", {"command": "echo 'git commitment'"}) is None)

        check("gh pr create gated", denied(run("Bash", {"command": "gh pr create --fill"}, session="gh")))
        check("gh issue create gated", denied(run("Bash", {"command": "gh issue create -t t -b b"}, session="gh")))
        check("gh pr edit with labels only silent", run("Bash", {"command": "gh pr edit 3 --add-label x"}) is None)
        check("gh pr review approve silent", run("Bash", {"command": "gh pr review 3 --approve"}) is None)
        check("gh pr review with body gated", denied(run("Bash", {"command": "gh pr review 3 --request-changes --body x"}, session="gh")))

        gl = "mcp__gitlab-local__"
        check("first issue body denied", denied(run(gl + "create_issue", {"title": "t", "description": "d"})))
        check("issue checklist attached later", "Opens with the problem" in text(run(gl + "update_issue", {"description": "d"})))
        check("state-only issue update silent", run(gl + "update_issue", {"state_event": "close"}) is None)
        check("milestone-only issue update silent", run(gl + "update_issue", {"milestone_id": "30"}) is None)
        check("description patch is prose", "Opens with the problem" in text(run(gl + "update_issue_description_patch", {"patch": "p"})))
        check("dry-run patch silent", run(gl + "update_issue_description_patch", {"patch": "p", "dry_run": True}) is None)
        cr = run(gl + "create_merge_request", {"title": "t", "description": "d"})
        check("first MR denied with the change-request checklist", denied(cr) and "Names what reviewers must check" in text(cr))
        check("labels-only MR update silent", run(gl + "update_merge_request", {"labels": ["a"]}) is None)
        thread = run(gl + "create_merge_request_thread", {"body": "b"})
        check("MR thread uses the review checklist", denied(thread) and "Marks itself blocking or optional" in text(thread))
        note = run(gl + "create_issue_note", {"body": "b"})
        check("issue note uses the short-format section", denied(note) and "bottom line, then impact" in text(note))
        check("short-format section stops at the next heading", "The editing pass" not in text(note))
        check("other server's create_issue silent", run("mcp__jira__create_issue", {"title": "t"}) is None)
        check("prose-free GitLab tool silent", run(gl + "create_issue_link", {"target": "x"}) is None)
        check("read tool silent", run(gl + "get_issue", {}) is None)

        missing = run("Bash", commit, session="s9", refs=Path(scratch) / "nowhere")
        check("missing checklist never denies", not denied(missing) and _SKILL in text(missing))
        check("no session id never denies", not denied(run("Bash", commit, session="")))
        blocked = Path(scratch) / "file"
        blocked.write_text("", encoding="utf-8")
        check("unwritable state never denies", not first_of_kind("s10", "commit", blocked))

        os.environ["TECHDOCS_SHORT_FORM_GATE"] = "remind"
        reminded = run("Bash", commit, session="s11")
        check("remind mode attaches without denying", not denied(reminded) and "why the change exists" in text(reminded))
        os.environ["TECHDOCS_SHORT_FORM_GATE"] = "off"
        check("off mode silent", run("Bash", commit, session="s12") is None)
        os.environ.pop("TECHDOCS_SHORT_FORM_GATE", None)

    for name in failures:
        print(f"FAIL {name}")
    print(f"{len(failures)} failed" if failures else "all checks passed")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    """Answer one PreToolUse call on stdin; exit 0 whatever happens."""
    if "--self-test" in argv:
        return _self_test()
    try:
        # Bytes, because Windows would decode stdin with the ANSI code page.
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        response = decide(payload) if isinstance(payload, dict) else None
    except Exception:  # noqa: BLE001 -- a hook bug must never block a write
        return 0
    if response:
        sys.stdout.write(json.dumps(response))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
