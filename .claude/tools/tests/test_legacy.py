"""Tests for legacy — the one-time config upgrades quarantined from linear.py.

These exercise the `.linear_project` → `.stride.json` migration and config
default backfills as pure functions, patching the config paths so no real repo
file is touched.

Run with:
    python -m pytest .claude/tools/tests/test_legacy.py
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import legacy  # noqa: E402
import linear  # noqa: E402
from legacy import (  # noqa: E402
    backfill_focus,
    backfill_unattended,
    migrate_from_legacy,
)
from linear import DEFAULT_FOCUS, DEFAULT_UNATTENDED, LinearError  # noqa: E402


def test_migrate_from_legacy_round_trip(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    legacy_file = tmp_path / ".linear_project"
    legacy_file.write_text(
        "project = Round Trip\napi_key_env = LINEAR_RT_API_KEY\n"
    )
    expected = {"project": "Round Trip", "api_key_env": "LINEAR_RT_API_KEY"}
    with (
        patch("linear.STRIDE_CONFIG_PATH", stride),
        patch("legacy.LEGACY_CONFIG_PATH", legacy_file),
    ):
        assert migrate_from_legacy() == expected
    assert json.loads(stride.read_text()) == expected
    assert not legacy_file.exists()


def test_migrate_from_legacy_keeps_original_when_malformed(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    legacy_file = tmp_path / ".linear_project"
    legacy_file.write_text("# only a comment, no project\n")
    with (
        patch("linear.STRIDE_CONFIG_PATH", stride),
        patch("legacy.LEGACY_CONFIG_PATH", legacy_file),
    ):
        with pytest.raises(LinearError, match="malformed"):
            migrate_from_legacy()
    assert legacy_file.read_text() == "# only a comment, no project\n"
    assert not stride.exists()


def test_legacy_config_path_anchored_to_repo_root():
    repo_root = Path(linear.__file__).resolve().parent.parent.parent
    assert legacy.LEGACY_CONFIG_PATH == repo_root / ".linear_project"


def test_backfill_focus_adds_default_when_missing(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    stride.write_text(
        '{\n  "project": "Foo",\n  "api_key_env": "LINEAR_FOO_API_KEY"\n}\n'
    )
    expected = {
        "project": "Foo",
        "api_key_env": "LINEAR_FOO_API_KEY",
        "focus": DEFAULT_FOCUS,
    }
    with patch("linear.STRIDE_CONFIG_PATH", stride):
        assert backfill_focus() == expected
    assert json.loads(stride.read_text()) == expected


def test_backfill_focus_appends_focus_last(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    stride.write_text(
        '{\n  "project": "Foo",\n  "api_key_env": "LINEAR_FOO_API_KEY"\n}\n'
    )
    with patch("linear.STRIDE_CONFIG_PATH", stride):
        backfill_focus()
    assert list(json.loads(stride.read_text())) == [
        "project",
        "api_key_env",
        "focus",
    ]


def test_backfill_focus_leaves_explicit_choice_untouched(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    original = '{\n  "project": "Foo",\n  "focus": "technical"\n}\n'
    stride.write_text(original)
    with patch("linear.STRIDE_CONFIG_PATH", stride):
        assert backfill_focus() == {"project": "Foo", "focus": "technical"}
    assert stride.read_text() == original


def test_backfill_focus_no_op_when_file_missing(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    with patch("linear.STRIDE_CONFIG_PATH", stride):
        assert backfill_focus() == {}
    assert not stride.exists()


def test_backfill_unattended_adds_default_when_missing(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    stride.write_text('{\n  "project": "Foo"\n}\n')
    with patch("linear.STRIDE_CONFIG_PATH", stride):
        config = backfill_unattended()
    assert config == {"project": "Foo", "unattended": DEFAULT_UNATTENDED}


def test_backfill_unattended_leaves_explicit_choice_untouched(tmp_path: Path):
    stride = tmp_path / ".stride.json"
    original = '{\n  "project": "Foo",\n  "unattended": true\n}\n'
    stride.write_text(original)
    with patch("linear.STRIDE_CONFIG_PATH", stride):
        assert backfill_unattended()["unattended"] is True
    assert stride.read_text() == original
