"""Exercise the worktree settings script and the real config reader."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import linear  # noqa: E402

SHARE_SETTINGS_SCRIPT = Path(__file__).resolve().parents[1] / (
    "share_stride_settings.sh"
)


def test_shared_worktree_settings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    repo = Path(__file__).resolve().parents[3]
    main = tmp_path / "main checkout"
    worktree = tmp_path / "first worktree"
    sibling = tmp_path / "second worktree"

    def git(cwd: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    git(repo, "clone", "--shared", str(repo), str(main))
    git(main, "worktree", "add", "--detach", str(worktree), "HEAD")
    git(worktree, "worktree", "add", "--detach", str(sibling), "HEAD")
    assert (
        git(sibling, "worktree", "list", "--porcelain").splitlines()[0]
        == f"worktree {main}"
    )
    source = main / ".stride.json"
    target = worktree / ".stride.json"
    settings = {
        "project": "Test",
        "api_key_env": "LINEAR_TEST_KEY",
        "focus": "outcome",
        "unattended": True,
    }

    def run_share_settings_script(
        destination: Path = worktree,
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(SHARE_SETTINGS_SCRIPT), str(main), str(destination)],
            capture_output=True,
            text=True,
        )

    def link(destination: Path = worktree) -> int:
        return run_share_settings_script(destination).returncode

    for content in [None, "invalid json", "[]"]:
        if content is not None:
            source.write_text(content)
        assert link() != 0
        assert not target.is_symlink()
    source.write_text(json.dumps(settings))
    assert link() == 0
    assert target.is_symlink() and target.readlink() == source
    inode = target.lstat().st_ino
    assert link() == 0 and target.lstat().st_ino == inode
    monkeypatch.setattr(linear, "STRIDE_CONFIG_PATH", target)
    assert linear.project_config() == settings
    settings["unattended"] = False
    source.write_text(json.dumps(settings))
    assert linear.project_config() == settings
    linear.write_config({**settings, "focus": "technical"})
    assert json.loads(source.read_text())["focus"] == "technical"
    assert link(sibling) == 0
    assert git(worktree, "status", "--porcelain") == ""

    target.unlink()
    target.write_text("keep my settings")
    taken = run_share_settings_script()
    assert taken.returncode != 0 and target.read_text() == "keep my settings"
    assert f"Existing .stride.json in {worktree}" in taken.stderr
    target.unlink()
    target.mkdir()
    assert link() != 0 and list(target.iterdir()) == []
    target.rmdir()
    for other in [sibling / ".stride.json", tmp_path / "missing settings"]:
        target.symlink_to(other)
        # A different link resolving to the same shared file is already correct.
        assert link() == (0 if other.exists() else 1)
        assert target.readlink() == other
        target.unlink()
    independent = tmp_path / "independent settings"
    independent.write_text("{}")
    target.symlink_to(independent)
    assert link() != 0 and target.readlink() == independent
    target.unlink()

    git(main, "add", "-f", ".stride.json")
    tracked = run_share_settings_script()
    assert tracked.returncode != 0 and not target.is_symlink()
    assert f"Tracked .stride.json in {main}" in tracked.stderr
    git(main, "update-index", "--force-remove", ".stride.json")
    assert link() == 0
    git(worktree, "add", "-f", ".stride.json")
    assert link() != 0
    git(worktree, "update-index", "--force-remove", ".stride.json")
    git(main, "worktree", "remove", "--force", str(worktree))
    git(main, "worktree", "remove", "--force", str(sibling))
    assert source.is_file()
