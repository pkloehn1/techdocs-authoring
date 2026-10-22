#!/usr/bin/env python3
"""Hold Markdown prose to the repository's MD013 line length, and answer markdownlint findings.

Three events, one script:

- PreToolUse on Write and Edit of a ``.md`` or ``.markdown`` file: compute the
  text the call leaves behind and deny it when it adds a line over the
  repository's MD013 limit, listing each line with the fix guidance.
- PostToolUse and PostToolUseFailure on Bash and PowerShell: when the output
  holds a markdownlint finding (``file.md:110:201 error MD013/line-length``),
  attach the guidance. A failing linter exits non-zero, which Claude Code
  reports as PostToolUseFailure, so both events are needed.
- UserPromptSubmit: the same, for linter output the operator pastes.

The limit comes from the repository's own markdownlint config, found the way
MegaLinter and markdownlint-cli2 find it, and the guidance from this plugin's
style-guide reference at call time. Without a config the gate stays silent.

Every failure path allows the call: no config, an unreadable file, an old
string that does not match, or any exception.

Set TECHDOCS_MARKDOWN_LINT_GATE=remind to turn the edit denial into context, or
=off to silence all three events.

Stdlib only. Self-test::

    python hooks/markdown_lint_gate.py --self-test
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from short_form_gate import _REFERENCES, _SKILL, section

# Rule -> (reference file, heading prefix of its fix section).
_GUIDANCE: dict[str, tuple[str, str]] = {
    "MD013": ("style-guide.md", "Fixing a line-length finding"),
}

_MD_SUFFIXES = (".md", ".markdown")
_NATIVE_CONFIGS = (".markdownlint.jsonc", ".markdownlint.json", ".markdownlint.yaml", ".markdownlint.yml")
_MEGALINTER_CONFIGS = (".mega-linter.yml", ".mega-linter.yaml")

# `file.md:110:201 error MD013/line-length ...` from markdownlint-cli, -cli2 and
# MegaLinter. The location prefix keeps a rule named in prose from matching.
_FINDING = re.compile(r":\d+(?::\d+)?\s+(?:error\s+|warning\s+)?(MD0\d\d)/([a-z][a-z-]*)")

# shortcut: an inline markdownlint comment can change any rule for any range;
# the gate stays silent on such files rather than model the comment grammar.
_INLINE_CONFIG = re.compile(r"<!--\s*markdownlint-")

# From markdownlint's lib/md013.mjs.
_NOT_WRAPPABLE = re.compile(r"^(?:[#>\s]*\s)?\S*$")
_LAST_RUN = re.compile(r"\S*$")

_FENCE = re.compile(r"^\s*(?:>\s*)*(`{3,}|~{3,})(.*)$")
_INDENTED = re.compile(r"^(?: {4}|\t)")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
_ATX = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")
_SETEXT = re.compile(r"^ {0,3}(?:=+|-+)\s*$")
_TABLE_DELIMITER = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
_DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*\S")
# A line holding only a link, image or autolink, optionally in a list item,
# a blockquote or (strong) emphasis.
_LINK_ONLY = re.compile(
    r"^\s*(?:(?:[-*+]|\d+[.)])\s+|>\s*)*[*_]*"
    r"(?:!?\[[^\]]*\](?:\([^)]*\)|\[[^\]]*\])|<[a-z][\w+.-]*:[^>\s]*>|https?://\S+)"
    r"[*_]*\s*$",
    re.IGNORECASE,
)

_JSONC_NOISE = re.compile(r'("(?:\\.|[^"\\])*")|//[^\n]*|/\*[\s\S]*?\*/')


def _scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value in ("true", "false"):
        return value == "true"
    try:
        return int(value)
    except ValueError:
        return value


def _yaml(text: str) -> dict[str, Any]:
    """Top-level keys of a markdownlint or MegaLinter YAML file, one mapping level deep.

    shortcut: covers the block and flow mappings these configs use, not YAML;
    move to a real parser if a config needs anchors, lists of maps or multi-line scalars.
    """
    out: dict[str, Any] = {}
    parent: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = re.sub(r"(?:^|\s)#.*$", "", raw).rstrip()
        if line.strip() in ("", "---", "..."):
            continue
        m = re.match(r"^(\s*)(\"[^\"]*\"|'[^']*'|[^\s:]+)\s*:(?:\s+(.*))?$", line)
        if not m:
            continue
        key, value = m[2].strip("\"'"), (m[3] or "").strip()
        if m[1]:
            if parent is not None and value:
                parent[key] = _scalar(value)
        elif not value:
            parent = out[key] = {}
        elif value.startswith("{") and value.endswith("}"):
            pairs = (p.partition(":") for p in value[1:-1].split(",") if ":" in p)
            out[key], parent = {k.strip().strip("\"'"): _scalar(v) for k, _, v in pairs}, None
        else:
            out[key], parent = _scalar(value), None
    return out


def _jsonc(text: str) -> dict[str, Any]:
    text = _JSONC_NOISE.sub(lambda m: m[1] or "", text)
    data = json.loads(re.sub(r",(\s*[}\]])", r"\1", text))
    return data if isinstance(data, dict) else {}


def load_config(path: Path, depth: int = 0) -> dict[str, Any]:
    """A markdownlint config file, with `extends` merged shallowly as markdownlint does."""
    text = path.read_text(encoding="utf-8")
    config = _jsonc(text) if path.suffix in (".json", ".jsonc") else _yaml(text)
    base = config.pop("extends", None)
    if isinstance(base, str) and depth < 5:
        config = {**load_config(path.parent / base, depth + 1), **config}
    return config


def find_config(md_file: Path) -> Path | None:
    """The markdownlint config that governs *md_file*, or None.

    MegaLinter first, when the repository runs it: its config file name in the
    root, then under its rules path. Otherwise markdownlint-cli2's search: a
    `.markdownlint.*` file in the file's directory or any parent up to the root.
    shortcut: `.markdownlint-cli2.*` and `.markdownlintrc` are not read; add them
    if a repository keeps its MD013 settings there.
    """
    root = next((d for d in md_file.parents if (d / ".git").exists()), None)
    if root is None:
        return None
    for name in _MEGALINTER_CONFIGS:
        if (root / name).is_file():
            mega = _yaml((root / name).read_text(encoding="utf-8"))
            filename = str(mega.get("MARKDOWN_MARKDOWNLINT_CONFIG_FILE") or ".markdownlint.json")
            if filename != "LINTER_DEFAULT":
                rules = str(mega.get("MARKDOWN_MARKDOWNLINT_RULES_PATH") or mega.get("LINTER_RULES_PATH") or ".github/linters")
                for candidate in (root / filename, root / rules / filename):
                    if candidate.is_file():
                        return candidate
            break
    for directory in md_file.parents:
        for name in _NATIVE_CONFIGS:
            if (directory / name).is_file():
                return directory / name
        if directory == root:
            break
    return None


def md013_options(config: dict[str, Any]) -> dict[str, Any] | None:
    """MD013's parameters under *config*, or None when the rule is off."""
    upper = {str(k).upper(): v for k, v in config.items()}
    value = upper.get("MD013", upper.get("LINE-LENGTH", upper.get("LINE_LENGTH", upper.get("DEFAULT", True))))
    if isinstance(value, dict):
        return value
    return {} if value else None


