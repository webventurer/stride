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

import linear  # noqa: E402
import linear_cli  # noqa: E402

REAL_WAITS_FOR_ANSWER = linear_cli.waits_for_answer


@pytest.fixture(autouse=True)
def no_card_waits_on_an_answer():
    with patch("linear_cli.waits_for_answer", return_value=False):
        yield


from linear import (  # noqa: E402
    LinearError,
    bearer_token,
    board_order,
    board_states,
    create_comment,
    create_issue,
    create_label,
    create_milestone,
    create_project,
    create_workflow_state,
    declared_states,
    get_issue,
    get_project,
    get_team,
    graphql,
    graphql_data,
    in_canonical_order,
    issues_query,
    label_drift,
    list_by_parent,
    list_by_project_state,
    list_by_project_state_type,
    list_comments,
    list_milestones,
    list_projects,
    list_team_states,
    list_teams,
    looks_like_uuid,
    milestone_open_issues,
    min_backlog_sort_order,
    operation_name,
    order_states,
    project_config,
    project_content,
    provision_labels,
    provision_states,
    raise_for_graphql_errors,
    raise_for_http,
    read_text_arg,
    resolve_project_id,
    resolve_state_for_issue,
    resolve_workspace_labels,
    search_by_project,
    set_project_view_manual,
    set_sort_order,
    state_drift,
    token_from_project_config,
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
        raise_for_graphql_errors(
            {"errors": [{"message": "bad filter"}]}, "query { x }"
        )

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
        with patch(
            "linear.requests.post",
            return_value=ok_response({"viewer": {"id": "u1"}}),
        ) as mock:
            result = graphql(
                "lin_test", "query { viewer { id } }", variables={"x": 1}
            )

    assert result == {"data": {"viewer": {"id": "u1"}}}
    args, kwargs = mock.call_args
    assert args[0] == "https://api.linear.app/graphql"
    assert kwargs["json"] == {
        "query": "query { viewer { id } }",
        "variables": {"x": 1},
    }
    assert kwargs["headers"]["Authorization"] == "lin_test"


def test_graphql_data_returns_data_payload_not_full_body():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch(
            "linear.requests.post",
            return_value=ok_response({"viewer": {"id": "u1"}}),
        ):
            assert graphql_data("query { viewer { id } }", {}) == {
                "viewer": {"id": "u1"}
            }


def test_graphql_data_raises_on_graphql_errors():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch(
            "linear.requests.post",
            return_value=graphql_errors_response([{"message": "bad filter"}]),
        ):
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

    return patch.dict(
        "os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False
    ), patch("linear.requests.post", return_value=make_response())


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
    data = {
        "project": {
            "projectMilestones": {"nodes": [{"id": "m1", "name": "Phase 1"}]}
        }
    }
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
    data = {
        "projectMilestoneCreate": {
            "projectMilestone": {"id": "m2", "name": "Q4"}
        }
    }
    env, post = with_env_and_mock(data)
    with env, post as mock:
        result = create_milestone("proj-1", "Q4", target_date="2026-12-31")

    assert result == {"id": "m2", "name": "Q4"}
    assert sent_variables(mock)["target"] == "2026-12-31"
    assert "targetDate: $target" in sent_query(mock)


def test_create_milestone_omits_target_date_when_absent():
    data = {
        "projectMilestoneCreate": {
            "projectMilestone": {"id": "m3", "name": "Q4"}
        }
    }
    env, post = with_env_and_mock(data)
    with env, post as mock:
        create_milestone("proj-1", "Q4")

    assert "target" not in sent_variables(mock)
    assert "targetDate" not in sent_query(mock)


def test_update_milestone_description_returns_success():
    data = {"projectMilestoneUpdate": {"success": True}}
    env, post = with_env_and_mock(data)
    with env, post:
        assert (
            update_milestone_description("m1", "Completed: 2026-05-24") is True
        )


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
    assert sent_variables(mock) == {
        "id": "proj-1",
        "content": "# Vision: stride",
    }


# ---- board order ----


def test_min_backlog_sort_order_returns_minimum_not_first_node():
    nodes = [
        {"sortOrder": -204750},
        {"sortOrder": -205050},
        {"sortOrder": -204850},
    ]
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


def relation_nodes(*relations: tuple[str, ...]) -> dict:
    nodes = [
        {
            "type": kind,
            "issue": {"identifier": ident, "state": {"type": state_type}},
        }
        for kind, ident, state_type, *_ in [
            (*r, "unstarted") for r in relations
        ]
    ]
    return {"nodes": nodes}


def test_issue_blockers_lists_only_blocking_relations():
    data = {
        "issue": {
            "inverseRelations": relation_nodes(
                ("blocks", "WB-1"), ("related", "WB-2"), ("blocks", "WB-3")
            )
        }
    }
    env, post = with_env_and_mock(data)
    with env, post:
        assert linear.get_issue_blockers("WB-9") == ["WB-1", "WB-3"]


def test_add_blocker_creates_a_blocks_relation_from_the_blocker():
    data = {"issueRelationCreate": {"success": True}}
    env, post = with_env_and_mock(data)
    with env, post as mock:
        assert linear.add_blocker("WB-9", "WB-1") is True

    assert sent_variables(mock) == {"blocker": "WB-1", "blocked": "WB-9"}
    assert "type: blocks" in sent_query(mock)


def test_todo_cards_carries_each_cards_blockers():
    node = {
        "id": "u1",
        "identifier": "WB-9",
        "title": "Nine",
        "priority": 2,
        "sortOrder": 5.0,
        "inverseRelations": relation_nodes(("blocks", "WB-1")),
    }
    env, post = with_env_and_mock({"issues": {"nodes": [node]}})
    with env, post as mock:
        cards = linear.list_todo_cards("Stride")

    assert cards[0]["blockers"] == ["WB-1"]
    assert 'name: { eq: "Todo" }' in sent_query(mock)


def test_todo_cards_carries_open_blockers_and_description():
    relations = relation_nodes(
        ("blocks", "WB-1", "completed"), ("blocks", "WB-2", "started")
    )
    node = {
        "id": "u1",
        "identifier": "WB-9",
        "title": "Nine",
        "description": "### What we'll do",
        "priority": 2,
        "sortOrder": 5.0,
        "inverseRelations": relations,
    }
    env, post = with_env_and_mock({"issues": {"nodes": [node]}})
    with env, post as mock:
        cards = linear.list_todo_cards("Stride")

    assert cards[0]["open_blockers"] == ["WB-2"]
    assert cards[0]["blockers"] == ["WB-1", "WB-2"]
    assert " description " in sent_query(mock)


def test_todo_cards_carries_each_cards_parent():
    node = {
        "id": "u1",
        "identifier": "WB-9",
        "title": "Nine",
        "priority": 2,
        "sortOrder": 5.0,
        "parent": {"identifier": "WB-935"},
        "inverseRelations": relation_nodes(),
    }
    env, post = with_env_and_mock({"issues": {"nodes": [node]}})
    with env, post as mock:
        cards = linear.list_todo_cards("Stride")

    assert cards[0]["parent"] == {"identifier": "WB-935"}
    assert "parent { identifier }" in sent_query(mock)


def test_write_todo_order_sets_manual_view_then_changed_orders():
    ordered = [
        {"id": "u1", "identifier": "A", "sortOrder": 10.0},
        {"id": "u2", "identifier": "B", "sortOrder": 30.0},
    ]
    with (
        patch("linear.resolve_project_id", return_value="p1"),
        patch("linear.bearer_token", return_value="lin_test"),
        patch("linear.set_project_view_manual") as manual,
        patch("linear.set_sort_order") as write,
    ):
        linear.write_todo_order("Stride", ordered, {"A": 10.0, "B": 20.0})

    manual.assert_called_once_with("p1")
    write.assert_called_once_with("u2", 20.0)


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
    data = teams(
        [{"states": {"nodes": [{"name": "Doing", "type": "started"}]}}]
    )
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
    config = {
        "states": {"started": ["Doing", "In Review"], "completed": ["Done"]}
    }

    assert declared_states(config) == {
        ("Doing", "started"),
        ("In Review", "started"),
        ("Done", "completed"),
    }


def test_state_drift_flags_declared_state_missing_from_board():
    statuses = {"states": {"started": ["Doing", "In Progress"]}}
    board = teams(
        [{"states": {"nodes": [{"name": "Doing", "type": "started"}]}}]
    )
    env, post = with_env_and_mock(board)
    with env, post:
        with patch("linear.load_statuses", return_value=statuses):
            assert state_drift("WB") == [
                {"name": "In Progress", "type": "started"}
            ]


def test_state_drift_empty_when_board_carries_every_declared_state():
    statuses = {"states": {"started": ["Doing"]}}
    board = teams(
        [
            {
                "states": {
                    "nodes": [
                        {"name": "Doing", "type": "started"},
                        {"name": "Done", "type": "completed"},
                    ]
                }
            }
        ]
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
    data = {
        "workflowStateCreate": {"workflowState": {"id": "s1", "name": "Doing"}}
    }
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
    board = {
        "teams": {
            "nodes": [
                {
                    "id": "t1",
                    "issues": {"nodes": []},
                    "states": {
                        "nodes": [
                            {
                                "id": "b",
                                "name": "Backlog",
                                "type": "backlog",
                                "position": 0.0,
                            },
                        ]
                    },
                }
            ]
        }
    }
    created_state = {"workflowStateCreate": {"workflowState": {"id": "new"}}}

    def fake_post(
        url: str,
        json: dict | None = None,
        headers: dict | None = None,
        **kwargs,
    ) -> MagicMock:
        query = json["query"]
        return ok_response(board if "teams(" in query else created_state)

    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear.requests.post", side_effect=fake_post):
            with patch(
                "linear.load_statuses",
                return_value={
                    "states": {"backlog": ["Backlog"], "started": ["Doing"]}
                },
            ):
                result = provision_states("WB")

    assert result["created"] == [{"name": "Doing", "type": "started"}]
    assert result["in_sync"] is False


def test_provision_states_in_sync_when_board_has_all_canonical():
    board = {
        "teams": {
            "nodes": [
                {
                    "id": "t1",
                    "issues": {"nodes": []},
                    "states": {
                        "nodes": [
                            {
                                "id": "b",
                                "name": "Backlog",
                                "type": "backlog",
                                "position": 0.0,
                            },
                            {
                                "id": "d",
                                "name": "Doing",
                                "type": "started",
                                "position": 1.0,
                            },
                        ]
                    },
                }
            ]
        }
    }
    env, post = with_env_and_mock(board)
    with env, post as mock:
        with patch(
            "linear.load_statuses",
            return_value={
                "states": {"backlog": ["Backlog"], "started": ["Doing"]}
            },
        ):
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


# ---- type-label provisioning (workspace-scoped) ----

THREE_LABELS = [
    {"name": "Bug", "color": "#eb5757"},
    {"name": "Epic", "color": "#5e6ad2"},
    {"name": "Story", "color": "#4cb782"},
]


def labels_page(nodes: list) -> dict:
    return {
        "issueLabels": {
            "nodes": nodes,
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        }
    }


def workspace_label(name: str) -> dict:
    return {"name": name, "team": None}


def test_create_label_omits_team_id_from_input():
    created = {
        "issueLabelCreate": {
            "issueLabel": {"id": "new", "name": "Bug", "color": "#eb5757"}
        }
    }
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch(
            "linear.requests.post", return_value=ok_response(created)
        ) as mock:
            create_label({"name": "Bug", "color": "#eb5757"})

    sent = sent_variables(mock)["input"]
    assert "teamId" not in sent
    assert sent == {"name": "Bug", "color": "#eb5757"}


def test_provision_labels_creates_all_three_at_workspace_scope():
    page = labels_page([])
    created = {"issueLabelCreate": {"issueLabel": {"id": "new"}}}

    def fake_post(
        url: str,
        json: dict | None = None,
        headers: dict | None = None,
        **kwargs,
    ) -> MagicMock:
        return ok_response(
            created if "issueLabelCreate" in json["query"] else page
        )

    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear.requests.post", side_effect=fake_post):
            with patch("linear.declared_labels", return_value=THREE_LABELS):
                result = provision_labels()

    assert len(result["created"]) == 3
    assert result["in_sync"] is False


def test_provision_labels_in_sync_when_labels_exist_at_workspace_scope():
    page = labels_page(
        [
            workspace_label("Bug"),
            workspace_label("Epic"),
            workspace_label("Story"),
        ]
    )
    env, post = with_env_and_mock(page)
    with env, post as mock:
        with patch("linear.declared_labels", return_value=THREE_LABELS):
            result = provision_labels()

    assert result == {"created": [], "in_sync": True}
    # only the read query ran — no create mutations
    assert mock.call_count == 1


def test_provision_labels_names_blocking_label_on_duplicate():
    page = labels_page([])

    def fake_post(
        url: str,
        json: dict | None = None,
        headers: dict | None = None,
        **kwargs,
    ) -> MagicMock:
        if "issueLabelCreate" in json["query"]:
            return graphql_errors_response(
                [{"message": "duplicate label name"}]
            )
        return ok_response(page)

    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch("linear.requests.post", side_effect=fake_post):
            with patch("linear.declared_labels", return_value=THREE_LABELS):
                with pytest.raises(LinearError) as excinfo:
                    provision_labels()

    message = str(excinfo.value)
    assert "team-scoped" in message
    assert ".md" not in message


def test_label_drift_empty_when_labels_exist_workspace_wide():
    page = labels_page(
        [
            workspace_label("Bug"),
            workspace_label("Epic"),
            workspace_label("Story"),
        ]
    )
    env, post = with_env_and_mock(page)
    with env, post:
        with patch("linear.declared_labels", return_value=THREE_LABELS):
            assert label_drift() == []


def test_label_drift_flags_declared_label_missing_from_workspace():
    page = labels_page([workspace_label("Bug")])
    env, post = with_env_and_mock(page)
    with env, post:
        with patch("linear.declared_labels", return_value=THREE_LABELS):
            assert label_drift() == [
                {"name": "Epic", "color": "#5e6ad2"},
                {"name": "Story", "color": "#4cb782"},
            ]


def test_label_drift_ignores_a_same_name_team_scoped_label():
    page = labels_page([{"name": "Bug", "team": {"id": "team-1"}}])
    env, post = with_env_and_mock(page)
    with env, post:
        with patch("linear.declared_labels", return_value=THREE_LABELS):
            assert label_drift() == THREE_LABELS


def test_provision_labels_surfaces_api_errors():
    with patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}, clear=False):
        with patch(
            "linear.requests.post",
            return_value=graphql_errors_response(
                [{"message": "api unavailable"}]
            ),
        ):
            with patch("linear.declared_labels", return_value=THREE_LABELS):
                with pytest.raises(LinearError) as excinfo:
                    provision_labels()

    assert "api unavailable" in str(excinfo.value)


