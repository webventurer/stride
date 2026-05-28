#!/usr/bin/env python3
# /// script
# dependencies = ["click"]
# ///
"""Weekly changelog from git log.

Reads commits in a configurable window (default 7 days), picks the top
N features by aggregate diff size, and renders a two-paragraph overview.

    uv run .claude/tools/changelog.py
    uv run .claude/tools/changelog.py --days 14 --top 5
    uv run .claude/tools/changelog.py --output CHANGELOG.md
"""

import subprocess
from collections import namedtuple
from pathlib import Path

import click

Commit = namedtuple("Commit", ["sha", "subject", "insertions", "deletions"])


def git_log_since(days: int) -> list[Commit]:
    out = subprocess.run(
        ["git", "log", f"--since={days} days ago", "--no-merges",
         "--pretty=format:%H|%s", "--numstat"],
        capture_output=True, text=True, check=True,
    ).stdout
    return parse_log(out)


def parse_log(text: str) -> list[Commit]:
    commits, current = [], None
    for line in text.splitlines():
        if is_header(line):
            if current:
                commits.append(current)
            sha, subject = line.split("|", 1)
            current = Commit(sha, subject, 0, 0)
        elif current and (delta := parse_numstat(line)):
            current = current._replace(
                insertions=current.insertions + delta[0],
                deletions=current.deletions + delta[1],
            )
    if current:
        commits.append(current)
    return commits


def is_header(line: str) -> bool:
    return "|" in line and len(line.split("|", 1)[0]) == 40


def parse_numstat(line: str) -> tuple[int, int] | None:
    parts = line.split("\t")
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[0]), int(parts[1])
    return None


def features(commits: list[Commit]) -> list[Commit]:
    return [c for c in commits if c.subject.startswith("feat:")]


def top_n(commits: list[Commit], n: int) -> list[Commit]:
    return sorted(commits, key=lambda c: c.insertions + c.deletions, reverse=True)[:n]


def group_by_type(commits: list[Commit]) -> dict[str, int]:
    types: dict[str, int] = {}
    for c in commits:
        prefix = c.subject.split(":", 1)[0] if ":" in c.subject else "other"
        types[prefix] = types.get(prefix, 0) + 1
    return types


def summarise_non_feature_types(types: dict[str, int]) -> str:
    others = sorted(((k, v) for k, v in types.items() if k != "feat"),
                    key=lambda kv: kv[1], reverse=True)[:3]
    return ", ".join(f"{v} {k}" for k, v in others) if others else "minor work"


def render_top(top: list[Commit]) -> str:
    return "\n".join(
        f"- **{c.subject.removeprefix('feat:').strip()}** "
        f"(+{c.insertions}/-{c.deletions}, {c.insertions + c.deletions} lines changed)"
        for c in top
    )


def render_overview(commits: list[Commit], days: int) -> str:
    feat_count = len(features(commits))
    others = summarise_non_feature_types(group_by_type(commits))
    para1 = (
        f"Over the past {days} days, {len(commits)} commits landed across the "
        f"codebase. Of those, {feat_count} were new features, with the rest "
        f"covering {others}. The largest changes by diff size — the ones most "
        f"likely to be felt by a user or a downstream consumer — are highlighted above."
    )
    para2 = (
        "The week's work concentrated on shipping useful additions while keeping "
        "the existing surface stable. Feature commits brought new capability online, "
        "and supporting commits filled in tests, docs, and refactors around them. "
        "Read the headlines for the substance, then drill into `git log` for the "
        "exact diffs and rationale."
    )
    return f"{para1}\n\n{para2}"


def render(days: int, top: int) -> str:
    commits = git_log_since(days)
    if not commits:
        return f"# Weekly changelog\n\nNo commits in the past {days} days.\n"
    feats = top_n(features(commits), top)
    return (
        f"# Weekly changelog\n\n"
        f"*Window: past {days} days. {len(commits)} commits, "
        f"{len(features(commits))} feature commits.*\n\n"
        f"## Top {len(feats)} feature changes\n\n"
        f"{render_top(feats)}\n\n"
        f"## Overview\n\n"
        f"{render_overview(commits, days)}\n"
    )


@click.command()
@click.option("--days", default=7, type=int, help="Window in days (default 7).")
@click.option("--top", default=5, type=int, help="How many feature changes to highlight.")
@click.option("--output", type=click.Path(), help="Write to file instead of stdout.")
def main(days: int, top: int, output: str | None) -> None:
    text = render(days, top)
    if output:
        Path(output).write_text(text)
        click.echo(f"Wrote {output}")
    else:
        click.echo(text)


if __name__ == "__main__":
    main()
