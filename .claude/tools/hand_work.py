"""
Reads the work a person is doing by hand in the main folder.

A batch must not start a card that edits a file the person has changed there
and not yet pushed. `files_in_hand` lists those files: uncommitted changes,
staged or untracked, and the files changed by commits the folder's current
branch has and its upstream lacks (`origin/main` when it has no upstream).
`files_named` reads the files a card names in its "What we'll do" section, and
`overlap` says which of the person's files a set of names reaches.

Two commands serve the coordinator of a batch:

    hand_work.py overlap <main-folder>             # file paths on stdin
    hand_work.py replay <main-folder> <scratch>    # prints clean or conflict: ...

`overlap` prints each of the person's files the stdin paths reach. `replay`
builds a scratch worktree at `origin/main`, replays the person's unpushed
commits there and checks their uncommitted changes still apply. It never
changes the main folder's files, `HEAD`, index or stash.
"""

import re
import subprocess
import sys
from pathlib import Path

FILE_NAME_RE = re.compile(r"(?<![\w/.-])([\w./-]*[\w-]\.[A-Za-z]\w{0,4})(?!\w)")
DOTFILE_RE = re.compile(r"(?<![\w/.-])(\.[A-Za-z][\w-]*)(?![\w/.])")
BACKTICKED_RE = re.compile(r"`([^`\s]+)`")
NAMING_HEADINGS = ("### What we'll do", "### Assumptions to confirm")
PATCH_FAILURE_RES = (
    re.compile(r"error: patch failed: (.+?):\d+"),
    re.compile(
        r"error: (.+?): (?:patch does not apply|No such file or directory"
        r"|already exists in working directory)"
    ),
)


def files_named(description: str) -> set[str]:
    text = "\n".join(
        description.partition(heading)[2].split("\n### ")[0]
        for heading in NAMING_HEADINGS
    )
    found = (
        FILE_NAME_RE.findall(text)
        + DOTFILE_RE.findall(text)
        + BACKTICKED_RE.findall(text)
    )
    names = {re.sub(r"^(\./|/)+", "", name) for name in found}
    return names - {""}


def overlap(named: set[str], in_hand: set[str]) -> list[str]:
    return sorted(
        path
        for path in in_hand
        if any(path == name or path.endswith("/" + name) for name in named)
    )


def run_git(
    folder: Path, *args: str, stdin: bytes | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=stride",
            "-c",
            "user.email=stride@localhost",
            "--no-optional-locks",
            "-C",
            str(folder),
            *args,
        ],
        input=stdin,
        capture_output=True,
        check=True,
    )


def git_out(folder: Path, *args: str) -> str:
    return run_git(folder, *args).stdout.decode()


def main_folder() -> Path:
    common = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()
    return Path(common).parent


def files_in_hand(folder: Path) -> set[str]:
    return uncommitted_files(folder) | unpushed_files(folder)


def uncommitted_files(folder: Path) -> set[str]:
    entries = git_out(
        folder, "status", "--porcelain", "-z", "--untracked-files=all"
    ).split("\0")
    files: set[str] = set()
    renamed = False
    for entry in entries:
        if not entry:
            continue
        if renamed:
            files.add(entry)
            renamed = False
            continue
        files.add(entry[3:])
        renamed = entry[0] in "RC"
    return files


def unpushed_files(folder: Path) -> set[str]:
    try:
        diff = git_out(
            folder,
            "diff",
            "--name-only",
            "--no-renames",
            "-z",
            f"{unpushed_base(folder)}...HEAD",
        )
    except subprocess.CalledProcessError:
        return set()
    return {path for path in diff.split("\0") if path}


def unpushed_base(folder: Path) -> str:
    try:
        return git_out(
            folder, "rev-parse", "--abbrev-ref", "@{upstream}"
        ).strip()
    except subprocess.CalledProcessError:
        return "origin/main"


def replay(folder: Path, scratch: Path) -> list[str]:
    run_git(folder, "fetch", "--quiet", "origin", "main")
    unpushed = git_out(
        folder,
        "log",
        "--reverse",
        "--no-merges",
        "--format=%H",
        "origin/main..HEAD",
    ).split()
    uncommitted = run_git(folder, "diff", "HEAD", "--binary").stdout
    untracked = git_out(
        folder, "ls-files", "--others", "--exclude-standard", "-z"
    ).split("\0")
    run_git(folder, "worktree", "add", "--detach", str(scratch), "origin/main")
    try:
        return unique(
            cherry_pick_conflicts(scratch, unpushed)
            + patch_conflicts(scratch, uncommitted)
            + [p for p in untracked if p and (scratch / p).exists()]
        )
    finally:
        run_git(scratch, "reset", "--hard", "HEAD")
        run_git(folder, "worktree", "remove", str(scratch))


def unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def cherry_pick_conflicts(scratch: Path, commits: list[str]) -> list[str]:
    conflicts: list[str] = []
    for commit in commits:
        try:
            run_git(scratch, "cherry-pick", "--keep-redundant-commits", commit)
        except subprocess.CalledProcessError:
            clashing = git_out(
                scratch, "diff", "--name-only", "--diff-filter=U"
            )
            conflicts += clashing.split() or [commit[:7]]
            run_git(scratch, "cherry-pick", "--abort")
    return conflicts


def patch_conflicts(scratch: Path, patch: bytes) -> list[str]:
    if not patch:
        return []
    try:
        run_git(scratch, "apply", "--check", stdin=patch)
    except subprocess.CalledProcessError as error:
        failed = error.stderr.decode()
        paths = [m for r in PATCH_FAILURE_RES for m in r.findall(failed)]
        return sorted(set(paths)) or ["the uncommitted changes"]
    return []


def replay_report(conflicts: list[str]) -> str:
    return "conflict: " + ", ".join(conflicts) if conflicts else "clean"


def main(argv: list[str]) -> int:
    command, *args = argv
    if command == "overlap":
        paths = {line.strip() for line in sys.stdin if line.strip()}
        print("\n".join(overlap(paths, files_in_hand(Path(args[0])))))
        return 0
    if command == "replay":
        print(replay_report(replay(Path(args[0]), Path(args[1]))))
        return 0
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
