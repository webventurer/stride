"""Tests for the label recovery commands, with Linear replaced.

Each command is run through click the way the runbook runs it, with the
Linear client's network calls swapped for fixed data, so the output the
runbook relies on is checked without a workspace.
"""

import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import label_recovery  # noqa: E402

LABELS = [
    {"id": "l1", "name": "Story", "color": "#4cb782", "team": {"id": "t1"}},
    {"id": "l2", "name": "Bug", "color": "#eb5757", "team": None},
    {"id": "l3", "name": "Epic", "color": "#5e6ad2", "team": {"id": "t1"}},
]


def run(*args: str) -> str:
    result = CliRunner().invoke(label_recovery.cli, list(args))
    assert result.exit_code == 0, result.output
    return result.output


def test_team_labels_lists_only_team_scoped(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(label_recovery, "bearer_token", lambda: "key")
    monkeypatch.setattr(label_recovery, "list_labels", lambda key: LABELS)

    output = run("team-labels")

    assert output.splitlines() == [
        "l1 | Story | #4cb782",
        "l3 | Epic | #5e6ad2",
    ]


def test_graphql_prints_what_the_client_returns(
    monkeypatch: pytest.MonkeyPatch,
):
    sent = []

    def fake_graphql_data(query: str, variables: dict) -> dict:
        sent.append((query, variables))
        return {"viewer": {"id": "u1"}}

    monkeypatch.setattr(label_recovery, "graphql_data", fake_graphql_data)

    output = run("graphql", "query { viewer { id } }")

    assert output.strip() == "{'viewer': {'id': 'u1'}}"
    assert sent == [("query { viewer { id } }", {})]
