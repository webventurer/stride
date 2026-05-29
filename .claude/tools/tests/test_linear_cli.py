"""Tests for linear_cli.

linear_cli talks Linear's GraphQL API directly via `requests`, so these
tests are pure-function and `requests.post`-mocked — they run without
network access. Live behaviour is exercised by driving a real /linear:*
cycle, not from here.

Run with:
    python -m pytest .claude/tools/tests/test_linear_cli.py
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the tools directory to the path so we can import linear_cli
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from linear_cli import (  # noqa: E402
    LinearError,
    LinctlError,
    bearer_token,
    board_states,
    create_milestone,
    create_workflow_state,
    declared_states,
    graphql,
    issues_query,
    linctl_graphql,
    list_by_parent,
    list_by_project_state,
    list_by_project_state_type,
    list_milestones,
    milestone_open_issues,
    min_backlog_sort_order,
    operation_name,
    order_states,
    project_content,
    provision_states,
    raise_for_graphql_errors,
    raise_for_http,
    search_by_project,
    set_sort_order,
    state_drift,
    update_milestone_description,
    update_project_content,
)


def ok_response(data: dict) -> MagicMock:
    """Mock requests.Response carrying a successful GraphQL data payload."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"data": data}
    resp.text = json.dumps({"data": data})
    return resp


def error_response(status_code: int, body: str) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = body
    resp.json.return_value = {}
    return resp


def graphql_errors_response(errors: list) -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"errors": errors}
    resp.text = json.dumps({"errors": errors})
    return resp


def sent_body(mock: MagicMock) -> dict:
    """Return the JSON body sent with the most recent requests.post call."""
    return mock.call_args.kwargs["json"]


def sent_query(mock: MagicMock) -> str:
    return sent_body(mock)["query"]


def sent_variables(mock: MagicMock) -> dict:
    return sent_body(mock).get("variables", {})


# ---- plumbing ----


def test_legacy_linctl_error_alias_resolves_to_linear_error():
    assert LinctlError is LinearError


def test_issues_query_embeds_params_filters_and_node_fields():
    query = issues_query("$x: String!", "project: { name: { eq: $x } }")

    assert query.startswith("query($x: String!)")
    assert "project: { name: { eq: $x } }" in query
    assert "identifier title state { name type }" in query


def test_raise_for_http_raises_on_4xx_with_body_snippet():
    resp = error_response(401, "Unauthorized: bad token")

    with pytest.raises(LinearError) as excinfo:
        raise_for_http(resp, "query { viewer { id } }")

    assert "401" in str(excinfo.value)
    assert "Unauthorized" in str(excinfo.value)


def test_raise_for_http_passes_on_2xx():
    resp = MagicMock()
    resp.status_code = 200

    raise_for_http(resp, "query { x }")  # does not raise


def test_raise_for_graphql_errors_raises_when_errors_present():
    with pytest.raises(LinearError) as excinfo:
        raise_for_graphql_errors({"errors": [{"message": "bad filter"}]}, "query { x }")

    assert "bad filter" in str(excinfo.value)


def test_raise_for_graphql_errors_passes_when_no_errors():
    raise_for_graphql_errors({"data": {}}, "query { x }")  # does not raise


def test_operation_name_extracts_named_query():
    assert operation_name("query MyQuery($x: String!) { foo }") == "MyQuery"


def test_operation_name_falls_back_to_first_field():
    assert operation_name("{ viewer { id } }") == "viewer"


def test_bearer_token_prefers_linear_api_key_over_legacy():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_canonical", "LINCTL_API_KEY": "lin_legacy"}, clear=False):
        assert bearer_token() == "lin_canonical"


def test_bearer_token_falls_back_to_legacy_linctl_env():
    env = {"LINCTL_API_KEY": "lin_legacy"}
    with patch.dict("os.environ", env, clear=True):
        assert bearer_token() == "lin_legacy"


def test_bearer_token_raises_when_no_credentials():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(LinearError) as excinfo:
            bearer_token()

    assert "LINEAR_API_KEY" in str(excinfo.value)


def test_graphql_sends_query_and_variables_to_linear_endpoint():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear_cli.requests.post", return_value=ok_response({"viewer": {"id": "u1"}})) as mock:
            result = graphql("lin_test", "query { viewer { id } }", variables={"x": 1})

    assert result == {"data": {"viewer": {"id": "u1"}}}
    args, kwargs = mock.call_args
    assert args[0] == "https://api.linear.app/graphql"
    assert kwargs["json"] == {"query": "query { viewer { id } }", "variables": {"x": 1}}
    assert kwargs["headers"]["Authorization"] == "lin_test"


