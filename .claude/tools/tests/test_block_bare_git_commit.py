"""
Tests for the bare-commit guard (.claude/hooks/pretooluse/block_bare_git_commit.sh).

Each row of the table is piped to the real hook as JSON, the way Claude Code
and Codex send it, with the hook process started in the project root (as Codex
does) and the shell's folder in the payload's cwd.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HOOKS_DIR = (
    Path(__file__).resolve().parent.parent.parent / "hooks" / "pretooluse"
)
GIT = ["git", "-c", "user.name=test", "-c", "user.email=test@example.com"]

ALLOWED = 0
REFUSED = 2

ROWS = [
    ("git -C {scratch} commit -m init", "project", ALLOWED),
    ("cd {scratch} && git commit -m init", "project", ALLOWED),
    ("git commit -m init", "scratch", ALLOWED),
    ("git status", "project", ALLOWED),
    ("git commit -m x", "project", REFUSED),
    ("git commit -m x", "subfolder", REFUSED),
    ("git commit -m x", "worktree", REFUSED),
    ("git commit -m x", "linked", REFUSED),
    ("git -C {project} commit -m x", "scratch", REFUSED),
    ("git -C {worktree} commit -m x", "scratch", REFUSED),
    ("git -c k=v commit -m x", "project", REFUSED),
    ("git --no-pager commit -m x", "project", REFUSED),
    ("git -C {scratch} commit -m a && git commit -m b", "project", REFUSED),
    ("cd {scratch} && cd {project} && git commit -m x", "scratch", REFUSED),
    ("(cd {scratch}); git commit -m x", "project", REFUSED),
    ("git commit -m x", "plain", REFUSED),
    ("git commit -m x", "missing", REFUSED),
    ("git -C {missing} commit -m x", "project", REFUSED),
    (
        "mkdir {missing} && cd {missing} && git init -q && git commit -m x",
        "scratch",
        REFUSED,
    ),
    ("GIT_DIR={project}/.git git commit -m x", "scratch", REFUSED),
    ("git --git-dir={project}/.git commit -m x", "scratch", REFUSED),
    ('grep -rn "git commit" .claude/', "project", ALLOWED),
    ("echo 'git commit'", "project", ALLOWED),
    ('echo "git commit"', "project", ALLOWED),
    ("echo hi # git commit", "project", ALLOWED),
    ("cat > notes.md <<'EOF'\nrun git commit later\nEOF", "project", ALLOWED),
    ("cat <<EOF\nrun git commit later\nEOF\ngit status", "project", ALLOWED),
    ('echo "git commit" && git -C {scratch} commit -m a', "project", ALLOWED),
    ('echo "git commit" && git commit -m x', "project", REFUSED),
    ("echo a\ngit commit -m x", "project", REFUSED),
    ("git \\\n commit -m x", "project", REFUSED),
    ("FOO=1 git commit -m x", "project", REFUSED),
    ("if true; then git commit -m x; fi", "project", REFUSED),
    ("echo hi | git commit -F -", "project", REFUSED),
    ('echo "git commit', "project", REFUSED),
    ('echo "$(git commit -m x)"', "project", REFUSED),
    ("echo `git commit -m x`", "project", REFUSED),
    ("cat <<EOF\n$(git commit -m x)\nEOF", "project", REFUSED),
    ("cat <<EOF\nrun git commit later", "project", REFUSED),
    ('echo "git commit', "scratch", ALLOWED),
    ("git commit -m x", "nested", ALLOWED),
    ("git --git-dir=.git status", "project", ALLOWED),
    ("git --no-pager log", "project", ALLOWED),
    ("git --config-env user.name=NAME commit -m x", "project", REFUSED),
    ("git --attr-source HEAD commit -m x", "project", REFUSED),
    ("cd {project} || cd {scratch}; git commit -m x", "scratch", REFUSED),
    ("cd {scratch} | git commit -m x", "project", REFUSED),
    ("cd {scratch} & git commit -m x", "project", REFUSED),
    ("false && cd {scratch}; git commit -m x", "project", REFUSED),
    (">/dev/null git commit -m x", "project", REFUSED),
    ("2>&1 git commit -m x", "project", REFUSED),
    ("env git commit -m x", "project", REFUSED),
    ("git commit -m x 2>&1", "scratch", ALLOWED),
]


@pytest.fixture(scope="module")
def folders(tmp_path_factory):
    root = tmp_path_factory.mktemp("guard").resolve()
    project = root / "project"
    scratch = root / "scratch"
    for repository in (project, scratch):
        repository.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    shutil.copytree(HOOKS_DIR, project / ".claude/hooks/pretooluse")
    (project / "docs").mkdir()
    subprocess.run(
        [*GIT, "commit", "--allow-empty", "-qm", "init"],
        cwd=project,
        check=True,
    )
    subprocess.run(
        ["git", "worktree", "add", "-q", root / "worktree"],
        cwd=project,
        check=True,
    )
    (project / "nested").mkdir()
    subprocess.run(["git", "init", "-q"], cwd=project / "nested", check=True)
    (root / "plain").mkdir()
    (root / "linked").symlink_to(project)
    return {
        "project": project,
        "subfolder": project / "docs",
        "scratch": scratch,
        "worktree": root / "worktree",
        "linked": root / "linked",
        "plain": root / "plain",
        "nested": project / "nested",
        "missing": root / "missing",
    }


@pytest.mark.parametrize("command, shell_folder, expected", ROWS)
def test_guard_decision(folders, command, shell_folder, expected):
    payload = {
        "tool_input": {"command": command.format(**folders)},
        "cwd": str(folders[shell_folder]),
    }

    result = subprocess.run(
        [
            "bash",
            folders["project"]
            / ".claude/hooks/pretooluse/block_bare_git_commit.sh",
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=folders["project"],
    )

    assert result.returncode == expected, result.stderr


@pytest.mark.parametrize(
    "command, expected",
    [
        ("git -C {scratch} commit -m x", REFUSED),
        ('echo "git commit"', REFUSED),
        ("git status", ALLOWED),
    ],
)
def test_without_python_the_words_are_refused(
    folders, tmp_path, command, expected
):
    tools = tmp_path / "bin"
    tools.mkdir()
    for name in ("dirname", "grep", "cat"):
        (tools / name).symlink_to(shutil.which(name))
    payload = {
        "tool_input": {"command": command.format(**folders)},
        "cwd": str(folders["project"]),
    }

    result = subprocess.run(
        [
            "/bin/bash",
            folders["project"]
            / ".claude/hooks/pretooluse/block_bare_git_commit.sh",
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PATH": str(tools)},
    )

    assert result.returncode == expected, result.stderr
