"""
Measure how much of the plan one batch run used, session by session.

Reads every Claude Code session log in a run folder, wherever it was saved,
and reports each session's use from the usage totals Claude Code records at
the end of every turn, which include the advisor. Use is the list-price cost
of the tokens, so every model sits on one scale; the captain's first turn is
reported apart as its planning.

It owns reading the logs and adding them up; running the batch and judging
its work belong to the parallel-sessions skill.
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import click

CAPTAIN_LOG = "captain.log"
LOGS_OUTSIDE_THE_BATCH = {"judge.log", "writer.log"}
LOG_SUFFIXES = {".jsonl", ".log"}
TOKEN_FIELDS = (
    "inputTokens",
    "cacheCreationInputTokens",
    "cacheReadInputTokens",
    "outputTokens",
)
USE_DECIMAL_PLACES = 4


@dataclass
class SessionLog:
    """One Claude Code session's stream-json log."""

    path: Path
    events: list[dict] = field(default_factory=list)

    @classmethod
    def from_path(cls, path: Path) -> "SessionLog":
        lines = path.read_text(errors="replace").splitlines()
        events = [parsed_event(line) for line in lines if line.startswith("{")]
        return cls(path, [event for event in events if event])

    @property
    def session_id(self) -> str:
        inits = [e for e in self.events if e.get("subtype") == "init"]
        return inits[0].get("session_id", "") if inits else ""

    @property
    def holder(self) -> str:
        return self.path.name.split(".")[0]

    @property
    def usage_totals(self) -> list[dict]:
        results = [e for e in self.events if e.get("type") == "result"]
        return [result.get("modelUsage") or {} for result in results]

    @property
    def usage(self) -> dict:
        return self.usage_totals[-1] if self.usage_totals else {}

    @property
    def first_turn_usage(self) -> dict:
        return self.usage_totals[0] if self.usage_totals else {}

    @property
    def times(self) -> list[datetime]:
        stamps = [e["timestamp"] for e in self.events if "timestamp" in e]
        return [datetime.fromisoformat(stamp) for stamp in stamps]

    @property
    def seconds_taken(self) -> float:
        return seconds_spanned(self.times)


def parsed_event(line: str) -> dict | None:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def seconds_spanned(times: list[datetime]) -> float:
    return (max(times) - min(times)).total_seconds() if times else 0.0


@click.command()
@click.argument("run_dir", type=click.Path(exists=True, path_type=Path))
def main(run_dir: Path):
    click.echo(json.dumps(use_report(run_dir), indent=2))


def use_report(run_dir: Path) -> dict:
    logs = session_logs(run_dir)
    captain_logs = [log for log in logs if log.path.name == CAPTAIN_LOG]
    soldier_logs = [log for log in logs if log.path.name != CAPTAIN_LOG]
    report = {
        "captain": captain_report(captain_logs),
        "soldiers": soldier_reports(soldier_logs),
    }
    return {**report, "total_use": total_use(report)}


def session_logs(run_dir: Path) -> list[SessionLog]:
    paths = [path for path in sorted(run_dir.rglob("*")) if is_batch_log(path)]
    logs = [SessionLog.from_path(path) for path in paths]
    return [log for log in logs if log.session_id]


def is_batch_log(path: Path) -> bool:
    is_in_git = ".git" in path.parts
    is_outside_batch = path.name in LOGS_OUTSIDE_THE_BATCH
    is_log = path.suffix in LOG_SUFFIXES and path.is_file()
    return is_log and not is_in_git and not is_outside_batch


def captain_report(logs: list[SessionLog]) -> dict:
    usage = logs[-1].usage if logs else {}
    planning = weighted_use(logs[0].first_turn_usage) if logs else 0.0
    total = weighted_use(usage)
    running = round(total - planning, USE_DECIMAL_PLACES)
    return {
        "planning": planning,
        "running": running,
        "total": total,
        "tokens_by_model": tokens_by_model(usage),
    }


def soldier_reports(logs: list[SessionLog]) -> dict:
    logs_by_session = defaultdict(list)
    for log in logs:
        logs_by_session[log.session_id].append(log)
    sessions = sorted(logs_by_session.values(), key=lambda s: s[0].path.name)
    return dict(session_report(session) for session in sessions)


def session_report(logs: list[SessionLog]) -> tuple[str, dict]:
    latest = max(logs, key=lambda log: max(log.times, default=datetime.min))
    times = [time for log in logs for time in log.times]
    report = {
        "use": weighted_use(latest.usage),
        "resume_count": len(logs) - 1,
        "seconds": seconds_spanned(times),
        "tokens_by_model": tokens_by_model(latest.usage),
    }
    return logs[0].holder, report


def tokens_by_model(usage: dict) -> dict:
    return {
        model: {name: counts.get(name, 0) for name in TOKEN_FIELDS}
        for model, counts in usage.items()
    }


def weighted_use(usage: dict) -> float:
    costs = [counts.get("costUSD", 0.0) for counts in usage.values()]
    return round(sum(costs), USE_DECIMAL_PLACES)


def total_use(report: dict) -> float:
    soldiers_use = sum(
        soldier["use"] for soldier in report["soldiers"].values()
    )
    return round(report["captain"]["total"] + soldiers_use, USE_DECIMAL_PLACES)


if __name__ == "__main__":
    main()
