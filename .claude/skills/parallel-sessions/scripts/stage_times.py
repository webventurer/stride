"""
Record how long each stage of a card took, and report where the time goes.

After a card merges, it reads the Claude Code session logs saved for the
card's working directory, and the log of each reviewer sub-agent beside them,
and records one row per stage run in a diskcache store in the main checkout.
The report reads that store back: for each stage, its median and slowest time
and how often it ran again, over the last merged cards.

It owns reading the logs and the record; running the stages and merging the
card belong to the stride commands, which a missing log never stops.
"""

# /// script
# dependencies = ["click", "diskcache"]
# ///

import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from pathlib import Path

import click
from diskcache import Cache
from measure_run import SessionLog
from slots import main_checkout_path, read_git_output

STORE_FOLDER = Path("work", "stage-times")
EXCLUDE_LINE = "/work"
CLAUDE_LOGS = Path.home() / ".claude" / "projects"
DEFAULT_CARD_COUNT = 10
SLOW_SECONDS = 90
BUILD = "Build"
MERGE = "Merge"
WAIT = "Wait on the user"
REVIEWER_BRIEFS = (
    ("card-start-review.md", "Start check"),
    ("simplify-review.md", "Simplification review"),
    ("card-check-review.md", "Card check"),
    ("skills/commit/REVIEW.md", "Commit review"),
)
REVIEWER_STAGES = {stage for _, stage in REVIEWER_BRIEFS}
BRIEF_SEARCH_LENGTH = 300
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
ASK_TOOL = "AskUserQuestion"
START_COMMAND = "linear:start"
MERGE_COMMAND = re.compile(
    r"\s*(?:cd\s+(?:\"[^\"]*\"|'[^']*'|[^\s&;]+)\s*&&\s*)?gh pr merge\b"
)
AUTOMATED_PREFIXES = (
    "[SYSTEM NOTIFICATION",
    "<task-notification",
    "<system-reminder",
)
CONVERSATION = {"user", "assistant"}
LENS_PATTERN = re.compile(r"Your lens is ([^.]+)\.")
CARD_PATTERN = re.compile(r"[A-Za-z]+-\d+")


@dataclass
class StageRow:
    """One run of one stage of one card."""

    card: str
    stage: str
    lens: str
    model: str
    effort: str
    started_at: str
    seconds: float
    longest_silence: float
    working_seconds: float
    run: int

    @property
    def repeat(self) -> bool:
        return self.run > 1

    @property
    def key(self) -> tuple:
        return (self.card, self.stage, self.lens, self.run, self.started_at)

    def as_dict(self) -> dict:
        return asdict(self)


def stage_row(
    card: str,
    stage: str,
    times: list[datetime],
    lens: str = "",
    model: str = "",
    effort: str = "",
) -> StageRow:
    ordered = sorted(times)
    seconds = (ordered[-1] - ordered[0]).total_seconds()
    gaps = [(b - a).total_seconds() for a, b in zip(ordered, ordered[1:])]
    silence = max(gaps, default=0.0)
    return StageRow(
        card,
        stage,
        lens,
        model,
        effort,
        ordered[0].isoformat(),
        seconds,
        silence,
        seconds - silence,
        1,
    )


def record_card(card: str, folders: list[Path], store: Cache) -> list[StageRow]:
    paths = [path for folder in folders for path in session_paths(folder)]
    rows = [row for path in paths for row in session_rows(card, path)]
    numbered = number_runs(rows)
    if numbered:
        replace_card_rows(store, card, numbered)
    return numbered


