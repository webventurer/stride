#!/usr/bin/env python3
# /// script
# dependencies = ["click"]
# ///
"""Print the next free TCP port from a base — for parallel worktree dev servers.

When several worktrees serve the same app in one VS Code window, they all
reach for the same default port and collide. Splice a free one in:

    flask run --port "$(uv run .claude/tools/stride_port.py)"
    uv run .claude/tools/stride_port.py 8000
"""

import socket
from contextlib import suppress

import click

SCAN_RANGE = 100


@click.command()
@click.argument("base", type=int, default=5000)
def main(base: int):
    click.echo(next_free_port(base))


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