def _classify(lines: list[str]) -> list[str]:
    """Per line: front, code, table, heading, definition or text."""
    kinds = ["text"] * len(lines)
    start = 0
    if lines and lines[0].strip() == "---":
        end = next((j for j in range(1, len(lines)) if lines[j].strip() in ("---", "...")), 0)
        if end:
            kinds[: end + 1] = ["front"] * (end + 1)
            start = end + 1
    fence, in_table, in_list = "", False, False
    for j in range(start, len(lines)):
        line = lines[j]
        m = _FENCE.match(line)
        if line.strip() and not _INDENTED.match(line):
            in_list = bool(_LIST_ITEM.match(line))
        if fence:
            kinds[j] = "code"
            if m and m[1][0] == fence[0] and len(m[1]) >= len(fence) and not m[2].strip():
                fence = ""
        elif m and not (m[1][0] == "`" and "`" in m[2]):
            fence, in_table, kinds[j] = m[1], False, "code"
        elif not line.strip():
            in_table = False
        elif _INDENTED.match(line) and not in_list and (j == start or kinds[j - 1] == "code" or not lines[j - 1].strip()):
            kinds[j] = "code"  # an indented code block cannot interrupt a paragraph; in a list it is item text
        elif in_table or ("|" in line and j + 1 < len(lines) and "-" in lines[j + 1] and _TABLE_DELIMITER.match(lines[j + 1])):
            in_table, kinds[j] = True, "table"
        elif _ATX.match(line):
            kinds[j] = "heading"
        elif _SETEXT.match(line) and j > start and kinds[j - 1] == "text" and lines[j - 1].strip():
            kinds[j] = kinds[j - 1] = "heading"
        elif _DEFINITION.match(line):
            kinds[j] = "definition"
    return kinds