# ---- WB-454: fat-CLI helpers (get_issue / whoami / teams / comments / resolvers) ----


def test_get_issue_returns_full_issue_object():
    data = {
        "issue": {
            "identifier": "WB-453",
            "title": "Vendor a client",
            "state": {"name": "Done"},
        }
    }
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = get_issue("lin_test", "WB-453")

    assert result == data["issue"]
    assert sent_variables(mock) == {"id": "WB-453"}


def test_get_project_returns_full_project_object():
    data = {
        "project": {
            "id": "p1",
            "name": "Stride",
            "description": "Apply guardrails",
        }
    }
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
    data = {
        "teams": {"nodes": [{"id": "t1", "key": "WB", "name": "Webventurer"}]}
    }
    with patch("linear.requests.post", return_value=ok_response(data)):
        result = list_teams("lin_test")

    assert result == data["teams"]["nodes"]


def test_get_team_returns_first_match():
    data = {
        "teams": {"nodes": [{"id": "t1", "key": "WB", "name": "Webventurer"}]}
    }
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = get_team("lin_test", "WB")

    assert result["key"] == "WB"
    assert sent_variables(mock) == {"key": "WB"}


def test_get_team_returns_none_when_no_match():
    with patch(
        "linear.requests.post",
        return_value=ok_response({"teams": {"nodes": []}}),
    ):
        assert get_team("lin_test", "NOPE") is None


