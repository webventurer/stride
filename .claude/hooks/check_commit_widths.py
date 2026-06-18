#!/usr/bin/env python3
"""Reject commit messages that break the 50/72 width rule (see /commit).

Invoked by do_commit.sh as `check_commit_widths.py --args <git commit
args>`: validates the message passed via -m/-F and exits 1 listing the
offending lines when the subject exceeds 50 chars or a wrappable body
line exceeds 72. Args that carry no new message (--amend --no-edit,
--fixup, editor commits) exit 0 — fail open, never block. Without
--args the message is read from stdin. Lines with no spaces (URLs,
paths) can't wrap and are exempt, as are subjects git generates
(Merge, fixup!, squash!).
"""

import sys

SUBJECT_MAX = 50
BODY_MAX = 72
EXEMPT_SUBJECTS = ("Merge ", "fixup!", "squash!")


def main() -> int:
    problems = width_violations(message_in(sys.argv[1:]))
    if problems:
        report(problems)
    return 1 if problems else 0


def message_in(argv: list) -> str:
    if argv[:1] != ["--args"]:
        return sys.stdin.read()
    return inline_message(argv[1:]) or file_message(argv[1:])


def inline_message(args: list) -> str:
    flagged = [
        value_after(args, i)
        for i, a in enumerate(args)
        if a in ("-m", "--message")
    ]
    equals = [a.split("=", 1)[1] for a in args if a.startswith("--message=")]
    return "\n\n".join(p for p in flagged + equals if p)


def file_message(args: list) -> str:
    flagged = [
        value_after(args, i)
        for i, a in enumerate(args)
        if a in ("-F", "--file")
    ]
    equals = [a.split("=", 1)[1] for a in args if a.startswith("--file=")]
    paths = [p for p in flagged + equals if p and p != "-"]
    return text_of(paths[0]) if paths else ""


def value_after(args: list, index: int) -> str | None:
    return args[index + 1] if index + 1 < len(args) else None


def text_of(path: str) -> str:
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


def width_violations(message: str) -> list:
    lines = message.splitlines()
    if not lines or lines[0].startswith(EXEMPT_SUBJECTS):
        return []
    return subject_violations(lines[0]) + body_violations(lines[1:])


def subject_violations(subject: str) -> list:
    if len(subject) <= SUBJECT_MAX:
        return []
    return [(1, len(subject), SUBJECT_MAX, subject)]


def body_violations(body: list) -> list:
    return [
        (i + 2, len(line), BODY_MAX, line)
        for i, line in enumerate(body)
        if overlong_prose(line)
    ]


def overlong_prose(line: str) -> bool:
    return len(line) > BODY_MAX and " " in line.strip()


def report(problems: list) -> None:
    print(
        "Commit blocked: message breaks the 50/72 rule (see /commit).",
        file=sys.stderr,
    )
    for lineno, length, limit, text in problems:
        print(
            f"  line {lineno}: {length} chars (max {limit}) — {text}",
            file=sys.stderr,
        )
    print(
        "Fix: wrap body at 72, subject at 50 — or pass a wrapped -F file.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    sys.exit(main())
