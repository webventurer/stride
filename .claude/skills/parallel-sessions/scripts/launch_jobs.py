"""
Start each job's `claude -p` session only once it holds a slot.

The launcher claims a slot for each job in turn, waiting in the shell while
none is free, then starts that job's session and frees the slot when the
session exits, whatever its exit code. A session therefore never waits for a
slot, and no more sessions run than there are slots.

A session that exits because the connection was lost is resumed by its session
ID, after a wait that holds no slot and once the launcher holds a slot for it.
Any other non-zero exit, or running out of tries, marks the job failed.

While a session runs, a shell command in its current log that has run past the
stall limit is stopped, with every process it started, and its job is marked
stalled, so the session sees the command fail and carries on.

It owns starting and resuming the sessions of a batch; the slot store belongs
to slots.py and the batch itself to the parallel-sessions skill.
"""

import contextlib
import json
import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass, field
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
DEFAULT_RESUME_TRIES = 5
FINAL_STATES = ("merged", "canceled", "failed")
DEFAULT_RESUME_WAIT_SECONDS = 300
WAIT_GROWTH = 3
CONNECTION_MESSAGES = ("Can't reach the API server", "Unable to connect to API")
DEFAULT_STALL_LIMIT_SECONDS = 300
SHELL_TOOL = "Bash"
RESUME_MESSAGE = (
    "Your session was cut off by a lost connection. Before you carry on, "
    "check what you have already committed and what is still uncommitted in "
    "this worktree, then carry on with your brief from there."
)


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
class Stall:
    """A shell command that has run past the stall limit."""

    tool_use_id: str
    command: str
    elapsed_seconds: int