def _length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2  # markdownlint counts UTF-16 code units


def violations(text: str, opts: dict[str, Any]) -> list[tuple[int, int, int, str]]:
    """(line number, length, limit, line) for each line MD013 would flag under *opts*.

    Mirrors markdownlint's lib/md013.mjs. shortcut: tables and code blocks are
    found by line shape, not a CommonMark parse, and code nested in a list is
    read as text; parse properly if a false denial shows up in real use.
    """
    limit = int(opts.get("line_length", 80))
    limits = {"heading": int(opts.get("heading_line_length", limit)), "code": int(opts.get("code_block_line_length", limit))}
    strict, stern = bool(opts.get("strict")), bool(opts.get("stern"))
    excluded = {kind for kind, key in (("code", "code_blocks"), ("table", "tables"), ("heading", "headings")) if not opts.get(key, True)}
    lines = re.split(r"\r\n|\r|\n", text)
    found = []
    for number, (line, kind) in enumerate(zip(lines, _classify(lines)), 1):
        maximum = limits.get(kind, limit)
        if kind in ("front", "definition") or kind in excluded or maximum <= 0:
            continue
        # md013.mjs drops the link-only exemption under strict, whatever the rule's doc says.
        if not strict and ((stern and _NOT_WRAPPABLE.match(line)) or _LINK_ONLY.match(line)):
            continue
        measured = line if strict or stern else _LAST_RUN.sub("#", line, count=1)
        if _length(measured) > maximum:
            found.append((number, _length(line), maximum, line))
    return found


def guidance(rules: set[tuple[str, str]], references: Path = _REFERENCES) -> str:
    """The fix guidance for each (rule, alias) pair, from the skill's references."""
    parts = []
    for rule, alias in sorted(rules):
        body = section(*_GUIDANCE[rule], references) if rule in _GUIDANCE else ""
        parts.append(body or f"{rule}/{alias}: fix the reported lines against the repository's own markdownlint config, then re-run its linter.")
    return "\n\n".join(parts)


def _edit_gate(payload: dict[str, Any], mode: str, references: Path) -> dict[str, Any] | None:
    tool_input = payload.get("tool_input")
    tool = payload.get("tool_name")
    if not isinstance(tool_input, dict) or tool not in ("Write", "Edit"):
        return None
    path = Path(str(tool_input.get("file_path", "")))
    if path.suffix.lower() not in _MD_SUFFIXES:
        return None
    try:
        before = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError:
        before = ""
    if tool == "Write":
        after = str(tool_input.get("content", ""))
    else:
        old, new = str(tool_input.get("old_string", "")), str(tool_input.get("new_string", ""))
        if not old or old not in before:
            return None
        after = before.replace(old, new) if tool_input.get("replace_all") else before.replace(old, new, 1)
    config = find_config(path)
    opts = md013_options(load_config(config)) if config else None
    if opts is None or _INLINE_CONFIG.search(after):
        return None
    # A line already over the limit is not this edit's doing; each one excuses one copy.
    existing = Counter(v[3] for v in violations(before, opts))
    added = []
    for v in violations(after, opts):
        if existing[v[3]]:
            existing[v[3]] -= 1
        else:
            added.append(v)
    if not added:
        return None
    listing = "\n".join(f"- line {n}: {length} characters (limit {limit})" for n, length, limit, _ in added)
    message = (
        f"This {tool} leaves {path.name} with lines over the MD013 line length set in {config}. "
        f"Rewrite them, then send the call again:\n{listing}\n\n"
        f"From {_SKILL}:\n\n{guidance({('MD013', 'line-length')}, references)}"
    )
    if mode == "remind":
        return _context("PreToolUse", message)
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": message}}


