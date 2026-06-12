"""Tests for linear_cli.

linear_cli talks Linear's GraphQL API directly via `requests`, so these
tests are pure-function and `requests.post`-mocked — they run without
network access. Live behaviour is exercised by driving a real /linear:*
cycle, not from here.

Run with:
    python -m pytest .claude/tools/tests/test_linear_cli.py
"""

import io
import json
import sys
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

# Add the tools directory to the path so we can import linear_cli
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import linear_cli  # noqa: E402
from linear import (  # noqa: E402
    LinearError,
    looks_like_uuid,
    read_text_arg,
    bearer_token,
    board_order,
    board_states,
    create_comment,
    create_issue,
    create_milestone,
    create_project,
    create_workflow_state,
    project_config,
    token_from_project_config,
    declared_states,
    get_issue,
    get_project,
    get_team,
    graphql,
    issues_query,
    graphql_data,
    in_canonical_order,
    list_by_parent,
    list_by_project_state,
    list_by_project_state_type,
    list_comments,
    list_milestones,
    list_projects,
    list_team_states,
    list_teams,
    milestone_open_issues,
    min_backlog_sort_order,
    operation_name,
    order_states,
    project_content,
    provision_states,
    raise_for_graphql_errors,
    raise_for_http,
    resolve_labels_for_team,
    resolve_project_id,
    resolve_state_for_issue,
    search_by_project,
    set_project_view_manual,
    set_sort_order,
    state_drift,
    update_issue,
    update_milestone_description,
    update_project_content,
    view_pref_id_for,
    whoami,
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


def test_issues_query_embeds_params_filters_and_node_fields():
    query = issues_query("$x: String!", "project: { name: { eq: $x } }")

    assert query.startswith("query($x: String!)")
    assert "project: { name: { eq: $x } }" in query
    assert "identifier title sortOrder state { name type }" in query


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


def test_bearer_token_raises_when_no_credentials():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(LinearError) as excinfo:
            bearer_token()

    assert "LINEAR_API_KEY" in str(excinfo.value)


def test_graphql_sends_query_and_variables_to_linear_endpoint():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear.requests.post", return_value=ok_response({"viewer": {"id": "u1"}})) as mock:
            result = graphql("lin_test", "query { viewer { id } }", variables={"x": 1})

    assert result == {"data": {"viewer": {"id": "u1"}}}
    args, kwargs = mock.call_args
    assert args[0] == "https://api.linear.app/graphql"
    assert kwargs["json"] == {"query": "query { viewer { id } }", "variables": {"x": 1}}
    assert kwargs["headers"]["Authorization"] == "lin_test"


def test_graphql_data_returns_data_payload_not_full_body():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear.requests.post", return_value=ok_response({"viewer": {"id": "u1"}})):
            assert graphql_data("query { viewer { id } }", {}) == {"viewer": {"id": "u1"}}


def test_graphql_data_raises_on_graphql_errors():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear.requests.post", return_value=graphql_errors_response([{"message": "bad filter"}])):
            with pytest.raises(LinearError) as excinfo:
                graphql_data("query { x }", {})

    assert "bad filter" in str(excinfo.value)


# ---- issue queries ----


def issues(nodes: list) -> dict:
    return {"issues": {"nodes": nodes}}


def projects_page(nodes: list) -> dict:
    return {
        "projects": {
            "nodes": nodes,
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        },
    }


def with_env_and_mock(data: dict):
    """Context-manager helper: patch env + requests.post returning the given data."""

    def make_response():
        return ok_response(data)

    return patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False), patch(
        "linear.requests.post", return_value=make_response()
    )


def test_search_by_project_passes_variables_and_returns_nodes():
    env, post = with_env_and_mock(issues([{"identifier": "WB-1"}]))
    with env, post as mock:
        result = search_by_project("Stride", "epic")

    assert result == [{"identifier": "WB-1"}]
    assert sent_variables(mock) == {"project": "Stride", "text": "epic"}
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


def test_list_projects_requests_lead_summary_and_recency_fields():
    env, post = with_env_and_mock(projects_page([]))
    with env, post as mock:
        list_projects("lin_test")

    query = sent_query(mock)
    assert "description" in query
    assert "updatedAt" in query
    assert "lead { name }" in query


