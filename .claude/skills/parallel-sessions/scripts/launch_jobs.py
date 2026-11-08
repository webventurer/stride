"""
Start each job's `claude -p` session only once it holds a slot.

The launcher claims a slot for each job in turn, waiting in the shell while
none is free, then starts that job's session and frees the slot when the
session exits, whatever its exit code. A session therefore never waits for a
slot, and no more sessions run than there are slots.

It owns starting the sessions of a batch; the slot store belongs to slots.py
and the batch itself to the parallel-sessions skill.
"""

import json
import os
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import click
from diskcache import Cache
from slots import (
    DEFAULT_EXPIRY_SECONDS,
    DEFAULT_LIMIT,
    EXIT_FAILURE,
    EXIT_SUCCESS,
    SlotPool,
    exit_with,
    shared_store_path,
)

DEFAULT_POLL_SECONDS = 15


@dataclass
class Job:
    """One job: its holder name, where it runs and how its session starts."""

    holder: str
    checkout: str
    brief: str
    model: str
    effort: str
    log: str
    errors: str


@dataclass
class Launcher:
    """Starts sessions as slots free, and frees each slot as its session ends."""

    pool: SlotPool
    claude: str
    poll_seconds: float

    def run(self, jobs: list[Job]) -> int:
        watchers = [self.launch(job) for job in jobs]
        for watcher in watchers:
            if watcher:
                watcher.join()
        return watchers.count(None)

    def launch(self, job: Job) -> threading.Thread | None:
        self.wait_for_slot(job.holder)
        try:
            session = start_session(self.claude, job)
        except OSError as error:
            self.pool.release(job.holder)
            click.echo(f"{job.holder} could not start: {error}")
            return None
        click.echo(f"{job.holder} started")
        watcher = threading.Thread(
            target=self.free_slot_when_done, args=(job.holder, session)
        )
        watcher.start()
        return watcher

    def wait_for_slot(self, holder: str):
        while self.pool.claim(holder) is None:
            time.sleep(self.poll_seconds)

    def free_slot_when_done(self, holder: str, session: subprocess.Popen):
        exit_code = session.wait()
        self.pool.release(holder)
        click.echo(f"{holder} exited with code {exit_code}, slot freed")


@click.command()
@click.option(
    "--store",
    "store_folder",
    type=click.Path(path_type=Path),
    help="Slot store folder; defaults to work/slots under the main checkout",
)
@click.option("--limit", default=DEFAULT_LIMIT, show_default=True)
@click.option(
    "--expiry",
    "expiry_seconds",
    default=DEFAULT_EXPIRY_SECONDS,
    show_default=True,
    help="Seconds before an unrenewed claim lapses",
)
@click.option(
    "--poll",
    "poll_seconds",
    type=float,
    default=DEFAULT_POLL_SECONDS,
    show_default=True,
    help="Seconds between checks for a free slot",
)
@click.option(
    "--claude", default="claude", show_default=True, help="The claude program"
)
@click.argument("jobs_file", type=click.Path(exists=True, path_type=Path))
def main(
    store_folder: Path | None,
    limit: int,
    expiry_seconds: int,
    poll_seconds: float,
    claude: str,
    jobs_file: Path,
):
    folder = store_folder or shared_store_path(Path.cwd())
    pool = SlotPool(Cache(str(folder)), limit, expiry_seconds)
    jobs = [Job(**entry) for entry in json.loads(jobs_file.read_text())]
    failures = Launcher(pool, claude, poll_seconds).run(jobs)
    exit_with(
        EXIT_FAILURE if failures else EXIT_SUCCESS,
        f"{len(jobs) - failures} of {len(jobs)} sessions started",
    )


def start_session(claude: str, job: Job) -> subprocess.Popen:
    command = [
        claude,
        "-p",
        Path(job.brief).read_text(),
        "--model",
        job.model,
        "--effort",
        job.effort,
        "--dangerously-skip-permissions",
        "--output-format",
        "stream-json",
        "--verbose",
    ]
    with open(job.log, "w") as log, open(job.errors, "w") as errors:
        return subprocess.Popen(
            command,
            cwd=job.checkout,
            env=session_environment(),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=errors,
        )


def session_environment() -> dict[str, str]:
    environment = {
        name: value
        for name, value in os.environ.items()
        if name != "ANTHROPIC_API_KEY"
    }
    environment["CLAUDE_CODE_DISABLE_ADVISOR_TOOL"] = "1"
    return environment


if __name__ == "__main__":
    main()