def decide(payload: dict[str, Any], references: Path = _REFERENCES) -> dict[str, Any] | None:
    """The hook response for *payload*, or None to stay silent."""
    mode = os.environ.get("TECHDOCS_MARKDOWN_LINT_GATE", "").strip().lower()
    event = str(payload.get("hook_event_name", ""))
    if mode == "off":
        return None
    if event == "PreToolUse":
        return _edit_gate(payload, mode, references)
    if event in ("PostToolUse", "PostToolUseFailure"):
        text = json.dumps(payload.get("tool_response"), ensure_ascii=False) + str(payload.get("error", ""))
    elif event == "UserPromptSubmit":
        text = str(payload.get("prompt", ""))
    else:
        return None
    rules = {(m[1], m[2]) for m in _FINDING.finditer(text)}
    if not rules:
        return None
    names = ", ".join(f"{r}/{a}" for r, a in sorted(rules))
    return _context(event, f"markdownlint findings: {names}. Fix guidance from {_SKILL}:\n\n{guidance(rules, references)}")


def _context(event: str, text: str) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def _self_test() -> int:
    """Run the built-in cases against scratch repositories; non-zero on any failure."""
    failures: list[str] = []

    def check(name: str, ok: Any) -> None:
        if not ok:
            failures.append(name)

    def out(r: Any) -> dict[str, Any]:
        return r["hookSpecificOutput"] if r else {}

    def denied(r: Any) -> bool:
        return out(r).get("permissionDecision") == "deny"

    def text(r: Any) -> str:
        return out(r).get("permissionDecisionReason", "") + out(r).get("additionalContext", "")

    # The live reference: a renamed heading must fail here, not silently drop the guidance.
    for rule, (filename, heading) in _GUIDANCE.items():
        check(f"live guidance for {rule} found", section(filename, heading).startswith(f"## {heading}"))

    prose = " ".join(["word"] * 60)[:271]  # 271 characters with spaces past any limit
    check("fixture prose is 271 characters", len(prose) == 271)
    url_line = "See " + "https://example.com/" + "a" * 250
    os.environ.pop("TECHDOCS_MARKDOWN_LINT_GATE", None)

    with tempfile.TemporaryDirectory() as scratch:
        base = Path(scratch)

        def repo(name: str, files: dict[str, str]) -> Path:
            root = base / name
            (root / ".git").mkdir(parents=True)
            for rel, body in files.items():
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(body, encoding="utf-8")
            return root

        mega = {
            ".mega-linter.yml": "---\nLINTER_RULES_PATH: .linters\nMARKDOWN_MARKDOWNLINT_CONFIG_FILE: .markdownlint.yml\n",
            ".linters/.markdownlint.yml": "---\n# comment\nMD013:\n  line_length: 200\n  tables: false\n",
        }
        ml = repo("mega", mega)

        def write(root: Path, body: str, name: str = "README.md", event: str = "PreToolUse") -> Any:
            payload = {
                "hook_event_name": event,
                "tool_name": "Write",
                "tool_input": {"file_path": str(root / name), "content": body},
            }
            return decide(payload)

        # Discovery and config parsing.
        check("MegaLinter rules path found", find_config(ml / "docs" / "a.md") == ml / ".linters" / ".markdownlint.yml")
        check("YAML MD013 options read", (md013_options(load_config(ml / ".linters" / ".markdownlint.yml")) or {}).get("line_length") == 200)
        check("no .git means no config", find_config(base / "loose" / "a.md") is None)
        check("MD013 false disables", md013_options({"MD013": False}) is None)
        check("alias line-length read", md013_options({"line-length": {"line_length": 9}}) == {"line_length": 9})
        check("default false without MD013 disables", md013_options({"default": False}) is None)
        check("rule absent defaults on", md013_options({"MD033": False}) == {})

        # The edit gate.
        r = write(ml, f"# Title\n\n{prose}\n")
        check("271-char prose denied under 200", denied(r))
        check("denial names line, length and limit", "line 3: 271 characters (limit 200)" in text(r))
        check("denial carries the live guidance", "one sentence per line" in text(r))
        check("prose within limit passes", write(ml, "# Title\n\nShort line.\n") is None)
        check("table exempt when tables false", write(ml, f"| a | b |\n| --- | --- |\n| {prose} | x |\n") is None)
        check("long trailing URL passes by default", write(ml, url_line + "\n") is None)
        check("link-only line passes", write(ml, f"[{prose}](https://example.com)\n") is None)
        check("reference definition passes", write(ml, f"[ref]: https://example.com/{'a' * 300} \"t\"\n") is None)
        check("front matter skipped", write(ml, f"---\ntitle: {prose}\n---\n\nok\n") is None)
        check("inline disable fails open", write(ml, f"<!-- markdownlint-disable MD013 -->\n{prose}\n") is None)
        check("non-Markdown file silent", write(ml, prose, name="notes.txt") is None)
        check("code block checked by default", denied(write(ml, f"```text\n{prose}\n```\n")))

        plain = repo("plain", {".markdownlint.jsonc": '// c\n{ "MD013": { "line_length": 80, "code_blocks": false, "headings": false, }, }\n'})
        check("native JSONC config found", find_config(plain / "a.md") == plain / ".markdownlint.jsonc")
        check("code block exempt when code_blocks false", write(plain, f"```text\n{prose}\n```\n") is None)
        check("tilde fence exempt too", write(plain, f"~~~\n{prose}\n~~~\n") is None)
        check("indented code exempt too", write(plain, f"Text.\n\n    {prose}\n") is None)
        check("indented list text still checked", denied(write(plain, f"- item\n\n    {prose}\n")))
        check("indented line inside a paragraph still checked", denied(write(plain, f"Text\n    {prose}\n")))
        check("heading exempt when headings false", write(plain, f"# {prose}\n") is None)
        check("setext heading exempt too", write(plain, f"{prose}\n===\n") is None)
        check("table checked when tables included", denied(write(plain, f"| a |\n| --- |\n| {prose} |\n")))
        check("default limit 80 applies", denied(write(plain, " ".join(["word"] * 20) + "\n")))

        strict = repo("strict", {".markdownlint.yaml": "MD013: {line_length: 40, strict: true}\n"})
        check("flow mapping read", (md013_options(load_config(strict / ".markdownlint.yaml")) or {}).get("strict") is True)
        check("strict flags a trailing URL", denied(write(strict, url_line + "\n")))
        stern = repo("stern", {".markdownlint.yml": "MD013:\n  line_length: 40\n  stern: true\n"})
        check("stern allows an unbroken line", write(stern, "x" * 60 + "\n") is None)
        check("stern flags a trailing URL", denied(write(stern, url_line + "\n")))
        ext = repo("ext", {".markdownlint.yml": "extends: base.yml\nMD033: false\n", "base.yml": "MD013: false\n"})
        check("extends inherits MD013 false", write(ext, prose + "\n") is None)
        off = repo("off", {".markdownlint.json": '{"MD013": false}'})
        check("MD013 false repo silent", write(off, prose + "\n") is None)
        check("repo without config silent", write(repo("none", {}), prose + "\n") is None)
        check("emoji count as two characters", violations("\U0001F600" * 41 + " x\n", {"line_length": 80}) != [])

        # Edit: applies old -> new to the current file and judges only lines it adds.
        doc = ml / "doc.md"
        doc.write_bytes(f"# Doc\r\n\r\n{prose}\r\n\r\nold\r\n".encode())

        def edit(old: str, new: str, replace_all: bool = False) -> Any:
            tool_input = {"file_path": str(doc), "old_string": old, "new_string": new, "replace_all": replace_all}
            return decide({"hook_event_name": "PreToolUse", "tool_name": "Edit", "tool_input": tool_input})

        check("edit beside an existing long line passes", edit("old", "new") is None)
        r = edit("old", prose)
        check("edit adding a long line denied", denied(r) and "line 5: 271" in text(r))
        check("edit with unmatched old string silent", edit("absent", prose) is None)
        doc.write_text("a\n\na\n", encoding="utf-8")
        check("replace_all reaches every match", "line 3:" in text(edit("a", prose, replace_all=True)))
        check("replace once reaches only the first", "line 3:" not in text(edit("a", prose)))

        os.environ["TECHDOCS_MARKDOWN_LINT_GATE"] = "remind"
        r = write(ml, prose + "\n")
        check("remind mode attaches without denying", not denied(r) and "line 1: 271" in text(r))
        os.environ["TECHDOCS_MARKDOWN_LINT_GATE"] = "off"
        check("off mode silent", write(ml, prose + "\n") is None)
        os.environ.pop("TECHDOCS_MARKDOWN_LINT_GATE", None)

        # Findings in tool output and in the prompt.
        finding = "README.md:110:201 error MD013/line-length Line length [Expected: 200; Actual: 271]"

        def shell(event: str, response: Any, extra: dict[str, Any] | None = None) -> Any:
            payload = {"hook_event_name": event, "tool_name": "Bash", "tool_input": {"command": "git push"}, "tool_response": response}
            return decide({**payload, **(extra or {})})

        r = shell("PostToolUse", {"stdout": finding, "stderr": "", "interrupted": False})
        check("PostToolUse attaches MD013 guidance", out(r).get("hookEventName") == "PostToolUse" and "one sentence per line" in text(r))
        r = shell("PostToolUseFailure", None, {"error": "Exit code 1\n" + finding})
        check("PostToolUseFailure attaches guidance", out(r).get("hookEventName") == "PostToolUseFailure" and "one sentence per line" in text(r))
        check("clean output silent", shell("PostToolUse", {"stdout": "all good"}) is None)
        check("rule name in prose silent", shell("PostToolUse", {"stdout": "see MD013/line-length docs"}) is None)
        r = shell("PostToolUse", {"stdout": "a.md:3 MD009/no-trailing-spaces Trailing spaces"})
        check("other rule gets the generic pointer", "MD009/no-trailing-spaces" in text(r) and "one sentence per line" not in text(r))
        r = decide({"hook_event_name": "UserPromptSubmit", "prompt": "push failed:\n" + finding})
        check("pasted finding attaches guidance", out(r).get("hookEventName") == "UserPromptSubmit" and "one sentence per line" in text(r))
        check("plain prompt silent", decide({"hook_event_name": "UserPromptSubmit", "prompt": "hello"}) is None)
        r = decide({"hook_event_name": "UserPromptSubmit", "prompt": finding}, base / "nowhere")
        check("missing guidance still points at the skill", _SKILL in text(r))
        os.environ["TECHDOCS_MARKDOWN_LINT_GATE"] = "off"
        check("off mode silences findings", decide({"hook_event_name": "UserPromptSubmit", "prompt": finding}) is None)
        os.environ.pop("TECHDOCS_MARKDOWN_LINT_GATE", None)

    for name in failures:
        print(f"FAIL {name}")
    print(f"{len(failures)} failed" if failures else "all checks passed")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    """Answer one hook call on stdin; exit 0 whatever happens."""
    if "--self-test" in argv:
        return _self_test()
    try:
        # Bytes, because Windows would decode stdin with the ANSI code page.
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        response = decide(payload) if isinstance(payload, dict) else None
    except Exception:  # noqa: BLE001 -- a hook bug must never block an edit
        return 0
    if response:
        sys.stdout.write(json.dumps(response))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