@dataclass
class Launcher:
    """Starts sessions as slots free, and resumes those a lost connection cut off."""

    pool: SlotPool
    claude: str
    poll_seconds: float
    resume_tries: int = DEFAULT_RESUME_TRIES
    resume_wait_seconds: float = DEFAULT_RESUME_WAIT_SECONDS
    progress: Path | None = None
    stall_limit_seconds: float = DEFAULT_STALL_LIMIT_SECONDS
    failed: list[str] = field(default_factory=list)
    progress_lock: threading.Lock = field(default_factory=threading.Lock)

    def run(self, jobs: list[Job]) -> int:
        watchers = [self.launch(job) for job in jobs]
        for watcher in watchers:
            if watcher:
                watcher.join()
        return watchers.count(None) + len(self.failed)

    def launch(self, job: Job) -> threading.Thread | None:
        self.wait_for_slot(job.holder)
        session = self.start(job, attempt=0, session_id=None)
        if session is None:
            return None
        click.echo(f"{job.holder} started")
        watcher = threading.Thread(target=self.supervise, args=(job, session))
        watcher.start()
        return watcher

    def start(
        self, job: Job, attempt: int, session_id: str | None
    ) -> subprocess.Popen | None:
        try:
            return start_session(self.claude, job, attempt, session_id)
        except OSError as error:
            self.pool.release(job.holder)
            click.echo(f"{job.holder} could not start: {error}")
            return None

    def wait_for_slot(self, holder: str):
        while self.pool.claim(holder) is None:
            time.sleep(self.poll_seconds)

    def supervise(self, job: Job, session: subprocess.Popen):
        session_id = None
        for attempt in range(self.resume_tries + 1):
            log, errors = attempt_paths(job, attempt)
            exit_code = self.watch(job, session, log)
            self.pool.release(job.holder)
            click.echo(f"{job.holder} exited with code {exit_code}, slot freed")
            session_id = find_session_id(log) or session_id
            if exit_code == 0:
                return
            if not cut_by_connection(log, errors):
                return self.fail(job, f"exited with code {exit_code}")
            if attempt == self.resume_tries:
                return self.fail(job, "ran out of resume tries")
            time.sleep(self.resume_wait_seconds * WAIT_GROWTH**attempt)
            self.wait_for_slot(job.holder)
            session = self.start(job, attempt + 1, session_id)
            if session is None:
                return self.fail(job, "could not be resumed")
            click.echo(f"{job.holder} resumed, try {attempt + 1}")

    def watch(self, job: Job, session: subprocess.Popen, log: Path) -> int:
        stopped = set()
        while True:
            try:
                return session.wait(timeout=self.poll_seconds)
            except subprocess.TimeoutExpired:
                for stall in stalled_commands(log, self.stall_limit_seconds):
                    if stall.tool_use_id not in stopped:
                        stopped.add(stall.tool_use_id)
                        self.stop(job, session, stall)

    def stop(self, job: Job, session: subprocess.Popen, stall: Stall):
        stop_command(session.pid, stall)
        click.echo(
            f"{job.holder} stalled: stopped after {stall.elapsed_seconds} "
            f"seconds: {stall.command.splitlines()[0]}"
        )
        self.mark(job, "stalled")

    def fail(self, job: Job, reason: str):
        click.echo(f"{job.holder} failed: {reason}")
        self.failed.append(job.holder)
        self.mark(job, "failed")

    def mark(self, job: Job, state: str):
        if self.progress:
            with self.progress_lock:
                mark_row(self.progress, job.holder, state)


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
@click.option(
    "--resume-tries",
    type=int,
    default=DEFAULT_RESUME_TRIES,
    show_default=True,
    help="Times a session cut off by a lost connection is resumed",
)
@click.option(
    "--resume-wait",
    "resume_wait_seconds",
    type=float,
    default=DEFAULT_RESUME_WAIT_SECONDS,
    show_default=True,
    help="Seconds before the first resume; each later one waits three times as long",
)
@click.option(
    "--progress",
    type=click.Path(path_type=Path),
    help="progress.md, whose row for a failed or stalled job is set to that state",
)
@click.option(
    "--stall-limit",
    "stall_limit_seconds",
    type=float,
    default=DEFAULT_STALL_LIMIT_SECONDS,
    show_default=True,
    help="Seconds a shell command may run before it is stopped as stalled",
)
@click.argument("jobs_file", type=click.Path(exists=True, path_type=Path))
def main(
    store_folder: Path | None,
    limit: int,
    expiry_seconds: int,
    poll_seconds: float,
    claude: str,
    resume_tries: int,
    resume_wait_seconds: float,
    progress: Path | None,
    stall_limit_seconds: float,
    jobs_file: Path,
):
    folder = store_folder or shared_store_path(Path.cwd())
    pool = SlotPool(Cache(str(folder)), limit, expiry_seconds)
    jobs = [Job(**entry) for entry in json.loads(jobs_file.read_text())]
    failures = Launcher(
        pool,
        claude,
        poll_seconds,
        resume_tries,
        resume_wait_seconds,
        progress,
        stall_limit_seconds,
    ).run(jobs)
    exit_with(
        EXIT_FAILURE if failures else EXIT_SUCCESS,
        f"{len(jobs) - failures} of {len(jobs)} jobs finished",
    )


def start_session(
    claude: str, job: Job, attempt: int, session_id: str | None
) -> subprocess.Popen:
    log, errors = attempt_paths(job, attempt)
    if session_id:
        prompt = [RESUME_MESSAGE, "--resume", session_id]
    else:
        prompt = [Path(job.brief).read_text()]
    command = [
        claude,
        "-p",
        *prompt,
        "--model",
        job.model,
        "--effort",
        job.effort,
        "--dangerously-skip-permissions",
        "--output-format",
        "stream-json",
        "--verbose",
    ]
    with open(log, "w") as log_file, open(errors, "w") as errors_file:
        return subprocess.Popen(
            command,
            cwd=job.checkout,
            env=session_environment(),
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=errors_file,
        )


def attempt_paths(job: Job, attempt: int) -> tuple[Path, Path]:
    if not attempt:
        return Path(job.log), Path(job.errors)
    return resume_path(job.log, attempt), resume_path(job.errors, attempt)


