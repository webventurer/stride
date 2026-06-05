"""Guard against doc-vs-CLI flag drift in the /linear:* command markdown.

Every `linear_cli.py` invocation written in the command/reference docs must
name a real subcommand and real flags. When they drift, a user following the
command literally hits an error — e.g. quick.md once documented
`issue attach --pr` when the CLI only has `--url` (WB-509 / WB-520).

This introspects the click app directly (more robust than scraping --help)
and scans the command markdown for invocations.

Run with:
    python -m pytest .claude/tools/tests/test_command_doc_flags.py
"""

import re
import sys
from pathlib import Path

import click

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import linear_cli  # noqa: E402

COMMANDS_DIR = TOOLS_DIR.parent / "commands" / "linear"

# A flag: a `--long` name, or a single-letter `-x` short. Excludes values that
# look flaggish (e.g. the ISO duration `-P1W`, which is `--since`'s value).
FLAG = re.compile(r"(?:^|\s)(--[A-Za-z][A-Za-z0-9-]*|-[A-Za-z])(?=\s|=|$)")


def command_registry(group: click.Group, prefix: tuple = ()) -> dict:
    registry: dict = {}
    for name, cmd in group.commands.items():
        path = prefix + (name,)
        if isinstance(cmd, click.Group):
            registry.update(command_registry(cmd, path))
            continue
        flags = {opt for p in cmd.params if isinstance(p, click.Option) for opt in p.opts}
        registry[path] = flags | {"--help"}
    return registry


REGISTRY = command_registry(linear_cli.cli)
GROUPS = {name for name, cmd in linear_cli.cli.commands.items() if isinstance(cmd, click.Group)}


def invocation_segments(text: str):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        marker = lines[i].find("linear_cli.py")
        if marker == -1:
            i += 1
            continue
        segment = lines[i][marker + len("linear_cli.py"):]
        while segment.rstrip().endswith("\\"):
            i += 1
            segment = segment.rstrip()[:-1] + " " + (lines[i] if i < len(lines) else "")
        # Stop at a closing inline-code backtick or a shell pipe (jq et al. follow `|`).
        yield segment.split("`")[0].split("|")[0]
        i += 1


def command_path(segment: str) -> tuple | None:
    head = segment.strip()
    if not head or head[0] in "<-":  # generic `<verb>` form or a bare `--help`
        return None
    words = re.findall(r"[a-z][a-z0-9-]*", head)
    if not words:
        return None
    return tuple(words[:2]) if words[0] in GROUPS else (words[0],)


def drift_in(path: Path) -> list:
    findings = []
    for segment in invocation_segments(path.read_text()):
        cmd = command_path(segment)
        if cmd is None:
            continue
        if cmd not in REGISTRY:
            findings.append((path.name, " ".join(cmd), "<unknown subcommand>"))
            continue
        findings += [
            (path.name, " ".join(cmd), flag.split("=")[0])
            for flag in FLAG.findall(segment)
            if flag.split("=")[0] not in REGISTRY[cmd]
        ]
    return findings


def test_command_docs_reference_only_real_cli_flags():
    drift = [f for md in sorted(COMMANDS_DIR.rglob("*.md")) for f in drift_in(md)]
    assert not drift, "Doc-vs-CLI drift — docs reference flags/subcommands the CLI lacks:\n" + "\n".join(
        f"  {name}: `{cmd}` → {flag}" for name, cmd, flag in drift
    )