def session_paths(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.jsonl")) if folder.is_dir() else []


def session_rows(card: str, path: Path) -> list[StageRow]:
    try:
        events = timed(SessionLog.from_path(path).events)
    except OSError:
        return []
    window = card_window(events, card)
    if not window:
        return []
    reviewers = reviewer_rows(card, path, window)
    return [
        *reviewers,
        *build_rows(card, window, reviewers),
        *merge_rows(card, window),
        *wait_rows(card, window),
    ]


def timed(events: list[dict]) -> list[dict]:
    return [event for event in events if event.get("timestamp")]


def moment(event: dict) -> datetime:
    return datetime.fromisoformat(event["timestamp"])


def card_window(events: list[dict], card: str) -> list[dict]:
    named = re.compile(rf"(?<![A-Za-z0-9]){re.escape(card)}(?!\d)", re.I)
    mentions = [i for i, e in enumerate(events) if named.search(dump(e))]
    if not mentions:
        return []
    starts = [i for i in mentions if START_COMMAND in dump(events[i])]
    window = events[(starts or mentions)[0] :]
    merge = merge_span(window)
    return window if merge is None else window[: merge[1] + 1]


def dump(event: dict) -> str:
    return json.dumps(event).lower()


def content_blocks(event: dict) -> list[dict]:
    message = event.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    blocks = content if isinstance(content, list) else []
    return [block for block in blocks if isinstance(block, dict)]


def tool_uses(event: dict) -> list[dict]:
    return [b for b in content_blocks(event) if b.get("type") == "tool_use"]


def answers_call(event: dict, call_id: str) -> bool:
    return any(
        b.get("type") == "tool_result" and b.get("tool_use_id") == call_id
        for b in content_blocks(event)
    )


def first_text(event: dict) -> str:
    texts = [b.get("text", "") for b in content_blocks(event)]
    return next((t for t in texts if isinstance(t, str) and t), "")


def is_user_prompt(event: dict) -> bool:
    blocks = content_blocks(event)
    is_result = any(b.get("type") == "tool_result" for b in blocks)
    text = first_text(event).lstrip()
    is_automated = text.startswith(AUTOMATED_PREFIXES)
    is_user = event.get("type") == "user" and not event.get("isSidechain")
    return is_user and not is_result and not is_automated


def reviewer_rows(
    card: str, session: Path, window: list[dict]
) -> list[StageRow]:
    first, last = moment(window[0]), moment(window[-1])
    agents = session.with_suffix("") / "subagents"
    logs = sorted(agents.glob("agent-*.jsonl")) if agents.is_dir() else []
    rows = [reviewer_row(card, log) for log in logs]
    return [
        row
        for row in rows
        if row and first <= datetime.fromisoformat(row.started_at) <= last
    ]


def reviewer_row(card: str, log: Path) -> StageRow | None:
    try:
        events = timed(SessionLog.from_path(log).events)
    except OSError:
        return None
    prompt = first_text(events[0]) if events else ""
    stage = stage_named_by(prompt)
    if stage is None:
        return None
    lens = LENS_PATTERN.search(prompt)
    meta = reviewer_meta(log.with_name(f"{log.stem}.meta.json"))
    return stage_row(
        card,
        stage,
        [moment(event) for event in events],
        lens.group(1) if lens else "",
        meta.get("model", ""),
        meta.get("effort", ""),
    )


def stage_named_by(prompt: str) -> str | None:
    opening = prompt[:BRIEF_SEARCH_LENGTH]
    return next((s for brief, s in REVIEWER_BRIEFS if brief in opening), None)


def reviewer_meta(path: Path) -> dict:
    try:
        meta = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return meta if isinstance(meta, dict) else {}


def build_rows(
    card: str, window: list[dict], reviewers: list[StageRow]
) -> list[StageRow]:
    edits = [
        e for e in window if any(c["name"] in EDIT_TOOLS for c in tool_uses(e))
    ]
    if not edits:
        return []
    edited = moment(edits[0])
    spawns = [datetime.fromisoformat(r.started_at) for r in reviewers]
    after_edit = [spawn for spawn in spawns if spawn > edited]
    if not after_edit:
        return []
    spawned = min(after_edit)
    during = [moment(e) for e in window if edited <= moment(e) <= spawned]
    return [stage_row(card, BUILD, [*during, spawned])]


def merge_span(events: list[dict]) -> tuple[int, int] | None:
    for index, event in enumerate(events):
        for call in tool_uses(event):
            command = call.get("input", {}).get("command", "")
            if call["name"] == "Bash" and MERGE_COMMAND.match(command):
                result = result_index(events, index, call["id"])
                if result is not None:
                    return index, result
    return None


def result_index(events: list[dict], after: int, call_id: str) -> int | None:
    later = range(after + 1, len(events))
    return next((i for i in later if answers_call(events[i], call_id)), None)


def merge_rows(card: str, window: list[dict]) -> list[StageRow]:
    span = merge_span(window)
    if span is None:
        return []
    return [stage_row(card, MERGE, [moment(window[i]) for i in span])]


def wait_rows(card: str, window: list[dict]) -> list[StageRow]:
    conversation = [e for e in window if e.get("type") in CONVERSATION]
    pairs = zip(conversation, conversation[1:])
    return [
        stage_row(card, WAIT, [moment(asked), moment(answered)])
        for asked, answered in pairs
        if waited_on_user(asked, answered)
    ]


def waited_on_user(asked: dict, answered: dict) -> bool:
    if asked.get("type") != "assistant" or answered.get("type") != "user":
        return False
    calls = tool_uses(asked)
    if not calls:
        return is_user_prompt(answered)
    return any(
        call["name"] == ASK_TOOL and answers_call(answered, call["id"])
        for call in calls
    )


def number_runs(rows: list[StageRow]) -> list[StageRow]:
    seen: Counter = Counter()
    numbered = []
    for row in sorted(rows, key=lambda row: row.started_at):
        if row.stage in REVIEWER_STAGES:
            seen[(row.stage, row.lens)] += 1
            row = replace(row, run=seen[(row.stage, row.lens)])
        numbered.append(row)
    return numbered


def replace_card_rows(store: Cache, card: str, rows: list[StageRow]):
    with store.transact():
        for key in [key for key in store.iterkeys() if key[0] == card]:
            del store[key]
        for row in rows:
            store[row.key] = row.as_dict()


def ensure_excluded(checkout: Path):
    exclude = (
        Path(
            read_git_output(
                checkout,
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            )
        )
        / "info"
        / "exclude"
    )
    lines = exclude.read_text().splitlines() if exclude.exists() else []
    if EXCLUDE_LINE not in lines:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text("\n".join([*lines, EXCLUDE_LINE]) + "\n")


def open_store(checkout: Path) -> Cache:
    root = main_checkout_path(checkout)
    ensure_excluded(root)
    return Cache(str(root / STORE_FOLDER))


def merged_cards(checkout: Path, count: int) -> list[str]:
    subjects = read_git_output(
        checkout, "log", "main", "--merges", "--format=%s"
    ).splitlines()
    cards = [
        match.group(0).upper()
        for s in subjects
        if (match := CARD_PATTERN.search(s))
    ]
    return list(dict.fromkeys(cards))[:count]


def logs_folder_name(working_dir: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(working_dir))


def report_text(store: Cache, cards: list[str]) -> str:
    rows = [
        StageRow(**store[key]) for key in store.iterkeys() if key[0] in cards
    ]
    by_stage = defaultdict(list)
    for row in rows:
        by_stage[row.stage].append(row)
    stages = sorted(
        by_stage,
        key=lambda s: max(r.seconds for r in by_stage[s]),
        reverse=True,
    )
    recorded = {row.card for row in rows}
    slow = [s for s in stages if slowest(by_stage[s]) > SLOW_SECONDS]
    silent = [card for card in cards if card not in recorded]
    return "\n".join(
        [
            f"Stage times over the last {len(cards)} merged cards",
            "",
            "| Stage | Median (s) | Slowest (s) | Repeats |",
            "|:--|--:|--:|--:|",
            *[stage_line(s, by_stage[s]) for s in stages],
            "",
            f"Over {SLOW_SECONDS} s: {', '.join(slow) or 'none'}",
            f"No rows: {', '.join(silent) or 'none'}",
        ]
    )


def slowest(rows: list[StageRow]) -> float:
    return max(row.seconds for row in rows)


def stage_line(stage: str, rows: list[StageRow]) -> str:
    median = statistics.median(row.seconds for row in rows)
    return f"| {stage} | {median:.1f} | {slowest(rows):.1f} | {repeats(rows)} |"


def repeats(rows: list[StageRow]) -> int:
    latest_run: dict[str, int] = defaultdict(int)
    for row in rows:
        latest_run[row.card] = max(latest_run[row.card], row.run)
    return sum(run - 1 for run in latest_run.values())


@click.group()
@click.option(
    "--checkout",
    type=click.Path(path_type=Path),
    default=Path.cwd,
    help="Repository to work in; defaults to the current folder",
)
@click.pass_context
def main(context: click.Context, checkout: Path):
    context.obj = checkout


@main.command("record")
@click.argument("card")
@click.option(
    "--logs-folder",
    "folders",
    multiple=True,
    type=click.Path(path_type=Path),
    help="Folder of session logs; defaults to the one Claude Code saved for --working-dir",
)
@click.option(
    "--working-dir",
    type=click.Path(path_type=Path),
    help="Folder the card's session started in; defaults to the checkout",
)
@click.pass_obj
def record_command(
    checkout: Path,
    card: str,
    folders: tuple[Path, ...],
    working_dir: Path | None,
):
    default_folder = CLAUDE_LOGS / logs_folder_name(
        (working_dir or checkout).resolve()
    )
    store = open_store(checkout)
    rows = record_card(card, list(folders) or [default_folder], store)
    if not rows:
        click.echo(f"{card}: no readable session log found, nothing recorded")
    else:
        click.echo(f"{card}: recorded {len(rows)} stage rows")


@main.command("report")
@click.option("--cards", default=DEFAULT_CARD_COUNT, show_default=True)
@click.pass_obj
def report_command(checkout: Path, cards: int):
    store = open_store(checkout)
    click.echo(report_text(store, merged_cards(checkout, cards)))


if __name__ == "__main__":
    main()