def test_list_projects_sorts_most_recently_updated_first():
    nodes = [
        {"name": "older", "updatedAt": "2026-01-01T00:00:00.000Z"},
        {"name": "newer", "updatedAt": "2026-05-01T00:00:00.000Z"},
    ]
    env, post = with_env_and_mock(projects_page(nodes))
    with env, post:
        result = list_projects("lin_test")

    assert [p["name"] for p in result] == ["newer", "older"]


def test_list_by_parent_filters_by_parent_id():
    env, post = with_env_and_mock(issues([]))
    with env, post as mock:
        list_by_parent("uuid-123")

    assert sent_variables(mock) == {"parent": "uuid-123"}
    assert "parent: { id: { eq: $parent } }" in sent_query(mock)
    assert "sortOrder" in sent_query(mock)


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


def test_min_backlog_sort_order_returns_minimum_not_first_node():
    nodes = [{"sortOrder": -204750}, {"sortOrder": -205050}, {"sortOrder": -204850}]
    data = {"project": {"issues": {"nodes": nodes}}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert min_backlog_sort_order("proj-1") == -205050


def test_min_backlog_sort_order_ignores_null_orders():
    nodes = [{"sortOrder": None}, {"sortOrder": -204950}]
    data = {"project": {"issues": {"nodes": nodes}}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert min_backlog_sort_order("proj-1") == -204950


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


def test_set_project_view_manual_sends_org_project_ordering():
    data = {"viewPreferencesCreate": {"success": True}}
    env, post = with_env_and_mock(data)
    with env, post as mock:
        result = set_project_view_manual("proj-1")

    assert result is True
    assert sent_variables(mock) == {
        "input": {
            "id": view_pref_id_for("proj-1"),
            "type": "organization",
            "viewType": "project",
            "projectId": "proj-1",
            "preferences": {"viewOrdering": "manual"},
        }
    }
    assert "viewPreferencesCreate" in sent_query(mock)


def test_view_pref_id_for_is_stable_per_project_and_v4_shaped():
    first = view_pref_id_for("proj-1")

    assert first == view_pref_id_for("proj-1")
    assert view_pref_id_for("proj-2") != first
    assert uuid.UUID(first).version == 4


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
        with patch("linear.load_statuses", return_value=statuses):
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
        with patch("linear.load_statuses", return_value=statuses):
            assert state_drift("WB") == []


def test_load_statuses_parses_the_repo_config():
    from linear import load_statuses as real_load

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
        {"name": "Doing", "type": "started", "position": 2.0},
        {"name": "In Review", "type": "started", "position": 1069.0},
    ]
    ids = {"Doing": "d", "In Review": "r"}
    with patch("linear.set_state_position") as set_pos:
        assert order_states(ONE_TYPE, board, ids) == []
    set_pos.assert_not_called()


def test_order_states_fixes_out_of_order_states():
    # In Review sits before Doing by position — must be reordered to JSON order.
    board = [
        {"name": "Doing", "type": "started", "position": 5.0},
        {"name": "In Review", "type": "started", "position": 2.0},
    ]
    ids = {"Doing": "d", "In Review": "r"}
    with patch("linear.set_state_position") as set_pos:
        result = order_states(ONE_TYPE, board, ids)

    assert result == ["Doing", "In Review"]
    assert set_pos.call_count == 2


# WB-534: Linear renders a board grouped by state type; position only orders
# states within a group, so cross-group position comparisons are meaningless.
CROSS_GROUP_BOARD = [
    {"name": "Backburner", "type": "backlog", "position": -974.71},
    {"name": "Backlog", "type": "backlog", "position": 0.0},
    {"name": "Todo", "type": "unstarted", "position": 1.0},
    {"name": "Doing", "type": "started", "position": 2.0},
    {"name": "In Review", "type": "started", "position": 1069.76},
    {"name": "Waiting", "type": "started", "position": 2120.79},
    {"name": "Done", "type": "completed", "position": 3.0},
    {"name": "Canceled", "type": "canceled", "position": 4.0},
    {"name": "Duplicate", "type": "duplicate", "position": 5.0},
]

CANONICAL_STATES = {
    "backlog": ["Backburner", "Backlog"],
    "unstarted": ["Todo"],
    "started": ["Doing", "In Review", "Waiting"],
    "completed": ["Done"],
    "canceled": ["Canceled"],
    "duplicate": ["Duplicate"],
}


def test_board_order_groups_by_type_before_position():
    assert board_order(CROSS_GROUP_BOARD) == [
        "Backburner",
        "Backlog",
        "Todo",
        "Doing",
        "In Review",
        "Waiting",
        "Done",
        "Canceled",
        "Duplicate",
    ]


def test_in_canonical_order_ignores_cross_group_positions():
    assert in_canonical_order(CANONICAL_STATES, CROSS_GROUP_BOARD) is True


def test_provision_states_creates_missing_and_reports_them():
    board = {"teams": {"nodes": [{"id": "t1", "issues": {"nodes": []}, "states": {"nodes": [
        {"id": "b", "name": "Backlog", "type": "backlog", "position": 0.0},
    ]}}]}}
    created_state = {"workflowStateCreate": {"workflowState": {"id": "new"}}}

    def fake_post(url: str, json: dict | None = None, headers: dict | None = None, **kwargs) -> MagicMock:
        query = json["query"]
        return ok_response(board if "teams(" in query else created_state)

    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear.requests.post", side_effect=fake_post):
            with patch("linear.load_statuses", return_value={"states": {"backlog": ["Backlog"], "started": ["Doing"]}}):
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
        with patch("linear.load_statuses", return_value={"states": {"backlog": ["Backlog"], "started": ["Doing"]}}):
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


# ---- WB-454: fat-CLI helpers (get_issue / whoami / teams / comments / resolvers) ----


def test_get_issue_returns_full_issue_object():
    data = {"issue": {"identifier": "WB-453", "title": "Vendor a client", "state": {"name": "Done"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = get_issue("lin_test", "WB-453")

    assert result == data["issue"]
    assert sent_variables(mock) == {"id": "WB-453"}


def test_get_project_returns_full_project_object():
    data = {"project": {"id": "p1", "name": "Stride", "description": "Apply guardrails"}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = get_project("lin_test", "p1")

    assert result == data["project"]
    assert sent_variables(mock) == {"id": "p1"}


def test_whoami_wraps_viewer_in_authenticated_envelope():
    data = {"viewer": {"id": "u1", "name": "Mike", "email": "mike@example.com"}}
    with patch("linear.requests.post", return_value=ok_response(data)):
        result = whoami("lin_test")

    assert result == {"authenticated": True, "user": data["viewer"]}


def test_list_teams_returns_team_nodes():
    data = {"teams": {"nodes": [{"id": "t1", "key": "WB", "name": "Webventurer"}]}}
    with patch("linear.requests.post", return_value=ok_response(data)):
        result = list_teams("lin_test")

    assert result == data["teams"]["nodes"]


def test_get_team_returns_first_match():
    data = {"teams": {"nodes": [{"id": "t1", "key": "WB", "name": "Webventurer"}]}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = get_team("lin_test", "WB")

    assert result["key"] == "WB"
    assert sent_variables(mock) == {"key": "WB"}


def test_get_team_returns_none_when_no_match():
    with patch("linear.requests.post", return_value=ok_response({"teams": {"nodes": []}})):
        assert get_team("lin_test", "NOPE") is None


def test_list_team_states_returns_states_for_team():
    data = {"teams": {"nodes": [{"states": {"nodes": [
        {"id": "s1", "name": "Backlog", "type": "backlog", "position": 0.0},
        {"id": "s2", "name": "Doing", "type": "started", "position": 1.0},
    ]}}]}}
    with patch("linear.requests.post", return_value=ok_response(data)):
        result = list_team_states("lin_test", "WB")

    assert [s["name"] for s in result] == ["Backlog", "Doing"]


def test_list_team_states_returns_empty_when_team_missing():
    with patch("linear.requests.post", return_value=ok_response({"teams": {"nodes": []}})):
        assert list_team_states("lin_test", "NOPE") == []


def test_list_comments_returns_comment_nodes():
    data = {"issue": {"comments": {"nodes": [
        {"id": "c1", "body": "Looks good", "user": {"name": "Mike"}},
    ]}}}
    with patch("linear.requests.post", return_value=ok_response(data)):
        result = list_comments("lin_test", "WB-453")

    assert result[0]["body"] == "Looks good"


def test_create_comment_sends_issue_uuid_and_body():
    data = {"commentCreate": {"comment": {"id": "c1", "body": "Hello"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = create_comment("lin_test", "issue-uuid-1", "Hello")

    assert result == {"id": "c1", "body": "Hello"}
    assert sent_variables(mock) == {"input": {"issueId": "issue-uuid-1", "body": "Hello"}}


# ---- WB-454: resolver helpers ----


def testlooks_like_uuid_recognises_standard_uuid_format():
    assert looks_like_uuid("21cec394-2ee6-4ed9-b2aa-4acfed3caf00")
    assert not looks_like_uuid("Stride >>>")
    assert not looks_like_uuid("")


def test_resolve_project_id_round_trips_uuids_without_a_query():
    with patch("linear.requests.post") as mock:
        result = resolve_project_id("lin_test", "21cec394-2ee6-4ed9-b2aa-4acfed3caf00")

    assert result == "21cec394-2ee6-4ed9-b2aa-4acfed3caf00"
    mock.assert_not_called()


def test_resolve_project_id_looks_up_names():
    data = {"projects": {"nodes": [{"id": "p1"}]}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = resolve_project_id("lin_test", "Stride >>>")

    assert result == "p1"
    assert sent_variables(mock) == {"name": "Stride >>>"}


def test_resolve_project_id_raises_when_name_unknown():
    with patch("linear.requests.post", return_value=ok_response({"projects": {"nodes": []}})):
        with pytest.raises(LinearError) as excinfo:
            resolve_project_id("lin_test", "Nonexistent")

    assert "Nonexistent" in str(excinfo.value)


def test_resolve_state_for_issue_returns_issue_uuid_and_state_id():
    data = {"issue": {
        "id": "issue-uuid",
        "team": {"states": {"nodes": [
            {"id": "s-backlog", "name": "Backlog"},
            {"id": "s-doing", "name": "Doing"},
        ]}},
    }}
    with patch("linear.requests.post", return_value=ok_response(data)):
        issue_uuid, state_id = resolve_state_for_issue("lin_test", "WB-453", "Doing")

    assert (issue_uuid, state_id) == ("issue-uuid", "s-doing")


def test_resolve_state_for_issue_raises_when_state_name_missing():
    data = {"issue": {"id": "issue-uuid", "team": {"states": {"nodes": [
        {"id": "s-backlog", "name": "Backlog"},
    ]}}}}
    with patch("linear.requests.post", return_value=ok_response(data)):
        with pytest.raises(LinearError) as excinfo:
            resolve_state_for_issue("lin_test", "WB-453", "In Progress")

    assert "In Progress" in str(excinfo.value)


def test_resolve_labels_for_team_translates_names_to_ids():
    labels = {"issueLabels": {"nodes": [
        {"id": "lbl-bug", "name": "bug", "team": {"id": "team-1"}},
        {"id": "lbl-feat", "name": "feature", "team": {"id": "team-1"}},
    ], "pageInfo": {"hasNextPage": False, "endCursor": None}}}
    with patch("linear.requests.post", return_value=ok_response(labels)):
        result = resolve_labels_for_team("lin_test", "team-1", ["bug", "feature"])

    assert result == ["lbl-bug", "lbl-feat"]


def test_resolve_labels_for_team_raises_for_missing_label():
    labels = {"issueLabels": {"nodes": [
        {"id": "lbl-bug", "name": "bug", "team": {"id": "team-1"}},
    ], "pageInfo": {"hasNextPage": False, "endCursor": None}}}
    with patch("linear.requests.post", return_value=ok_response(labels)):
        with pytest.raises(LinearError) as excinfo:
            resolve_labels_for_team("lin_test", "team-1", ["bug", "made-up"])

    assert "made-up" in str(excinfo.value)


# ---- WB-454: extended issue mutations (create returns full object, update with parent) ----


def test_create_issue_returns_full_issue_object():
    issue = {"id": "i1", "identifier": "WB-100", "title": "New", "state": {"name": "Backlog"}}
    data = {"issueCreate": {"issue": issue}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = create_issue("lin_test", team_id="t1", title="New")

    assert result == issue
    assert sent_variables(mock) == {"input": {"teamId": "t1", "title": "New", "description": ""}}


def test_create_issue_passes_optional_fields_when_provided():
    data = {"issueCreate": {"issue": {"id": "i1"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        create_issue(
            "lin_test", team_id="t1", title="New", project_id="p1",
            state_id="s1", description="desc", label_ids=["l1"],
            parent_id="parent-uuid", project_milestone_id="m1", priority=2,
        )

    input_data = sent_variables(mock)["input"]
    assert input_data == {
        "teamId": "t1", "title": "New", "description": "desc",
        "projectId": "p1", "stateId": "s1", "labelIds": ["l1"],
        "parentId": "parent-uuid", "projectMilestoneId": "m1", "priority": 2,
    }


def test_update_issue_accepts_parent_id():
    data = {"issueUpdate": {"issue": {"id": "i1", "parent": {"identifier": "WB-450"}}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = update_issue("lin_test", "i1", parent_id="parent-uuid")

    assert result["parent"]["identifier"] == "WB-450"
    assert sent_variables(mock)["input"] == {"parentId": "parent-uuid"}


def test_update_issue_omits_fields_not_passed():
    data = {"issueUpdate": {"issue": {"id": "i1"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        update_issue("lin_test", "i1", state_id="s-doing")

    assert sent_variables(mock)["input"] == {"stateId": "s-doing"}


# ---- WB-546: .stride.json config parser + bearer-token fallback ----


def test_project_config_reads_json_fields():
    data = {"project": "Test Project", "api_key_env": "LINEAR_TEST_API_KEY"}
    with patch("linear.STRIDE_CONFIG_PATH") as path:
        path.exists.return_value = True
        path.read_text.return_value = json.dumps(data)
        assert project_config() == data


def test_project_config_returns_empty_when_file_missing():
    with patch("linear.STRIDE_CONFIG_PATH") as stride_path, \
         patch("linear.LEGACY_CONFIG_PATH") as legacy_path:
        stride_path.exists.return_value = False
        legacy_path.exists.return_value = False
        assert project_config() == {}


def test_project_config_migrates_from_legacy_on_first_run():
    data = {"project": "Test Project", "api_key_env": "LINEAR_TEST_API_KEY"}
    legacy_text = "project = Test Project\napi_key_env = LINEAR_TEST_API_KEY\n"
    written = {}
    with patch("linear.STRIDE_CONFIG_PATH") as stride_path, \
         patch("linear.LEGACY_CONFIG_PATH") as legacy_path:
        stride_path.exists.return_value = False
        legacy_path.exists.return_value = True
        legacy_path.read_text.return_value = legacy_text
        stride_path.write_text.side_effect = lambda t: written.update({"text": t})
        assert project_config() == data
        assert legacy_path.unlink.called


def test_project_config_raises_on_invalid_json():
    with patch("linear.STRIDE_CONFIG_PATH") as path:
        path.exists.return_value = True
        path.read_text.return_value = "project = Stride\napi_key_env = LINEAR_KEY\n"
        with pytest.raises(Exception):
            project_config()


def test_token_from_project_config_reads_named_env_var():
    data = {"project": "Stride", "api_key_env": "LINEAR_TEST_API_KEY"}
    env = {"LINEAR_TEST_API_KEY": "lin_from_named"}
    with patch("linear.STRIDE_CONFIG_PATH") as path, patch.dict("os.environ", env, clear=True):
        path.exists.return_value = True
        path.read_text.return_value = json.dumps(data)
        assert token_from_project_config() == "lin_from_named"


def test_token_from_project_config_returns_none_when_api_key_env_absent():
    data = {"project": "Stride"}
    with patch("linear.STRIDE_CONFIG_PATH") as path, patch.dict("os.environ", {}, clear=True):
        path.exists.return_value = True
        path.read_text.return_value = json.dumps(data)
        assert token_from_project_config() is None


def test_token_from_project_config_returns_none_when_file_missing():
    with patch("linear.STRIDE_CONFIG_PATH") as path:
        path.exists.return_value = False
        assert token_from_project_config() is None


def test_bearer_token_falls_through_to_project_config_when_no_env():
    data = {"project": "Stride", "api_key_env": "LINEAR_TEST_API_KEY"}
    env = {"LINEAR_TEST_API_KEY": "lin_from_config"}
    with patch("linear.STRIDE_CONFIG_PATH") as path, patch.dict("os.environ", env, clear=True):
        path.exists.return_value = True
        path.read_text.return_value = json.dumps(data)
        assert bearer_token() == "lin_from_config"


def test_create_project_returns_id_and_sends_team_input():
    data = {"projectCreate": {"project": {"id": "p-new"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = create_project(
            "lin_test", "team-1", "Stride",
            description="tagline", content="# Vision",
        )

    assert result == "p-new"
    assert sent_variables(mock)["input"] == {
        "name": "Stride",
        "teamIds": ["team-1"],
        "description": "tagline",
        "content": "# Vision",
    }


# ---- read_text_arg: resolve inline / @file / - stdin body arguments ----

def test_read_text_arg_returns_none_unchanged():
    assert read_text_arg(None) is None


def test_read_text_arg_returns_empty_string_unchanged():
    assert read_text_arg("") == ""


def test_read_text_arg_returns_inline_text_unchanged():
    assert read_text_arg("just inline text") == "just inline text"


def test_read_text_arg_reads_file_contents_for_at_prefix(tmp_path: Path):
    body = tmp_path / "body.md"
    body.write_text("## Summary\nfrom a file")

    assert read_text_arg(f"@{body}") == "## Summary\nfrom a file"


def test_read_text_arg_preserves_shell_special_chars_from_file(tmp_path: Path):
    raw = "Body with `backticks`, $vars, an apostrophe's, and <angle> brackets"
    body = tmp_path / "tricky.md"
    body.write_text(raw)

    assert read_text_arg(f"@{body}") == raw


def test_read_text_arg_reads_stdin_for_dash(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("piped body text"))

    assert read_text_arg("-") == "piped body text"


def test_read_text_arg_raises_when_at_file_missing(tmp_path: Path):
    with pytest.raises(LinearError, match="Text-arg file not found"):
        read_text_arg(f"@{tmp_path / 'nope.md'}")


# ---- WB-538: long-text CLI options expand @path, never write it literally ----


def test_issue_update_expands_at_file_description(tmp_path: Path):
    body = tmp_path / "desc.md"
    body.write_text("### Real content\nfrom a file")

    with patch("linear_cli.bearer_token", return_value="lin_test"), patch(
        "linear_cli.get_issue", return_value={"id": "issue-uuid"}
    ), patch("linear_cli.update_issue", return_value={"id": "issue-uuid"}) as mock:
        result = CliRunner().invoke(
            linear_cli.cli,
            ["issue", "update", "WB-1", "--description", f"@{body}"],
        )

    assert result.exit_code == 0, result.output
    assert mock.call_args.kwargs["description"] == "### Real content\nfrom a file"


def test_project_create_expands_at_file_content(tmp_path: Path):
    vision = tmp_path / "VISION.md"
    vision.write_text("# Vision: stride")

    with patch("linear_cli.bearer_token", return_value="lin_test"), patch(
        "linear_cli.get_team", return_value={"id": "t1"}
    ), patch("linear_cli.create_project", return_value="p1") as mock, patch(
        "linear_cli.get_project", return_value={"id": "p1"}
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["project", "create", "-t", "WB", "--name", "X", "--content", f"@{vision}"],
        )

    assert result.exit_code == 0, result.output
    assert mock.call_args.kwargs["content"] == "# Vision: stride"
