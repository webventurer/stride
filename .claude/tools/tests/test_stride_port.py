"""Tests for the free-port finder (.claude/tools/stride_port.py).

Each test claims a real OS-assigned port via `free_port()` so the cases are
independent of whatever else is listening on the machine.
"""

import socket
import sys
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import stride_port  # noqa: E402
from stride_port import launch, main, next_free_port, template_for  # noqa: E402


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", 0))
        return sock.getsockname()[1]


def occupy(port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", port))
    return sock


def test_next_free_port_returns_base_when_free():
    port = free_port()

    assert next_free_port(port) == port


def test_next_free_port_skips_occupied_base():
    port = free_port()
    held = occupy(port)

    try:
        assert next_free_port(port) > port
    finally:
        held.close()


def test_next_free_port_raises_when_range_exhausted():
    port = free_port()
    held = occupy(port)

    try:
        with pytest.raises(click.ClickException):
            next_free_port(port, scan=1)
    finally:
        held.close()


def test_main_prints_a_free_port():
    result = CliRunner().invoke(main, [])

    assert result.exit_code == 0
    assert result.output.strip().isdigit()


def test_main_honours_base_port():
    port = free_port()

    result = CliRunner().invoke(main, [str(port)])

    assert result.exit_code == 0
    assert int(result.output) >= port


def test_template_for_returns_the_framework_command():
    assert template_for("3") == "python manage.py runserver 0.0.0.0:{port}"


def test_template_for_rejects_an_unknown_choice():
    with pytest.raises(click.ClickException):
        template_for("9")


def test_launch_runs_the_formatted_command(monkeypatch):
    calls = []
    monkeypatch.setattr(stride_port.subprocess, "run", calls.append)

    launch("flask run --port {port}", 5001)

    assert calls == [["flask", "run", "--port", "5001"]]


def test_main_run_launches_the_chosen_framework(monkeypatch):
    calls = []
    monkeypatch.setattr(stride_port.subprocess, "run", calls.append)
    port = free_port()

    result = CliRunner().invoke(main, [str(port), "--run"], input="1\n")

    assert result.exit_code == 0
    assert calls[0][:2] == ["flask", "run"]
