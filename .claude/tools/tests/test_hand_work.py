"""Tests for hand_work — reading and replaying the work a person does by hand.

Run with:
    python -m pytest .claude/tools/tests/test_hand_work.py
"""

import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from hand_work import (  # noqa: E402
    files_in_hand,
    files_named,
    overlap,
    replay,
    replay_report,
)

GIT_IDENTITY = ["-c", "user.name=Test", "-c", "user.email=test@example.com"]


def git(folder: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *GIT_IDENTITY, "-C", str(folder), *args],
        capture_output=True,
        check=True,
        text=True,
    ).stdout


def commit_file(folder: Path, name: str, content: str, message: str = "change"):
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    git(folder, "add", name)
    git(folder, "commit", "-m", message)


def make_repos(tmp_path: Path) -> tuple[Path, Path]:
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)],
        capture_output=True,
        check=True,
    )
    seed = tmp_path / "seed"
    subprocess.run(
        ["git", "clone", str(origin), str(seed)],
        capture_output=True,
        check=True,
    )
    git(seed, "checkout", "-b", "main")
    commit_file(seed, "server.py", "one\ntwo\nthree\n", "seed")
    commit_file(seed, "report.py", "report\n", "seed report")
    git(seed, "push", "-u", "origin", "main")
    mine = tmp_path / "mine"
    subprocess.run(
        ["git", "clone", str(origin), str(mine)],
        capture_output=True,
        check=True,
    )
    return origin, mine


def push_another_change(tmp_path: Path, origin: Path, name: str, content: str):
    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", str(origin), str(other)],
        capture_output=True,
        check=True,
    )
    commit_file(other, name, content, "card merge")
    git(other, "push", "origin", "main")


def test_files_named_reads_names_from_the_what_well_do_section_only():
    description = (
        "### Why this matters\n\nMentions `skip.py`.\n\n"
        "### What we'll do\n\nEdit `a/b/server.py`, then `todo.md`.\n\n"
        "### Expected outcome\n\nMentions `later.py`.\n"
    )

    assert files_named(description) == {"a/b/server.py", "todo.md"}


def test_files_named_reads_an_auto_link_and_a_plain_name():
    description = (
        "### What we'll do\n\nEdit [server.py](<http://server.py>) and "
        "report.py. Done.\n"
    )

    assert files_named(description) == {"server.py", "report.py"}


def test_files_named_reads_the_assumptions_section_too():
    description = (
        "### What we'll do\n\nEdit `a.py`.\n\n"
        "### Assumptions to confirm\n\nThe flag lives in `b/config.toml`.\n"
    )

    assert files_named(description) == {"a.py", "b/config.toml"}


def test_files_named_reads_a_dotfile_a_backticked_name_and_a_dot_slash_path():
    description = (
        "### What we'll do\n\nAdd a line to .gitignore and `Makefile`, "
        "then edit ./src/app.py.\n"
    )

    assert files_named(description) == {".gitignore", "Makefile", "src/app.py"}


def test_files_named_finds_nothing_in_a_card_that_names_no_file():
    assert files_named("### What we'll do\n\nTidy the wording.\n") == set()


def test_overlap_matches_a_bare_name_at_a_path_boundary():
    assert overlap({"server.py"}, {"src/server.py", "src/myserver.py"}) == [
        "src/server.py"
    ]


def test_files_in_hand_lists_uncommitted_staged_and_untracked_files(tmp_path):
    _, mine = make_repos(tmp_path)
    (mine / "server.py").write_text("edited\n")
    (mine / "new.py").write_text("new\n")
    git(mine, "add", "new.py")
    (mine / "notes.txt").write_text("notes\n")

    assert files_in_hand(mine) == {"server.py", "new.py", "notes.txt"}


def test_files_in_hand_lists_files_of_unpushed_commits(tmp_path):
    _, mine = make_repos(tmp_path)
    commit_file(mine, "src/api.py", "api\n")

    assert files_in_hand(mine) == {"src/api.py"}


def test_files_in_hand_lists_both_names_of_a_file_an_unpushed_commit_renamed(
    tmp_path,
):
    _, mine = make_repos(tmp_path)
    git(mine, "mv", "report.py", "summary.py")
    git(mine, "commit", "-m", "rename")

    assert files_in_hand(mine) == {"report.py", "summary.py"}


def test_files_in_hand_is_empty_once_the_work_is_pushed(tmp_path):
    _, mine = make_repos(tmp_path)
    commit_file(mine, "src/api.py", "api\n")
    git(mine, "push", "origin", "main")

    assert files_in_hand(mine) == set()


def test_files_in_hand_counts_unpushed_commits_on_a_branch_other_than_main(
    tmp_path,
):
    _, mine = make_repos(tmp_path)
    git(mine, "checkout", "-b", "feature")
    commit_file(mine, "src/api.py", "api\n")

    assert files_in_hand(mine) == {"src/api.py"}


