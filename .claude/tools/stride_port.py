#!/usr/bin/env python3
# /// script
# dependencies = ["click"]
# ///
"""Print the next free TCP port from a base — or launch a dev server on one.

When several worktrees serve the same app in one VS Code window, they all
reach for the same default port and collide. Splice a free one in:

    flask run --port "$(uv run .claude/tools/stride_port.py)"
    uv run .claude/tools/stride_port.py 8000

Or pick a framework and let it launch on the next free port:

    uv run .claude/tools/stride_port.py --run
"""

import shlex
import socket
import subprocess
from contextlib import suppress

import click

SCAN_RANGE = 100

FRAMEWORKS = {
    "1": ("Flask", "flask run --port {port}"),
    "2": ("Vite / Node", "npm run dev -- --port {port}"),
    "3": ("Django", "python manage.py runserver 0.0.0.0:{port}"),
    "4": ("Rails", "rails server --port {port}"),
    "5": ("Python http.server", "python -m http.server {port}"),
}


@click.command()
@click.argument("base", type=int, default=5000)
@click.option(
    "--run",
    "launch_server",
    is_flag=True,
    help="Pick a framework and launch it on a free port.",
)
def main(base: int, launch_server: bool):
    if launch_server:
        run_framework(base)
    else:
        click.echo(next_free_port(base))


def run_framework(base: int):
    template = choose_template()
    launch(template, next_free_port(base))


def choose_template() -> str:
    print_menu()
    return template_for(click.prompt(">"))


def print_menu():
    options = [f"  {key}. {name}" for key, (name, _) in FRAMEWORKS.items()]
    options.append("  6. Custom command (use {port})")
    click.echo("Which framework are you running?\n" + "\n".join(options))


def template_for(choice: str) -> str:
    if choice == "6":
        return click.prompt("Command (use {port})")
    if choice not in FRAMEWORKS:
        raise click.ClickException(f"unknown choice: {choice}")
    return FRAMEWORKS[choice][1]


def launch(template: str, port: int):
    command = template.format(port=port)
    click.echo(f"Found free port: {port}")
    click.echo(f"Running: {command}")
    subprocess.run(shlex.split(command))


def next_free_port(base: int, scan: int = SCAN_RANGE) -> int:
    free = (port for port in range(base, base + scan) if is_free(port))
    found = next(free, None)
    if found is None:
        raise click.ClickException(f"no free port in {base}..{base + scan - 1}")
    return found


def is_free(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with sock, suppress(OSError):
        sock.bind(("", port))
        return True
    return False


if __name__ == "__main__":
    main()