def test_list_team_states_returns_states_for_team():
    data = {
        "teams": {
            "nodes": [
                {
                    "states": {
                        "nodes": [
                            {
                                "id": "s1",
                                "name": "Backlog",
                                "type": "backlog",
                                "position": 0.0,
                            },
                            {
                                "id": "s2",
                                "name": "Doing",
                                "type": "started",
                                "position": 1.0,
                            },
                        ]
                    }
                }
            ]
        }
    }
    with patch("linear.requests.post", return_value=ok_response(data)):
        result = list_team_states("lin_test", "WB")

    assert [s["name"] for s in result] == ["Backlog", "Doing"]


def test_list_team_states_returns_empty_when_team_missing():
    with patch(
        "linear.requests.post",
        return_value=ok_response({"teams": {"nodes": []}}),
    ):
        assert list_team_states("lin_test", "NOPE") == []


def test_list_comments_returns_comment_nodes():
    data = {
        "issue": {
            "comments": {
                "nodes": [
                    {
                        "id": "c1",
                        "body": "Looks good",
                        "user": {"name": "Mike"},
                    },
                ]
            }
        }
    }
    with patch("linear.requests.post", return_value=ok_response(data)):
        result = list_comments("lin_test", "WB-453")

    assert result[0]["body"] == "Looks good"