def test_linctl_graphql_returns_data_payload_not_full_body():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear_cli.requests.post", return_value=ok_response({"viewer": {"id": "u1"}})):
            assert linctl_graphql("query { viewer { id } }", {}) == {"viewer": {"id": "u1"}}


def test_linctl_graphql_raises_on_graphql_errors():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear_cli.requests.post", return_value=graphql_errors_response([{"message": "bad filter"}])):
            with pytest.raises(LinearError) as excinfo:
                linctl_graphql("query { x }", {})

    assert "bad filter" in str(excinfo.value)


# ---- issue queries ----


def issues(nodes: list) -> dict:
    return {"issues": {"nodes": nodes}}


def with_env_and_mock(data: dict):
    """Context-manager helper: patch env + requests.post returning the given data."""

    def make_response():
        return ok_response(data)

    return patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False), patch(
        "linear_cli.requests.post", return_value=make_response()
    )


def test_search_by_project_passes_variables_and_returns_nodes():
    env, post = with_env_and_mock(issues([{"identifier": "WB-1"}]))
    with env, post as mock:
        result = search_by_project("Stride", "linctl")

    assert result == [{"identifier": "WB-1"}]
    assert sent_variables(mock) == {"project": "Stride", "text": "linctl"}
    assert "searchableContent: { contains: $text }" in sent_query(mock)


def test_list_by_project_state_adds_since_filter_when_given():
    env, post = with_env_and_mock(issues([]))
    with env, post as mock:
        list_by_project_state("Stride", "Done", since="-P1W")

    assert sent_variables(mock)["since"] == "-P1W"
    assert "createdAt: { gt: $since }" in sent_query(mock)


def test_list_by_project_state_omits_since_when_absent():
    env, post = with_env_and_mock(issues([]))
    with env, post as mock:
        list_by_project_state("Stride", "Done")

    assert "since" not in sent_variables(mock)
    assert "createdAt" not in sent_query(mock)


def test_list_by_project_state_type_filters_by_type():
    env, post = with_env_and_mock(issues([]))
    with env, post as mock:
        list_by_project_state_type("Stride", "started")

    assert sent_variables(mock) == {"project": "Stride", "type": "started"}
    assert "state: { type: { eq: $type } }" in sent_query(mock)


def test_list_by_parent_filters_by_parent_id():
    env, post = with_env_and_mock(issues([]))
    with env, post as mock:
        list_by_parent("uuid-123")

    assert sent_variables(mock) == {"parent": "uuid-123"}
    assert "parent: { id: { eq: $parent } }" in sent_query(mock)


# ---- milestones ----


