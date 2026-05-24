"""Tests for linear_cli.

linear_cli builds GraphQL and shells out to `linctl graphql`, so these
tests are pure-function and subprocess-mocked — they run without network,
linctl, or LINEAR_E2E. Live behaviour is exercised by driving a real
/linear:* cycle, not from here.

Run with:
    python -m pytest tools/tests/test_linear_cli.py
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the tools directory to the path so we can import linear_cli
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from linear_cli import (  # noqa: E402
    LinctlError,
    board_states,
    create_milestone,
    create_workflow_state,
    declared_states,
    graphql_data,
    issues_query,
    linctl_graphql,
    list_by_parent,
    list_by_project_state,
    list_by_project_state_type,
    list_milestones,
    milestone_open_issues,
    min_backlog_sort_order,
    project_content,
    provision_states,
    raise_for_failure,
    reorder_canonical,
    search_by_project,
    set_sort_order,
    state_drift,
    update_milestone_description,
    update_project_content,
)


def ok_run(data: dict) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess([], returncode=0, stdout=json.dumps({"data": data}), stderr="")


def issues(nodes: list) -> dict:
    return {"issues": {"nodes": nodes}}


def sent_query(mock: MagicMock) -> str:
    args = mock.call_args[0][0]
    return args[args.index("--query") + 1]


def sent_variables(mock: MagicMock) -> dict:
    args = mock.call_args[0][0]
    return json.loads(args[args.index("--variables") + 1])


# ---- plumbing ----

def test_issues_query_embeds_params_filters_and_node_fields():
    query = issues_query("$x: String!", "project: { name: { eq: $x } }")

    assert query.startswith("query($x: String!)")
    assert "project: { name: { eq: $x } }" in query
    assert "identifier title state { name type }" in query


def test_graphql_data_returns_data_payload():
    stdout = json.dumps({"data": {"issues": {"nodes": [{"identifier": "WB-1"}]}}})

    assert graphql_data(stdout) == {"issues": {"nodes": [{"identifier": "WB-1"}]}}


def test_graphql_data_raises_on_graphql_errors():
    stdout = json.dumps({"errors": [{"message": "bad filter"}]})

    with pytest.raises(LinctlError) as excinfo:
        graphql_data(stdout)

    assert "bad filter" in str(excinfo.value)


def test_raise_for_failure_raises_with_stderr_on_nonzero():
    result = subprocess.CompletedProcess([], returncode=1, stdout="", stderr="boom")

    with pytest.raises(LinctlError) as excinfo:
        raise_for_failure(result)

    assert "boom" in str(excinfo.value)


def test_raise_for_failure_passes_on_zero():
    result = subprocess.CompletedProcess([], returncode=0, stdout="{}", stderr="")

    raise_for_failure(result)  # does not raise


def test_linctl_graphql_raises_on_subprocess_failure():
    failed = subprocess.CompletedProcess([], returncode=1, stdout="", stderr="auth error")

    with patch("linear_cli.subprocess.run", return_value=failed):
        with pytest.raises(LinctlError) as excinfo:
            linctl_graphql("query { x }", {})

    assert "auth error" in str(excinfo.value)


# ---- issue queries ----

def test_search_by_project_passes_variables_and_returns_nodes():
    with patch("linear_cli.subprocess.run", return_value=ok_run(issues([{"identifier": "WB-1"}]))) as mock:
        result = search_by_project("Stride", "linctl")

    assert result == [{"identifier": "WB-1"}]
    assert sent_variables(mock) == {"project": "Stride", "text": "linctl"}
    assert "searchableContent: { contains: $text }" in sent_query(mock)


def test_list_by_project_state_adds_since_filter_when_given():
    with patch("linear_cli.subprocess.run", return_value=ok_run(issues([]))) as mock:
        list_by_project_state("Stride", "Done", since="-P1W")

    assert sent_variables(mock)["since"] == "-P1W"
    assert "createdAt: { gt: $since }" in sent_query(mock)


def test_list_by_project_state_omits_since_when_absent():
    with patch("linear_cli.subprocess.run", return_value=ok_run(issues([]))) as mock:
        list_by_project_state("Stride", "Done")

    assert "since" not in sent_variables(mock)
    assert "createdAt" not in sent_query(mock)


def test_list_by_project_state_type_filters_by_type():
    # "Started issues" spans Doing/In Review/Waiting — filter by state TYPE, not a name.
    with patch("linear_cli.subprocess.run", return_value=ok_run(issues([]))) as mock:
        list_by_project_state_type("Stride", "started")

    assert sent_variables(mock) == {"project": "Stride", "type": "started"}
    assert "state: { type: { eq: $type } }" in sent_query(mock)


def test_list_by_parent_filters_by_parent_id():
    with patch("linear_cli.subprocess.run", return_value=ok_run(issues([]))) as mock:
        list_by_parent("uuid-123")

    assert sent_variables(mock) == {"parent": "uuid-123"}
    assert "parent: { id: { eq: $parent } }" in sent_query(mock)


# ---- milestones ----

def test_list_milestones_extracts_nested_nodes():
    data = {"project": {"projectMilestones": {"nodes": [{"id": "m1", "name": "Phase 1"}]}}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)):
        assert list_milestones("proj-1") == [{"id": "m1", "name": "Phase 1"}]


def test_milestone_open_issues_filters_open_states():
    data = {"projectMilestone": {"issues": {"nodes": [{"identifier": "WB-9"}]}}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)) as mock:
        result = milestone_open_issues("m1")

    assert result == [{"identifier": "WB-9"}]
    assert '["backlog", "unstarted", "started"]' in sent_query(mock)


def test_create_milestone_includes_target_date_when_given():
    data = {"projectMilestoneCreate": {"projectMilestone": {"id": "m2", "name": "Q4"}}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)) as mock:
        result = create_milestone("proj-1", "Q4", target_date="2026-12-31")

    assert result == {"id": "m2", "name": "Q4"}
    assert sent_variables(mock)["target"] == "2026-12-31"
    assert "targetDate: $target" in sent_query(mock)


def test_create_milestone_omits_target_date_when_absent():
    data = {"projectMilestoneCreate": {"projectMilestone": {"id": "m3", "name": "Q4"}}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)) as mock:
        create_milestone("proj-1", "Q4")

    assert "target" not in sent_variables(mock)
    assert "targetDate" not in sent_query(mock)


def test_update_milestone_description_returns_success():
    data = {"projectMilestoneUpdate": {"success": True}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)):
        assert update_milestone_description("m1", "Completed: 2026-05-24") is True


# ---- project content ----

def test_linctl_graphql_isolates_stdin():
    # linctl treats a piped stdin as a competing query source alongside --query;
    # the subprocess call must close stdin or every live graphql call fails.
    with patch("linear_cli.subprocess.run", return_value=ok_run({"viewer": {"id": "u1"}})) as mock:
        linctl_graphql("{ viewer { id } }", {})
    assert mock.call_args.kwargs.get("stdin") == subprocess.DEVNULL


def test_project_content_returns_content():
    data = {"project": {"content": "# Vision: stride\n\n..."}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)):
        assert project_content("proj-1") == "# Vision: stride\n\n..."


def test_update_project_content_passes_content_and_returns_success():
    data = {"projectUpdate": {"success": True}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)) as mock:
        result = update_project_content("proj-1", "# Vision: stride")

    assert result is True
    assert sent_variables(mock) == {"id": "proj-1", "content": "# Vision: stride"}


# ---- board order ----

def test_min_backlog_sort_order_returns_first_value():
    data = {"project": {"issues": {"nodes": [{"sortOrder": -120450}]}}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)):
        assert min_backlog_sort_order("proj-1") == -120450


def test_min_backlog_sort_order_returns_none_when_empty():
    data = {"project": {"issues": {"nodes": []}}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)):
        assert min_backlog_sort_order("proj-1") is None


def test_set_sort_order_passes_float_and_returns_success():
    data = {"issueUpdate": {"success": True}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)) as mock:
        result = set_sort_order("issue-1", -120550.0)

    assert result is True
    assert sent_variables(mock) == {"id": "issue-1", "order": -120550.0}
    assert "$order: Float!" in sent_query(mock)


# ---- workflow-state drift ----

def teams(nodes: list) -> dict:
    return {"teams": {"nodes": nodes}}


def test_board_states_filters_by_team_key_and_flattens_nodes():
    data = teams([{"states": {"nodes": [{"name": "Doing", "type": "started"}]}}])
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)) as mock:
        result = board_states("WB")

    assert result == [{"name": "Doing", "type": "started"}]
    assert sent_variables(mock) == {"key": "WB"}
    assert "key: { eq: $key }" in sent_query(mock)


def test_board_states_returns_empty_when_no_team_matches():
    with patch("linear_cli.subprocess.run", return_value=ok_run(teams([]))):
        assert board_states("NOPE") == []


def test_declared_states_flattens_grouped_names_into_typed_pairs():
    config = {"states": {"started": ["Doing", "In Review"], "completed": ["Done"]}}

    assert declared_states(config) == {
        ("Doing", "started"),
        ("In Review", "started"),
        ("Done", "completed"),
    }


def test_state_drift_flags_declared_state_missing_from_board():
    statuses = {"states": {"started": ["Doing", "In Progress"]}}
    board = teams([{"states": {"nodes": [{"name": "Doing", "type": "started"}]}}])
    with patch("linear_cli.subprocess.run", return_value=ok_run(board)):
        with patch("linear_cli.load_statuses", return_value=statuses):
            assert state_drift("WB") == [{"name": "In Progress", "type": "started"}]


def test_state_drift_empty_when_board_carries_every_declared_state():
    statuses = {"states": {"started": ["Doing"]}}
    board = teams(
        [{"states": {"nodes": [
            {"name": "Doing", "type": "started"},
            {"name": "Done", "type": "completed"},
        ]}}]
    )
    with patch("linear_cli.subprocess.run", return_value=ok_run(board)):
        with patch("linear_cli.load_statuses", return_value=statuses):
            assert state_drift("WB") == []


def test_load_statuses_parses_the_repo_config():
    from linear_cli import load_statuses as real_load

    config = real_load()

    assert "states" in config and "transitions" in config
    assert "Doing" in config["states"]["started"]


# ---- workflow-state provisioning ----

ONE_TYPE = {"started": ["Doing", "In Review"]}


def test_create_workflow_state_passes_typed_input_and_color():
    data = {"workflowStateCreate": {"workflowState": {"id": "s1", "name": "Doing"}}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(data)) as mock:
        create_workflow_state("team-1", "Doing", "started", "#f2c94c", 2.0)

    assert sent_variables(mock)["input"] == {
        "teamId": "team-1",
        "name": "Doing",
        "type": "started",
        "color": "#f2c94c",
        "position": 2.0,
    }
    assert "workflowStateCreate(input: $input)" in sent_query(mock)


def test_reorder_canonical_skips_when_already_in_json_order():
    # Doing before In Review by position — matches ONE_TYPE order, so no writes.
    pos = {"Doing": 2.0, "In Review": 1069.0}
    ids = {"Doing": "d", "In Review": "r"}
    with patch("linear_cli.set_state_position") as set_pos:
        assert reorder_canonical(ONE_TYPE, pos, ids) == []
    set_pos.assert_not_called()


def test_reorder_canonical_fixes_out_of_order_states():
    # In Review sits before Doing by position — must be reordered to JSON order.
    pos = {"Doing": 5.0, "In Review": 2.0}
    ids = {"Doing": "d", "In Review": "r"}
    with patch("linear_cli.set_state_position") as set_pos:
        result = reorder_canonical(ONE_TYPE, pos, ids)

    assert result == ["Doing", "In Review"]
    assert set_pos.call_count == 2


def test_provision_states_creates_missing_and_reports_them():
    board = {"teams": {"nodes": [{"id": "t1", "states": {"nodes": [
        {"id": "b", "name": "Backlog", "type": "backlog", "position": 0.0},
    ]}}]}}
    created_state = {"workflowStateCreate": {"workflowState": {"id": "new"}}}

    def fake_run(args: list, **kwargs) -> subprocess.CompletedProcess:
        query = args[args.index("--query") + 1]
        return ok_run(board if "teams(" in query else created_state)

    with patch("linear_cli.subprocess.run", side_effect=fake_run):
        with patch("linear_cli.load_statuses", return_value={"states": {"backlog": ["Backlog"], "started": ["Doing"]}}):
            result = provision_states("WB")

    assert result["created"] == [{"name": "Doing", "type": "started"}]
    assert result["in_sync"] is False


def test_provision_states_in_sync_when_board_has_all_canonical():
    board = {"teams": {"nodes": [{"id": "t1", "states": {"nodes": [
        {"id": "b", "name": "Backlog", "type": "backlog", "position": 0.0},
        {"id": "d", "name": "Doing", "type": "started", "position": 1.0},
    ]}}]}}
    with patch("linear_cli.subprocess.run", return_value=ok_run(board)) as mock:
        with patch("linear_cli.load_statuses", return_value={"states": {"backlog": ["Backlog"], "started": ["Doing"]}}):
            result = provision_states("WB")

    assert result == {"created": [], "reordered": [], "in_sync": True}
    # only the read query ran — no create/update mutations
    assert mock.call_count == 1