def resume_path(path: str, attempt: int) -> Path:
    original = Path(path)
    return original.with_name(
        f"{original.stem}.resume-{attempt}{original.suffix}"
    )


def find_session_id(log: Path) -> str | None:
    for line in log.read_text(errors="replace").splitlines():
        try:
            session_id = json.loads(line).get("session_id")
        except (json.JSONDecodeError, AttributeError):
            continue
        if session_id:
            return session_id
    return None


def cut_by_connection(log: Path, errors: Path) -> bool:
    lines = log.read_text(errors="replace").splitlines()
    evidence = (lines[-1] if lines else "") + errors.read_text(errors="replace")
    return any(message in evidence for message in CONNECTION_MESSAGES)


def stalled_commands(log: Path, limit_seconds: float) -> list[Stall]:
    running, elapsed = {}, {}
    for entry in log_entries(log):
        for item in message_items(entry):
            if (
                item.get("type") == "tool_use"
                and item.get("name") == SHELL_TOOL
            ):
                running[item.get("id")] = item.get("input", {}).get(
                    "command", ""
                )
            if item.get("type") == "tool_result":
                running.pop(item.get("tool_use_id"), None)
        if entry.get("type") == "tool_progress":
            elapsed[entry.get("parent_tool_use_id")] = entry.get(
                "elapsed_time_seconds", 0
            )
    return [
        Stall(tool_use_id, command, elapsed[tool_use_id])
        for tool_use_id, command in running.items()
        if elapsed.get(tool_use_id, 0) >= limit_seconds
    ]


def log_entries(log: Path) -> list[dict]:
    entries = []
    for line in log.read_text(errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def message_items(entry: dict) -> list[dict]:
    message = entry.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    return [item for item in content if isinstance(item, dict)]


def stop_command(session_pid: int, stall: Stall):
    children = child_processes()
    marker = shell_marker(stall.command)
    shells = {}
    for pid in descendants(session_pid, children):
        age, command = process_details(pid)
        if marker in command:
            shells[pid] = abs(age - stall.elapsed_seconds)
    if shells:
        shell = min(shells, key=shells.get)
        for target in [shell, *descendants(shell, children)]:
            with contextlib.suppress(ProcessLookupError):
                os.kill(target, signal.SIGKILL)


def shell_marker(command: str) -> str:
    lines = command.splitlines() or [""]
    quoted = lines[0].replace("'", "'\"'\"'")
    return f"eval '{quoted}" + ("'" if len(lines) == 1 else "")


def child_processes() -> dict[int, list[int]]:
    listing = subprocess.run(
        ["ps", "-A", "-o", "pid=,ppid="], capture_output=True, text=True
    ).stdout
    children = {}
    for line in listing.splitlines():
        pid, parent = (int(number) for number in line.split())
        children.setdefault(parent, []).append(pid)
    return children


def descendants(pid: int, children: dict[int, list[int]]) -> list[int]:
    found = []
    for child in children.get(pid, []):
        found += [child, *descendants(child, children)]
    return found


def process_details(pid: int) -> tuple[int, str]:
    listing = subprocess.run(
        ["ps", "-ww", "-o", "etime=,command=", "-p", str(pid)],
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not listing:
        return 0, ""
    elapsed, _, command = listing.partition(" ")
    return seconds_from_elapsed(elapsed), command


def seconds_from_elapsed(elapsed: str) -> int:
    days, _, clock = elapsed.rpartition("-")
    seconds = 0
    for part in clock.split(":"):
        seconds = seconds * 60 + int(part)
    return seconds + int(days or 0) * 24 * 60 * 60


def mark_row(progress: Path, holder: str, state: str):
    rows = [
        state_row(line, holder, state)
        for line in progress.read_text().splitlines()
    ]
    progress.write_text("\n".join(rows) + "\n")


def state_row(line: str, holder: str, state: str) -> str:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if not line.lstrip().startswith("|") or holder not in cells:
        return line
    if cells[-1] in FINAL_STATES:
        return line
    return "| " + " | ".join([*cells[:-1], state]) + " |"


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