def test_list_milestones_extracts_nested_nodes():
    data = {"project": {"projectMilestones": {"nodes": [{"id": "m1", "name": "Phase 1"}]}}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert list_milestones("proj-1") == [{"id": "m1", "name": "Phase 1"}]


def test_milestone_open_issues_filters_open_states():
    data = {"projectMilestone": {"issues": {"nodes": [{"identifier": "WB-9"}]}}}
    env, post = with_env_and_mock(data)
    with env, post as mock:
        result = milestone_open_issues("m1")

    assert result == [{"identifier": "WB-9"}]
    assert '["backlog", "unstarted", "started"]' in sent_query(mock)


def test_create_milestone_includes_target_date_when_given():
    data = {"projectMilestoneCreate": {"projectMilestone": {"id": "m2", "name": "Q4"}}}
    env, post = with_env_and_mock(data)
    with env, post as mock:
        result = create_milestone("proj-1", "Q4", target_date="2026-12-31")

    assert result == {"id": "m2", "name": "Q4"}
    assert sent_variables(mock)["target"] == "2026-12-31"
    assert "targetDate: $target" in sent_query(mock)


def test_create_milestone_omits_target_date_when_absent():
    data = {"projectMilestoneCreate": {"projectMilestone": {"id": "m3", "name": "Q4"}}}
    env, post = with_env_and_mock(data)
    with env, post as mock:
        create_milestone("proj-1", "Q4")

    assert "target" not in sent_variables(mock)
    assert "targetDate" not in sent_query(mock)


def test_update_milestone_description_returns_success():
    data = {"projectMilestoneUpdate": {"success": True}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert update_milestone_description("m1", "Completed: 2026-05-24") is True


# ---- project content ----


def test_project_content_returns_content():
    data = {"project": {"content": "# Vision: stride\n\n..."}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert project_content("proj-1") == "# Vision: stride\n\n..."


def test_update_project_content_passes_content_and_returns_success():
    data = {"projectUpdate": {"success": True}}
    env, post = with_env_and_mock(data)
    with env, post as mock:
        result = update_project_content("proj-1", "# Vision: stride")

    assert result is True
    assert sent_variables(mock) == {"id": "proj-1", "content": "# Vision: stride"}


# ---- board order ----


def test_min_backlog_sort_order_returns_first_value():
    data = {"project": {"issues": {"nodes": [{"sortOrder": -120450}]}}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert min_backlog_sort_order("proj-1") == -120450


def test_min_backlog_sort_order_returns_none_when_empty():
    data = {"project": {"issues": {"nodes": []}}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert min_backlog_sort_order("proj-1") is None


def test_set_sort_order_passes_float_and_returns_success():
    data = {"issueUpdate": {"success": True}}
    env, post = with_env_and_mock(data)
    with env, post as mock:
        result = set_sort_order("issue-1", -120550.0)

    assert result is True
    assert sent_variables(mock) == {"id": "issue-1", "order": -120550.0}
    assert "$order: Float!" in sent_query(mock)


# ---- workflow-state drift ----


def teams(nodes: list) -> dict:
    return {"teams": {"nodes": nodes}}


def test_board_states_filters_by_team_key_and_flattens_nodes():
    data = teams([{"states": {"nodes": [{"name": "Doing", "type": "started"}]}}])
    env, post = with_env_and_mock(data)
    with env, post as mock:
        result = board_states("WB")

    assert result == [{"name": "Doing", "type": "started"}]
    assert sent_variables(mock) == {"key": "WB"}
    assert "key: { eq: $key }" in sent_query(mock)


def test_board_states_returns_empty_when_no_team_matches():
    env, post = with_env_and_mock(teams([]))
    with env, post:
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
    env, post = with_env_and_mock(board)
    with env, post:
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
    env, post = with_env_and_mock(board)
    with env, post:
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
    env, post = with_env_and_mock(data)
    with env, post as mock:
        create_workflow_state("team-1", "Doing", "started", "#f2c94c", 2.0)

    assert sent_variables(mock)["input"] == {
        "teamId": "team-1",
        "name": "Doing",
        "type": "started",
        "color": "#f2c94c",
        "position": 2.0,
    }
    assert "workflowStateCreate(input: $input)" in sent_query(mock)


def test_order_states_skips_when_already_in_json_order():
    # Doing before In Review by position — matches ONE_TYPE order, so no writes.
    board = [
        {"name": "Doing", "position": 2.0},
        {"name": "In Review", "position": 1069.0},
    ]
    ids = {"Doing": "d", "In Review": "r"}
    with patch("linear_cli.set_state_position") as set_pos:
        assert order_states(ONE_TYPE, board, ids) == []
    set_pos.assert_not_called()


def test_order_states_fixes_out_of_order_states():
    # In Review sits before Doing by position — must be reordered to JSON order.
    board = [
        {"name": "Doing", "position": 5.0},
        {"name": "In Review", "position": 2.0},
    ]
    ids = {"Doing": "d", "In Review": "r"}
    with patch("linear_cli.set_state_position") as set_pos:
        result = order_states(ONE_TYPE, board, ids)

    assert result == ["Doing", "In Review"]
    assert set_pos.call_count == 2


def test_provision_states_creates_missing_and_reports_them():
    board = {"teams": {"nodes": [{"id": "t1", "issues": {"nodes": []}, "states": {"nodes": [
        {"id": "b", "name": "Backlog", "type": "backlog", "position": 0.0},
    ]}}]}}
    created_state = {"workflowStateCreate": {"workflowState": {"id": "new"}}}

    def fake_post(url: str, json: dict | None = None, headers: dict | None = None, **kwargs) -> MagicMock:
        query = json["query"]
        return ok_response(board if "teams(" in query else created_state)

    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear_cli.requests.post", side_effect=fake_post):
            with patch("linear_cli.load_statuses", return_value={"states": {"backlog": ["Backlog"], "started": ["Doing"]}}):
                result = provision_states("WB")

    assert result["created"] == [{"name": "Doing", "type": "started"}]
    assert result["in_sync"] is False


def test_provision_states_in_sync_when_board_has_all_canonical():
    board = {"teams": {"nodes": [{"id": "t1", "issues": {"nodes": []}, "states": {"nodes": [
        {"id": "b", "name": "Backlog", "type": "backlog", "position": 0.0},
        {"id": "d", "name": "Doing", "type": "started", "position": 1.0},
    ]}}]}}
    env, post = with_env_and_mock(board)
    with env, post as mock:
        with patch("linear_cli.load_statuses", return_value={"states": {"backlog": ["Backlog"], "started": ["Doing"]}}):
            result = provision_states("WB")

    assert result == {
        "mode": "provisioned",
        "created": [],
        "deleted": [],
        "reordered": [],
        "in_sync": True,
    }
    # only the read query ran — no create/update mutations
    assert mock.call_count == 1