def test_replay_reports_clean_when_the_work_does_not_clash(tmp_path):
    origin, mine = make_repos(tmp_path)
    commit_file(mine, "report.py", "report\nmine\n")
    (mine / "server.py").write_text("one\ntwo\nthree\nedited\n")
    push_another_change(tmp_path, origin, "card.py", "card\n")

    assert replay_report(replay(mine, tmp_path / "scratch")) == "clean"


def test_replay_names_the_file_an_unpushed_commit_clashes_on(tmp_path):
    origin, mine = make_repos(tmp_path)
    commit_file(mine, "server.py", "one\nmine\nthree\n")
    push_another_change(tmp_path, origin, "server.py", "one\ncard\nthree\n")

    assert (
        replay_report(replay(mine, tmp_path / "scratch"))
        == "conflict: server.py"
    )


def test_replay_names_the_file_an_uncommitted_change_clashes_on(tmp_path):
    origin, mine = make_repos(tmp_path)
    (mine / "server.py").write_text("one\nmine\nthree\n")
    push_another_change(tmp_path, origin, "server.py", "one\ncard\nthree\n")

    assert (
        replay_report(replay(mine, tmp_path / "scratch"))
        == "conflict: server.py"
    )


def test_replay_names_every_unpushed_commit_that_clashes(tmp_path):
    origin, mine = make_repos(tmp_path)
    commit_file(mine, "server.py", "one\nmine\nthree\n")
    commit_file(mine, "report.py", "mine\n")
    push_another_change(tmp_path, origin, "server.py", "one\ncard\nthree\n")
    other = tmp_path / "other"
    commit_file(other, "report.py", "card\n")
    git(other, "push", "origin", "main")

    assert (
        replay_report(replay(mine, tmp_path / "scratch"))
        == "conflict: server.py, report.py"
    )


def test_replay_names_a_clash_in_the_uncommitted_changes_beside_a_commit_clash(
    tmp_path,
):
    origin, mine = make_repos(tmp_path)
    commit_file(mine, "server.py", "one\nmine\nthree\n")
    (mine / "report.py").write_text("edited\n")
    push_another_change(tmp_path, origin, "server.py", "one\ncard\nthree\n")
    other = tmp_path / "other"
    commit_file(other, "report.py", "card\n")
    git(other, "push", "origin", "main")

    assert (
        replay_report(replay(mine, tmp_path / "scratch"))
        == "conflict: server.py, report.py"
    )


def test_replay_names_a_staged_new_file_the_card_also_added(tmp_path):
    origin, mine = make_repos(tmp_path)
    (mine / "card.py").write_text("mine\n")
    git(mine, "add", "card.py")
    push_another_change(tmp_path, origin, "card.py", "card\n")

    assert (
        replay_report(replay(mine, tmp_path / "scratch")) == "conflict: card.py"
    )


def test_replay_reports_clean_for_an_unpushed_merge_commit(tmp_path):
    origin, mine = make_repos(tmp_path)
    git(mine, "checkout", "-b", "side")
    commit_file(mine, "side.py", "side\n")
    git(mine, "checkout", "main")
    commit_file(mine, "report.py", "report\nmain\n")
    git(mine, "merge", "--no-ff", "side", "-m", "merge side")
    push_another_change(tmp_path, origin, "card.py", "card\n")

    assert replay_report(replay(mine, tmp_path / "scratch")) == "clean"


def test_replay_names_a_file_the_card_deleted_that_the_person_edited(tmp_path):
    origin, mine = make_repos(tmp_path)
    (mine / "report.py").write_text("edited\n")
    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", str(origin), str(other)],
        capture_output=True,
        check=True,
    )
    git(other, "rm", "report.py")
    git(other, "commit", "-m", "card deletes report")
    git(other, "push", "origin", "main")

    assert (
        replay_report(replay(mine, tmp_path / "scratch"))
        == "conflict: report.py"
    )


def test_replay_names_an_untracked_file_the_card_also_added(tmp_path):
    origin, mine = make_repos(tmp_path)
    (mine / "card.py").write_text("mine\n")
    push_another_change(tmp_path, origin, "card.py", "card\n")

    assert (
        replay_report(replay(mine, tmp_path / "scratch")) == "conflict: card.py"
    )


def test_replay_leaves_the_main_folder_as_it_was(tmp_path):
    origin, mine = make_repos(tmp_path)
    commit_file(mine, "server.py", "one\nmine\nthree\n")
    (mine / "report.py").write_text("edited\n")
    (mine / "notes.txt").write_text("notes\n")
    push_another_change(tmp_path, origin, "server.py", "one\ncard\nthree\n")
    before = [git(mine, *args) for args in STATE_COMMANDS]

    replay(mine, tmp_path / "scratch")

    assert [git(mine, *args) for args in STATE_COMMANDS] == before
    assert not (tmp_path / "scratch").exists()


STATE_COMMANDS = [
    ("status", "--porcelain"),
    ("rev-parse", "HEAD"),
    ("stash", "list"),
    ("diff", "HEAD"),
]