def test_create_comment_sends_issue_uuid_and_body():
    data = {"commentCreate": {"comment": {"id": "c1", "body": "Hello"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = create_comment("lin_test", "issue-uuid-1", "Hello")

    assert result == {"id": "c1", "body": "Hello"}
    assert sent_variables(mock) == {
        "input": {"issueId": "issue-uuid-1", "body": "Hello"}
    }


# ---- WB-454: resolver helpers ----


def testlooks_like_uuid_recognises_standard_uuid_format():
    assert looks_like_uuid("21cec394-2ee6-4ed9-b2aa-4acfed3caf00")
    assert not looks_like_uuid("Stride >>>")
    assert not looks_like_uuid("")


def test_resolve_project_id_round_trips_uuids_without_a_query():
    with patch("linear.requests.post") as mock:
        result = resolve_project_id(
            "lin_test", "21cec394-2ee6-4ed9-b2aa-4acfed3caf00"
        )

    assert result == "21cec394-2ee6-4ed9-b2aa-4acfed3caf00"
    mock.assert_not_called()


def test_resolve_project_id_looks_up_names():
    data = {"projects": {"nodes": [{"id": "p1"}]}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = resolve_project_id("lin_test", "Stride >>>")

    assert result == "p1"
    assert sent_variables(mock) == {"name": "Stride >>>"}


def test_resolve_project_id_raises_when_name_unknown():
    with patch(
        "linear.requests.post",
        return_value=ok_response({"projects": {"nodes": []}}),
    ):
        with pytest.raises(LinearError) as excinfo:
            resolve_project_id("lin_test", "Nonexistent")

    assert "Nonexistent" in str(excinfo.value)


def test_resolve_state_for_issue_returns_issue_uuid_and_state_id():
    data = {
        "issue": {
            "id": "issue-uuid",
            "team": {
                "states": {
                    "nodes": [
                        {"id": "s-backlog", "name": "Backlog"},
                        {"id": "s-doing", "name": "Doing"},
                    ]
                }
            },
        }
    }
    with patch("linear.requests.post", return_value=ok_response(data)):
        issue_uuid, state_id = resolve_state_for_issue(
            "lin_test", "WB-453", "Doing"
        )

    assert (issue_uuid, state_id) == ("issue-uuid", "s-doing")


def test_resolve_state_for_issue_raises_when_state_name_missing():
    data = {
        "issue": {
            "id": "issue-uuid",
            "team": {
                "states": {
                    "nodes": [
                        {"id": "s-backlog", "name": "Backlog"},
                    ]
                }
            },
        }
    }
    with patch("linear.requests.post", return_value=ok_response(data)):
        with pytest.raises(LinearError) as excinfo:
            resolve_state_for_issue("lin_test", "WB-453", "In Progress")

    assert "In Progress" in str(excinfo.value)


def test_resolve_workspace_labels_translates_names_to_ids():
    labels = {
        "issueLabels": {
            "nodes": [
                {"id": "lbl-bug", "name": "bug", "team": None},
                {"id": "lbl-feat", "name": "feature", "team": None},
            ],
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        }
    }
    with patch("linear.requests.post", return_value=ok_response(labels)):
        result = resolve_workspace_labels("lin_test", ["bug", "feature"])

    assert result == ["lbl-bug", "lbl-feat"]


def test_resolve_workspace_labels_raises_for_missing_label():
    labels = {
        "issueLabels": {
            "nodes": [
                {"id": "lbl-bug", "name": "bug", "team": None},
            ],
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        }
    }
    with patch("linear.requests.post", return_value=ok_response(labels)):
        with pytest.raises(LinearError) as excinfo:
            resolve_workspace_labels("lin_test", ["bug", "made-up"])

    assert "made-up" in str(excinfo.value)


def test_resolve_workspace_labels_ignores_team_scoped_label():
    labels = {
        "issueLabels": {
            "nodes": [
                {"id": "lbl-bug", "name": "Bug", "team": None},
                {"id": "lbl-story", "name": "Story", "team": {"id": "team-1"}},
            ],
            "pageInfo": {"hasNextPage": False, "endCursor": None},
        }
    }
    with patch("linear.requests.post", return_value=ok_response(labels)):
        with pytest.raises(LinearError) as excinfo:
            resolve_workspace_labels("lin_test", ["Story"])

    assert "Story" in str(excinfo.value)


# ---- WB-454: extended issue mutations (create returns full object, update with parent) ----


def test_create_issue_returns_full_issue_object():
    issue = {
        "id": "i1",
        "identifier": "WB-100",
        "title": "New",
        "state": {"name": "Backlog"},
    }
    data = {"issueCreate": {"issue": issue}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = create_issue("lin_test", team_id="t1", title="New")

    assert result == issue
    assert sent_variables(mock) == {
        "input": {"teamId": "t1", "title": "New", "description": ""}
    }


def test_create_issue_passes_optional_fields_when_provided():
    data = {"issueCreate": {"issue": {"id": "i1"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        create_issue(
            "lin_test",
            team_id="t1",
            title="New",
            project_id="p1",
            state_id="s1",
            description="desc",
            label_ids=["l1"],
            parent_id="parent-uuid",
            project_milestone_id="m1",
            priority=2,
        )

    input_data = sent_variables(mock)["input"]
    assert input_data == {
        "teamId": "t1",
        "title": "New",
        "description": "desc",
        "projectId": "p1",
        "stateId": "s1",
        "labelIds": ["l1"],
        "parentId": "parent-uuid",
        "projectMilestoneId": "m1",
        "priority": 2,
    }


def test_update_issue_accepts_parent_id():
    data = {
        "issueUpdate": {
            "issue": {"id": "i1", "parent": {"identifier": "WB-450"}}
        }
    }
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = update_issue("lin_test", "i1", parent_id="parent-uuid")

    assert result["parent"]["identifier"] == "WB-450"
    assert sent_variables(mock)["input"] == {"parentId": "parent-uuid"}


def test_update_issue_omits_fields_not_passed():
    data = {"issueUpdate": {"issue": {"id": "i1"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        update_issue("lin_test", "i1", state_id="s-doing")

    assert sent_variables(mock)["input"] == {"stateId": "s-doing"}


# ---- WB-977: clear a parent, remove a blocked-by link ----


def test_update_issue_clears_the_parent_with_a_null_parent_id():
    data = {"issueUpdate": {"issue": {"id": "i1", "parent": None}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        update_issue("lin_test", "i1", clear_parent=True)

    assert sent_variables(mock)["input"] == {"parentId": None}


def blocker_relations(*relations: tuple[str, str, str]) -> MagicMock:
    nodes = [
        {"id": rid, "type": kind, "issue": {"identifier": ident}}
        for rid, kind, ident in relations
    ]
    return ok_response({"issue": {"inverseRelations": {"nodes": nodes}}})


def relation_deleted() -> MagicMock:
    return ok_response({"issueRelationDelete": {"success": True}})


def test_remove_blocker_deletes_only_the_relation_from_that_blocker():
    lookup = blocker_relations(
        ("r1", "blocks", "WB-1"), ("r2", "blocks", "WB-3")
    )
    with (
        patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}),
        patch(
            "linear.requests.post", side_effect=[lookup, relation_deleted()]
        ) as mock,
    ):
        assert linear.remove_blocker("WB-2", "WB-1") is True

    assert mock.call_count == 2
    assert sent_variables(mock) == {"id": "r1"}
    assert "issueRelationDelete" in sent_query(mock)


@pytest.mark.parametrize(
    "relations",
    [
        [],
        [("r1", "related", "WB-1")],
        [("r1", "blocks", "WB-3")],
    ],
    ids=["no link", "only related", "other blocker only"],
)
def test_remove_blocker_changes_nothing_when_the_card_is_not_a_blocker(
    relations,
):
    with (
        patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}),
        patch(
            "linear.requests.post", return_value=blocker_relations(*relations)
        ) as mock,
    ):
        assert linear.remove_blocker("WB-2", "WB-1") is False

    assert mock.call_count == 1


def test_remove_blocker_ignores_a_block_that_runs_the_other_way():
    # WB-2 blocks WB-1: the link sits on WB-2's outgoing relations, so
    # unblocking WB-2 from WB-1 must find nothing in its inverse relations.
    outgoing = {"nodes": [{"id": "r1", "type": "blocks"}]}
    lookup = ok_response(
        {"issue": {"relations": outgoing, "inverseRelations": {"nodes": []}}}
    )
    with (
        patch.dict("os.environ", {"LINEAR_API_KEY": "lin_test"}),
        patch("linear.requests.post", return_value=lookup) as mock,
    ):
        assert linear.remove_blocker("WB-2", "WB-1") is False

    assert mock.call_count == 1
    assert "inverseRelations" in sent_query(mock)


def test_issue_unblock_says_so_when_the_card_does_not_block():
    with (
        patch("linear_cli.remove_blocker", return_value=False),
    ):
        result = CliRunner().invoke(
            linear_cli.cli, ["issue", "unblock", "WB-2", "--by", "WB-1"]
        )

    assert result.exit_code != 0
    assert "WB-1 does not block WB-2" in result.output


def test_issue_update_no_parent_clears_the_parent():
    with (
        patch("linear_cli.bearer_token", return_value="lin_test"),
        patch("linear_cli.get_issue", return_value={"id": "issue-uuid"}),
        patch(
            "linear_cli.update_issue", return_value={"id": "issue-uuid"}
        ) as mock,
    ):
        result = CliRunner().invoke(
            linear_cli.cli, ["issue", "update", "WB-1", "--no-parent"]
        )

    assert result.exit_code == 0, result.output
    assert mock.call_args.kwargs["clear_parent"] is True


def test_issue_update_refuses_parent_together_with_no_parent():
    with (
        patch("linear_cli.bearer_token", return_value="lin_test"),
        patch("linear_cli.get_issue", return_value={"id": "issue-uuid"}),
        patch("linear_cli.update_issue") as mock,
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["issue", "update", "WB-1", "--parent", "WB-2", "--no-parent"],
        )

    assert result.exit_code != 0
    assert "--parent and --no-parent" in result.output
    mock.assert_not_called()


# ---- WB-546: .stride.json config parser + bearer-token fallback ----


def test_project_config_reads_json_fields():
    data = {"project": "Test Project", "api_key_env": "LINEAR_TEST_API_KEY"}
    with patch("linear.STRIDE_CONFIG_PATH") as path:
        path.exists.return_value = True
        path.read_text.return_value = json.dumps(data)
        assert project_config() == data


def test_project_config_returns_empty_when_file_missing():
    with patch("linear.STRIDE_CONFIG_PATH") as stride_path:
        stride_path.exists.return_value = False
        assert project_config() == {}


def test_project_config_does_not_migrate_legacy_when_file_missing():
    with (
        patch("linear.STRIDE_CONFIG_PATH") as stride_path,
        patch("legacy.LEGACY_CONFIG_PATH") as legacy_path,
    ):
        stride_path.exists.return_value = False
        legacy_path.exists.return_value = True
        assert project_config() == {}
        assert not legacy_path.unlink.called


# ---- WB-937: parallel-sessions sets how many cards run at once ----


def test_parallel_session_limit_returns_configured_number():
    with patch("linear.project_config", return_value={"parallel-sessions": 5}):
        assert linear.parallel_session_limit() == 5


def test_parallel_session_limit_defaults_to_three_when_missing():
    with patch("linear.project_config", return_value={"project": "Foo"}):
        assert linear.parallel_session_limit() == 3


@pytest.mark.parametrize("value", [0, -2, "three", 2.5, True, None])
def test_parallel_session_limit_refuses_invalid_value(value: object):
    with (
        patch(
            "linear.project_config", return_value={"parallel-sessions": value}
        ),
        pytest.raises(LinearError, match="parallel-sessions"),
    ):
        linear.parallel_session_limit()


# ---- WB-541: config paths resolve from repo root, not the CWD ----


def test_config_paths_anchored_to_repo_root():
    repo_root = Path(linear.__file__).resolve().parent.parent.parent
    assert linear.STRIDE_CONFIG_PATH == repo_root / ".stride.json"
    assert linear.STRIDE_CONFIG_PATH.is_absolute()


def test_project_config_raises_on_invalid_json():
    with patch("linear.STRIDE_CONFIG_PATH") as path:
        path.exists.return_value = True
        path.read_text.return_value = (
            "project = Stride\napi_key_env = LINEAR_KEY\n"
        )
        with pytest.raises(LinearError, match="invalid JSON"):
            project_config()


def test_token_from_project_config_reads_named_env_var():
    data = {"project": "Stride", "api_key_env": "LINEAR_TEST_API_KEY"}
    env = {"LINEAR_TEST_API_KEY": "lin_from_named"}
    with (
        patch("linear.STRIDE_CONFIG_PATH") as path,
        patch.dict("os.environ", env, clear=True),
    ):
        path.exists.return_value = True
        path.read_text.return_value = json.dumps(data)
        assert token_from_project_config() == "lin_from_named"


def test_token_from_project_config_returns_none_when_api_key_env_absent():
    data = {"project": "Stride"}
    with (
        patch("linear.STRIDE_CONFIG_PATH") as path,
        patch.dict("os.environ", {}, clear=True),
    ):
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
    with (
        patch("linear.STRIDE_CONFIG_PATH") as path,
        patch.dict("os.environ", env, clear=True),
    ):
        path.exists.return_value = True
        path.read_text.return_value = json.dumps(data)
        assert bearer_token() == "lin_from_config"


def test_create_project_returns_id_and_sends_team_input():
    data = {"projectCreate": {"project": {"id": "p-new"}}}
    with patch("linear.requests.post", return_value=ok_response(data)) as mock:
        result = create_project(
            "lin_test",
            "team-1",
            "Stride",
            description="tagline",
            content="# Vision",
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

    with (
        patch("linear_cli.bearer_token", return_value="lin_test"),
        patch("linear_cli.get_issue", return_value={"id": "issue-uuid"}),
        patch(
            "linear_cli.update_issue", return_value={"id": "issue-uuid"}
        ) as mock,
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["issue", "update", "WB-1", "--description", f"@{body}"],
        )

    assert result.exit_code == 0, result.output
    assert (
        mock.call_args.kwargs["description"] == "### Real content\nfrom a file"
    )


def test_project_create_expands_at_file_content(tmp_path: Path):
    vision = tmp_path / "VISION.md"
    vision.write_text("# Vision: stride")

    with (
        patch("linear_cli.bearer_token", return_value="lin_test"),
        patch("linear_cli.get_team", return_value={"id": "t1"}),
        patch("linear_cli.create_project", return_value="p1") as mock,
        patch("linear_cli.get_project", return_value={"id": "p1"}),
        patch("linear_cli.set_project_view_manual", return_value=True),
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            [
                "project",
                "create",
                "-t",
                "WB",
                "--name",
                "X",
                "--content",
                f"@{vision}",
            ],
        )

    assert result.exit_code == 0, result.output
    assert mock.call_args.kwargs["content"] == "# Vision: stride"


def test_project_create_starts_board_on_manual_ordering():
    with (
        patch("linear_cli.bearer_token", return_value="lin_test"),
        patch("linear_cli.get_team", return_value={"id": "t1"}),
        patch("linear_cli.create_project", return_value="p1"),
        patch("linear_cli.get_project", return_value={"id": "p1"}),
        patch("linear_cli.set_project_view_manual", return_value=True) as mock,
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["project", "create", "-t", "WB", "--name", "X"],
        )

    assert result.exit_code == 0, result.output
    mock.assert_called_once_with("p1")


def test_migrate_legacy_config_emits_migrated_config_as_json():
    config = {
        "project": "AI Thought Partner",
        "api_key_env": "LINEAR_PERSONAL_API_KEY",
    }
    with patch("linear_cli.migrate_from_legacy", return_value=config):
        result = CliRunner().invoke(linear_cli.cli, ["migrate-legacy-config"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == config


# ---- WB-939: next-steps picks the cards that can run at once ----


def todo_card(identifier: str, open_blockers: list[str]) -> dict:
    return {
        "identifier": identifier,
        "title": f"Card {identifier}",
        "description": "",
        "priority": 0,
        "sortOrder": 1.0,
        "blockers": open_blockers,
        "open_blockers": open_blockers,
    }


def test_next_batch_prints_each_considered_card_in_or_out():
    cards = [todo_card("A", []), todo_card("B", ["WB-1"])]
    with (
        patch("linear.project_config", return_value={"parallel-sessions": 2}),
        patch("linear_cli.list_todo_cards", return_value=cards),
    ):
        result = CliRunner().invoke(
            linear_cli.cli, ["next-batch", "--project", "Stride"]
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == [
        {
            "identifier": "A",
            "title": "Card A",
            "in_batch": True,
            "reason": None,
        },
        {
            "identifier": "B",
            "title": "Card B",
            "in_batch": False,
            "reason": "blocked by WB-1",
        },
    ]


def test_next_batch_shows_the_settings_message_for_a_refused_value():
    with patch("linear.project_config", return_value={"parallel-sessions": 0}):
        result = CliRunner().invoke(
            linear_cli.cli, ["next-batch", "--project", "Stride"]
        )

    assert result.exit_code != 0
    assert '"parallel-sessions" must be a whole number' in result.output


def test_next_batch_takes_a_card_whose_only_blocker_is_done():
    nodes = [
        {
            "id": "u0",
            "identifier": "WB-1",
            "title": "Epic: Something",
            "description": "",
            "priority": 0,
            "sortOrder": 0.0,
            "inverseRelations": relation_nodes(),
        },
        {
            "id": "u2",
            "identifier": "WB-2",
            "title": "Two",
            "description": "",
            "priority": 0,
            "sortOrder": 1.0,
            "inverseRelations": relation_nodes(("blocks", "WB-9", "completed")),
        },
    ]
    env, post = with_env_and_mock({"issues": {"nodes": nodes}})
    with (
        env,
        post,
        patch("linear.project_config", return_value={"parallel-sessions": 3}),
    ):
        result = CliRunner().invoke(
            linear_cli.cli, ["next-batch", "--project", "Stride"]
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == [
        {"identifier": "WB-2", "title": "Two", "in_batch": True, "reason": None}
    ]


# ---- WB-940: a card's start check sees what changed since it was written ----


def card_history(*changes: tuple[str, bool]) -> dict:
    nodes = [
        {"createdAt": at, "updatedDescription": described}
        for at, described in changes
    ]
    return {
        "issue": {
            "createdAt": "2026-11-01T09:00:00.000Z",
            "history": {"nodes": nodes},
        }
    }


def test_get_description_changed_at_is_the_last_description_change():
    data = card_history(
        ("2026-11-02T10:00:00.000Z", True),
        ("2026-11-04T10:00:00.000Z", True),
        ("2026-11-05T10:00:00.000Z", False),
    )
    env, post = with_env_and_mock(data)
    with env, post:
        changed = linear.get_description_changed_at("WB-9")

    assert changed == "2026-11-04T10:00:00.000Z"


def test_get_description_changed_at_is_creation_when_never_edited():
    data = card_history(("2026-11-05T10:00:00.000Z", False))
    env, post = with_env_and_mock(data)
    with env, post:
        assert (
            linear.get_description_changed_at("WB-9")
            == "2026-11-01T09:00:00.000Z"
        )


def test_issue_description_changed_at_prints_the_time():
    with patch(
        "linear_cli.get_description_changed_at",
        return_value="2026-11-04T10:00:00.000Z",
    ):
        result = CliRunner().invoke(
            linear_cli.cli, ["issue", "description-changed-at", "WB-9"]
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == "2026-11-04T10:00:00.000Z"


# ---- WB-942: /linear:start with no card runs the next batch from Todo ----


def test_start_choice_on_main_runs_the_cards_next_batch_picks():
    cards = [todo_card("A", []), todo_card("B", []), todo_card("C", ["WB-1"])]
    with (
        patch("linear.project_config", return_value={"parallel-sessions": 3}),
        patch("linear_cli.list_todo_cards", return_value=cards),
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["start-choice", "--project", "Stride", "--branch", "main"],
        )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"action": "batch", "cards": ["A", "B"]}


def test_start_choice_on_a_card_branch_reads_no_todo():
    with (
        patch("linear_cli.list_todo_cards") as todo,
        patch("linear_cli.get_issue", return_value={"identifier": "WB-7"}),
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["start-choice", "--project", "Stride", "--branch", "me/wb-7-x"],
        )

    assert json.loads(result.output) == {"action": "resume", "card": "WB-7"}
    todo.assert_not_called()


def test_start_choice_asks_when_the_branch_card_is_not_in_linear():
    with patch("linear_cli.get_issue", side_effect=LinearError("not found")):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["start-choice", "--project", "Stride", "--branch", "me/utf-8-fix"],
        )

    assert json.loads(result.output) == {"action": "ask"}


def test_start_choice_resumes_the_first_branch_card_linear_knows():
    def issue(_token: str, identifier: str) -> dict:
        if identifier == "UTF-8":
            raise LinearError("not found")
        return {"identifier": identifier}

    with patch("linear_cli.get_issue", side_effect=issue):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["start-choice", "--project", "S", "--branch", "me/utf-8-wb-945"],
        )

    assert json.loads(result.output) == {"action": "resume", "card": "WB-945"}


# ---- WB-973: /linear:start on an epic batches only that epic's cards ----


def sub_issue(identifier: str, epic: str, open_blockers: list | None = None):
    return todo_card(identifier, open_blockers or []) | {
        "parent": {"identifier": epic}
    }


def start_choice_for_epic(
    cards: list[dict], size: int = 3, started: tuple[str, ...] = ()
) -> dict:
    started_args = [arg for card in started for arg in ("--started", card)]
    with (
        patch(
            "linear.project_config", return_value={"parallel-sessions": size}
        ),
        patch("linear_cli.list_todo_cards", return_value=cards),
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            [
                "start-choice",
                "--project",
                "Stride",
                "--branch",
                "main",
                "--epic",
                "wb-1",
                *started_args,
            ],
        )

    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_start_choice_for_an_epic_batches_only_its_cards_up_to_the_limit():
    cards = [
        sub_issue("X1", "WB-2"),
        sub_issue("A", "WB-1"),
        sub_issue("B", "WB-1"),
        sub_issue("C", "WB-1"),
    ]

    assert start_choice_for_epic(cards, size=2) == {
        "action": "batch",
        "cards": ["A", "B"],
    }


def test_start_choice_for_an_epic_runs_its_one_able_card_alone():
    cards = [
        sub_issue("X1", "WB-2"),
        sub_issue("A", "WB-1"),
        sub_issue("B", "WB-1", ["WB-9"]),
    ]

    assert start_choice_for_epic(cards) == {"action": "single", "card": "A"}


def test_start_choice_for_an_epic_lists_each_reason_when_all_are_blocked():
    cards = [
        sub_issue("A", "WB-1", ["WB-8"]),
        sub_issue("B", "WB-1", ["WB-9"]),
    ]

    assert start_choice_for_epic(cards) == {
        "action": "blocked",
        "reasons": {"A": "blocked by WB-8", "B": "blocked by WB-9"},
    }


def test_start_choice_for_an_epic_with_nothing_in_todo_is_empty():
    cards = [sub_issue("X1", "WB-2")]

    assert start_choice_for_epic(cards) == {"action": "empty"}


# ---- WB-979: a named epic's run asks again after each batch ----


def test_start_choice_for_an_epic_names_the_next_batch_past_started_cards():
    cards = [
        sub_issue("X1", "WB-2"),
        sub_issue("A", "WB-1"),
        sub_issue("B", "WB-1"),
        sub_issue("C", "WB-1"),
        sub_issue("D", "WB-1"),
    ]

    assert start_choice_for_epic(cards, size=2, started=("A", "B")) == {
        "action": "batch",
        "cards": ["C", "D"],
    }


def test_start_choice_for_an_epic_never_names_a_card_of_another_epic():
    cards = [
        sub_issue("X1", "WB-2"),
        sub_issue("A", "WB-1"),
        sub_issue("B", "WB-1"),
    ]

    assert start_choice_for_epic(cards, started=("A", "B")) == {
        "action": "blocked",
        "reasons": {
            "A": "started earlier in this run and stopped in Todo",
            "B": "started earlier in this run and stopped in Todo",
        },
    }


def test_start_choice_for_an_epic_is_empty_once_its_cards_have_left_todo():
    cards = [sub_issue("X1", "WB-2")]

    assert start_choice_for_epic(cards, started=("A", "B")) == {
        "action": "empty"
    }


def test_start_choice_for_an_epic_runs_a_card_freed_by_a_merged_blocker_alone():
    cards = [sub_issue("B", "WB-1"), sub_issue("X1", "WB-2")]

    assert start_choice_for_epic(cards, started=("A",)) == {
        "action": "single",
        "card": "B",
    }


def test_next_batch_for_an_epic_shows_only_its_cards():
    cards = [sub_issue("X1", "WB-2"), sub_issue("A", "WB-1")]
    with (
        patch("linear.project_config", return_value={"parallel-sessions": 3}),
        patch("linear_cli.list_todo_cards", return_value=cards),
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["next-batch", "--project", "Stride", "--epic", "WB-1"],
        )

    assert [c["identifier"] for c in json.loads(result.output)] == ["A"]


# ---- WB-943: /linear:start works through Todo until it's empty ----


def comment(body: str, created_at: str) -> dict:
    return {"body": body, "createdAt": created_at}


def test_waits_on_answer_while_a_lesson_question_has_no_answer():
    comments = [
        comment("**Lesson question from WB-5**\n\nShould this change?", "T1"),
        comment("Lesson from WB-6: reworded a line.", "T2"),
    ]

    assert linear.waits_on_answer(comments) is True


def test_waits_on_answer_ends_when_a_later_comment_starts_with_answer():
    comments = [
        comment("**Lesson question from WB-5**\n\nShould this change?", "T1"),
        comment("Answer: yes, change it.", "T2"),
    ]

    assert linear.waits_on_answer(comments) is False


def test_waits_on_answer_ignores_an_answer_posted_before_the_question():
    comments = [
        comment("Answer: yes.", "T1"),
        comment("**Lesson question from WB-5**\n\nShould this change?", "T2"),
    ]

    assert linear.waits_on_answer(comments) is True


def test_waits_on_answer_is_false_for_a_card_with_no_question():
    assert linear.waits_on_answer([comment("Just a note", "T1")]) is False
    assert linear.waits_on_answer([]) is False


def blocked_by(state_type: str) -> dict:
    relation = {
        "type": "blocks",
        "issue": {"identifier": "WB-9", "state": {"type": state_type}},
    }
    return {"inverseRelations": {"nodes": [relation]}}


@pytest.mark.parametrize("state_type", ["backlog", "canceled", "started"])
def test_a_blocker_that_is_not_done_stays_open(state_type):
    node = blocked_by(state_type)

    assert linear.open_blocker_identifiers(node) == ["WB-9"]


def test_a_blocker_that_is_done_is_not_open():
    assert linear.open_blocker_identifiers(blocked_by("completed")) == []


def run_next_batch(cards: list[dict], waiting: set[str]) -> list:
    with (
        patch("linear.project_config", return_value={"parallel-sessions": 3}),
        patch("linear_cli.list_todo_cards", return_value=cards),
        patch(
            "linear_cli.waits_for_answer",
            side_effect=lambda card: card["identifier"] in waiting,
        ),
    ):
        result = CliRunner().invoke(
            linear_cli.cli, ["next-batch", "--project", "Stride"]
        )

    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_next_batch_leaves_out_a_card_waiting_on_an_answer():
    cards = [todo_card("A", []), todo_card("B", [])]

    lines = run_next_batch(cards, {"A"})

    assert [(c["identifier"], c["in_batch"]) for c in lines] == [
        ("A", False),
        ("B", True),
    ]
    assert lines[0]["reason"] == "waits for an answer to a lesson question"


def test_start_choice_leaves_out_every_started_card_still_in_todo():
    cards = [todo_card("WB-1", []), todo_card("WB-2", [])]

    choice = start_choice_on_main(cards, set(), "--started", "wb-1")

    assert choice == {"action": "single", "card": "WB-2"}


def start_choice_on_main(cards: list[dict], waiting: set[str], *args: str):
    with (
        patch("linear.project_config", return_value={"parallel-sessions": 3}),
        patch("linear_cli.list_todo_cards", return_value=cards),
        patch(
            "linear_cli.waits_for_answer",
            side_effect=lambda card: card["identifier"] in waiting,
        ),
    ):
        result = CliRunner().invoke(
            linear_cli.cli,
            ["start-choice", "--project", "S", "--branch", "main", *args],
        )

    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_start_choice_runs_the_only_card_able_to_start_when_a_question_waits():
    cards = [todo_card("A", []), todo_card("B", [])]

    assert start_choice_on_main(cards, {"A"}) == {
        "action": "single",
        "card": "B",
    }


def test_start_choice_ends_with_each_reason_when_only_waiting_cards_remain():
    cards = [
        todo_card("WB-1", []),
        todo_card("WB-2", []),
        todo_card("C", ["X"]),
    ]

    choice = start_choice_on_main(cards, {"WB-2"}, "--started", "WB-1")

    assert choice == {
        "action": "blocked",
        "reasons": {
            "WB-1": "started earlier in this run and stopped in Todo",
            "WB-2": "waits for an answer to a lesson question",
            "C": "blocked by X",
        },
    }


def test_waits_for_answer_reads_the_cards_own_comments():
    comments = [comment("**Lesson question from WB-5**\n\nOK?", "T1")]
    with (
        patch("linear_cli.bearer_token", return_value="key"),
        patch("linear_cli.list_comments", return_value=comments) as listing,
    ):
        waiting = REAL_WAITS_FOR_ANSWER({"identifier": "WB-7"})

    assert waiting is True
    listing.assert_called_once_with("key", "WB-7")
