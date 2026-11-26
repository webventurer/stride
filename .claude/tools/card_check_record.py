"""
The record a card check leaves on its card, and what the next start check has left to look at.

A check record is a comment saying when `main` was read and which wording was
checked. `/linear:start` reads the newest one to decide whether the card needs
the full start check, a check of what changed since, or none.
"""

import hashlib
import re
import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

MAIN_CHANGES_SCRIPT = Path(__file__).parent / "main_changes_since.sh"

TIME = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z"
RECORD_LINE = re.compile(
    rf"\*\*Card checked\*\* against `main` as of ({TIME})\. "
    r"Wording fingerprint: `([0-9a-f]+)`\."
)


def wording_fingerprint(card: dict) -> str:
    wording = f"{card['title']}\n\n{card.get('description') or ''}"
    return hashlib.sha256(wording.encode()).hexdigest()[:12]


def record_body(card: dict, read_at: str, findings: str = "") -> str:
    if not re.fullmatch(TIME, read_at):
        raise ValueError(f"Not a time like 2026-01-31T09:00:00Z: {read_at!r}")
    line = (
        f"**Card checked** against `main` as of {read_at}. "
        f"Wording fingerprint: `{wording_fingerprint(card)}`."
    )
    findings = findings.strip()
    return f"{line}\n\n{findings}" if findings else line


def check_scope(
    card: dict,
    comments: list[dict],
    sibling_comments: Callable[[], list[dict]],
    main_commits: Callable[[str], list[str]],
) -> dict:
    record = latest_record(comments)
    if record is None or record[2] != wording_fingerprint(card):
        return {"check": "full"}
    read_at = record[1]
    changed = (
        main_commits(read_at)
        or posted_since(comments, read_at)
        or posted_since(sibling_comments(), read_at)
    )
    return {"check": "changes" if changed else "none", "since": read_at}


def latest_record(comments: list[dict]) -> re.Match | None:
    newest_first = sorted(comments, key=lambda c: c["createdAt"], reverse=True)
    matches = (RECORD_LINE.match(c["body"]) for c in newest_first)
    return next((match for match in matches if match), None)


def posted_since(comments: list[dict], since: str) -> list[dict]:
    return [
        c
        for c in comments
        if not RECORD_LINE.match(c["body"])
        and as_time(c["createdAt"]) > as_time(since)
    ]


def as_time(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def main_commits_since(since: str) -> list[str]:
    listing = subprocess.run(
        [str(MAIN_CHANGES_SCRIPT), since],
        capture_output=True,
        text=True,
        check=True,
    )
    return listing.stdout.splitlines()
