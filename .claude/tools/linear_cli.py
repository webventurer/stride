#!/usr/bin/env python3
# /// script
# dependencies = ["click"]
# ///
"""Linear operations the /linear:* skills need that linctl can't express.

Vendored, no versioning. Each helper builds a GraphQL query and runs it
through `linctl graphql`, inheriting linctl's auth (LINCTL_API_KEY).

    LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py \\
        search-by-project --project "<project>" --text "<terms>"
"""

import json
import subprocess
from pathlib import Path

import click

STATUSES_PATH = (
    Path(__file__).resolve().parent.parent / "commands/linear/linear_statuses.json"
)


class LinctlError(Exception):
    """Raised when the linctl graphql subprocess fails or returns errors."""


def linctl_graphql(query: str, variables: dict) -> dict:
    result = subprocess.run(
        ["linctl", "graphql", "--query", query, "--variables", json.dumps(variables)],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,  # else linctl reads the piped stdin as a competing query source
    )
    raise_for_failure(result)
    return graphql_data(result.stdout)


def raise_for_failure(result: subprocess.CompletedProcess):
    if result.returncode != 0:
        raise LinctlError(
            f"linctl graphql failed (rc={result.returncode}): "
            f"stderr={result.stderr.strip()!r} stdout={result.stdout.strip()!r}"
        )


def graphql_data(stdout: str) -> dict:
    data = json.loads(stdout)
    if data.get("errors"):
        raise LinctlError(f"GraphQL errors: {data['errors']}")
    return data["data"]


# ---- Issue queries ----

NODE_FIELDS = "identifier title state { name type }"


def issues_query(params: str, filters: str) -> str:
    return (
        f"query({params}) {{ "
        f"issues(filter: {{ {filters} }}, first: 250) {{ "
        f"nodes {{ {NODE_FIELDS} }} }} }}"
    )


def search_by_project(project: str, text: str) -> list:
    query = issues_query(
        "$project: String!, $text: String!",
        "project: { name: { eq: $project } } searchableContent: { contains: $text }",
    )
    return linctl_graphql(query, {"project": project, "text": text})["issues"]["nodes"]


def list_by_project_state(project: str, state: str, since: str | None = None) -> list:
    params = "$project: String!, $state: String!"
    filters = "project: { name: { eq: $project } } state: { name: { eq: $state } }"
    variables = {"project": project, "state": state}
    if since:
        params += ", $since: DateTimeOrDuration!"
        filters += " createdAt: { gt: $since }"
        variables["since"] = since
    return linctl_graphql(issues_query(params, filters), variables)["issues"]["nodes"]


def list_by_project_state_type(project: str, state_type: str) -> list:
    query = issues_query(
        "$project: String!, $type: String!",
        "project: { name: { eq: $project } } state: { type: { eq: $type } }",
    )
    return linctl_graphql(query, {"project": project, "type": state_type})["issues"][
        "nodes"
    ]


def list_by_parent(parent_id: str) -> list:
    query = issues_query("$parent: ID!", "parent: { id: { eq: $parent } }")
    return linctl_graphql(query, {"parent": parent_id})["issues"]["nodes"]


# ---- Milestones (no typed linctl command) ----

OPEN_STATE_TYPES = '["backlog", "unstarted", "started"]'


def list_milestones(project_id: str) -> list:
    query = (
        "query($project: String!) { project(id: $project) { "
        "projectMilestones { nodes { id name } } } }"
    )
    data = linctl_graphql(query, {"project": project_id})
    return data["project"]["projectMilestones"]["nodes"]


def milestone_open_issues(milestone_id: str) -> list:
    query = (
        "query($milestone: String!) { projectMilestone(id: $milestone) { "
        f"issues(filter: {{ state: {{ type: {{ in: {OPEN_STATE_TYPES} }} }} }}) "
        "{ nodes { identifier } } } }"
    )
    data = linctl_graphql(query, {"milestone": milestone_id})
    return data["projectMilestone"]["issues"]["nodes"]


def create_milestone(
    project_id: str, name: str, target_date: str | None = None
) -> dict:
    params = "$project: String!, $name: String!"
    fields = "projectId: $project, name: $name"
    variables = {"project": project_id, "name": name}
    if target_date:
        params += ", $target: TimelessDate"
        fields += ", targetDate: $target"
        variables["target"] = target_date
    query = (
        f"mutation({params}) {{ projectMilestoneCreate(input: {{ {fields} }}) "
        "{ projectMilestone { id name } } }"
    )
    return linctl_graphql(query, variables)["projectMilestoneCreate"][
        "projectMilestone"
    ]


def update_milestone_description(milestone_id: str, description: str) -> bool:
    query = (
        "mutation($id: String!, $description: String!) { "
        "projectMilestoneUpdate(id: $id, input: { description: $description }) "
        "{ success } }"
    )
    data = linctl_graphql(query, {"id": milestone_id, "description": description})
    return data["projectMilestoneUpdate"]["success"]


# ---- Project content (linctl project update --description is length-limited
#      and targets the wrong field — the Vision doc lives in `content`) ----


def project_content(project_id: str) -> str | None:
    query = "query($id: String!) { project(id: $id) { content } }"
    return linctl_graphql(query, {"id": project_id})["project"]["content"]


def update_project_content(project_id: str, content: str) -> bool:
    query = (
        "mutation($id: String!, $content: String!) { "
        "projectUpdate(id: $id, input: { content: $content }) { success } }"
    )
    data = linctl_graphql(query, {"id": project_id, "content": content})
    return data["projectUpdate"]["success"]


# ---- Board order (linctl issue update has no --sort-order flag) ----


def min_backlog_sort_order(project_id: str) -> float | None:
    query = (
        "query($project: String!) { project(id: $project) { "
        'issues(first: 1, filter: { state: { type: { eq: "backlog" } } }) '
        "{ nodes { sortOrder } } } }"
    )
    nodes = linctl_graphql(query, {"project": project_id})["project"]["issues"]["nodes"]
    return nodes[0]["sortOrder"] if nodes else None


def set_sort_order(issue_id: str, sort_order: float) -> bool:
    query = (
        "mutation($id: String!, $order: Float!) { "
        "issueUpdate(id: $id, input: { sortOrder: $order }) { success } }"
    )
    return linctl_graphql(query, {"id": issue_id, "order": sort_order})["issueUpdate"][
        "success"
    ]


# ---- Workflow-state drift (board vs the names stride declares) ----


def board_states(team_key: str) -> list:
    query = (
        "query($key: String!) { teams(filter: { key: { eq: $key } }, first: 1) "
        "{ nodes { states { nodes { name type } } } } }"
    )
    nodes = linctl_graphql(query, {"key": team_key})["teams"]["nodes"]
    return nodes[0]["states"]["nodes"] if nodes else []


def first_team_key() -> str | None:
    nodes = linctl_graphql("query { teams(first: 1) { nodes { key } } }", {})["teams"][
        "nodes"
    ]
    return nodes[0]["key"] if nodes else None


def declared_states(config: dict) -> set:
    return {(name, t) for t, names in config["states"].items() for name in names}


def load_statuses() -> dict:
    return json.loads(STATUSES_PATH.read_text())


def state_drift(team_key: str | None = None) -> list:
    board = {(s["name"], s["type"]) for s in board_states(team_key or first_team_key())}
    missing = declared_states(load_statuses()) - board
    return [{"name": n, "type": t} for n, t in sorted(missing)]


# ---- Provision workflow states (linctl can't create a state or set its
#      position; both go through GraphQL) ----

TYPE_COLORS = {
    "backlog": "#bec2c8",
    "unstarted": "#e2e2e2",
    "started": "#f2c94c",
    "completed": "#5e6ad2",
    "canceled": "#95a2b3",
    "duplicate": "#95a2b3",
}

# Linear won't let the API create or reposition these state types.
RESERVED_TYPES = {"duplicate", "triage"}


def team_overview(team_key: str) -> dict:
    query = (
        "query($key: String!) { teams(filter: { key: { eq: $key } }, first: 1) "
        "{ nodes { id states { nodes { id name type position } } "
        "issues(first: 1) { nodes { id } } } } }"
    )
    nodes = linctl_graphql(query, {"key": team_key})["teams"]["nodes"]
    if not nodes:
        return {}
    team = nodes[0]
    return {
        "id": team["id"],
        "states": team["states"]["nodes"],
        "has_issues": bool(team["issues"]["nodes"]),
    }


def create_workflow_state(
    team_id: str, name: str, state_type: str, color: str, position: float
) -> dict:
    query = (
        "mutation($input: WorkflowStateCreateInput!) { "
        "workflowStateCreate(input: $input) { workflowState { id name type } } }"
    )
    state = {
        "teamId": team_id,
        "name": name,
        "type": state_type,
        "color": color,
        "position": position,
    }
    return linctl_graphql(query, {"input": state})["workflowStateCreate"]["workflowState"]


def set_state_position(state_id: str, position: float) -> bool:
    query = (
        "mutation($id: String!, $pos: Float!) { "
        "workflowStateUpdate(id: $id, input: { position: $pos }) { success } }"
    )
    data = linctl_graphql(query, {"id": state_id, "pos": position})
    return data["workflowStateUpdate"]["success"]


def archive_workflow_state(state_id: str) -> bool:
    query = "mutation($id: String!) { workflowStateArchive(id: $id) { success } }"
    return linctl_graphql(query, {"id": state_id})["workflowStateArchive"]["success"]


def canonical_sequence(states: dict) -> list:
    return [name for names in states.values() for name in names]


def orderable_sequence(states: dict) -> list:
    return [
        name
        for state_type, names in states.items()
        if state_type not in RESERVED_TYPES
        for name in names
    ]


def board_order(board: list) -> list:
    return [s["name"] for s in sorted(board, key=lambda s: s["position"])]


def positioned_in_order(target: list, board: list) -> bool:
    pos = {s["name"]: s["position"] for s in board}
    return sorted(target, key=lambda n: pos.get(n, 0.0)) == target


def in_canonical_order(states: dict, board: list) -> bool:
    present = {s["name"] for s in board}
    return positioned_in_order([n for n in orderable_sequence(states) if n in present], board)


def missing_states(states: dict, board: list) -> list:
    types = {n: t for t, names in states.items() for n in names}
    present = {s["name"] for s in board}
    return [{"name": n, "type": types[n]} for n in canonical_sequence(states) if n not in present]


def extra_states(states: dict, board: list) -> list:
    canon = set(canonical_sequence(states))
    return [name for name in board_order(board) if name not in canon]


def advise_report(states: dict, board: list) -> dict:
    return {
        "mode": "advise",
        "canonical_order": canonical_sequence(states),
        "board_order": board_order(board),
        "missing": missing_states(states, board),
        "extra": extra_states(states, board),
        "ordered": in_canonical_order(states, board),
    }


def create_missing(team_id: str, states: dict, ids: dict) -> list:
    todo = [
        (state_type, name)
        for state_type, names in states.items()
        if state_type not in RESERVED_TYPES
        for name in names
        if name not in ids
    ]
    for state_type, name in todo:
        color = TYPE_COLORS[state_type]
        ids[name] = create_workflow_state(team_id, name, state_type, color, 0.0)["id"]
    return [{"name": name, "type": state_type} for state_type, name in todo]


def archive_extra(states: dict, board: list) -> list:
    canon = set(canonical_sequence(states))
    extra = [s for s in board if s["name"] not in canon]
    for s in extra:
        archive_workflow_state(s["id"])
    return [s["name"] for s in extra]


def order_states(states: dict, board: list, ids: dict) -> list:
    target = [n for n in orderable_sequence(states) if n in ids]
    if positioned_in_order(target, board):
        return []
    for i, name in enumerate(target):
        set_state_position(ids[name], float(i))
    return target


def setup_empty_team(team_id: str, states: dict, board: list) -> dict:
    ids = {s["name"]: s["id"] for s in board}
    created = create_missing(team_id, states, ids)
    deleted = archive_extra(states, board)
    reordered = order_states(states, board, ids)
    return {
        "mode": "provisioned",
        "created": created,
        "deleted": deleted,
        "reordered": reordered,
        "in_sync": not (created or deleted or reordered),
    }


def provision_states(team_key: str | None = None) -> dict:
    team = team_overview(team_key or first_team_key())
    if not team:
        raise LinctlError(f"no team found for key {team_key!r}")
    states = load_statuses()["states"]
    if team["has_issues"]:
        return advise_report(states, team["states"])
    return setup_empty_team(team["id"], states, team["states"])


@click.group()
def cli():
    """Linear operations the /linear:* skills need that linctl can't express."""


@cli.command("search-by-project")
@click.option("--project", required=True)
@click.option("--text", required=True)
def search_by_project_cmd(project: str, text: str):
    click.echo(json.dumps(search_by_project(project, text)))


@cli.command("list-by-project-state")
@click.option("--project", required=True)
@click.option("--state", required=True)
@click.option("--since", default=None, help="ISO8601 duration/datetime, e.g. -P1W")
def list_by_project_state_cmd(project: str, state: str, since: str):
    click.echo(json.dumps(list_by_project_state(project, state, since)))


@cli.command("list-by-project-state-type")
@click.option("--project", required=True)
@click.option(
    "--type",
    "state_type",
    required=True,
    help="State type: started, unstarted, backlog, completed, canceled",
)
def list_by_project_state_type_cmd(project: str, state_type: str):
    click.echo(json.dumps(list_by_project_state_type(project, state_type)))


@cli.command("list-by-parent")
@click.argument("parent_id")
def list_by_parent_cmd(parent_id: str):
    click.echo(json.dumps(list_by_parent(parent_id)))


@cli.command("list-milestones")
@click.argument("project_id")
def list_milestones_cmd(project_id: str):
    click.echo(json.dumps(list_milestones(project_id)))


@cli.command("milestone-open-issues")
@click.argument("milestone_id")
def milestone_open_issues_cmd(milestone_id: str):
    click.echo(json.dumps(milestone_open_issues(milestone_id)))


@cli.command("create-milestone")
@click.option("--project", "project_id", required=True)
@click.option("--name", required=True)
@click.option("--target-date", default=None, help="TimelessDate, e.g. 2026-12-31")
def create_milestone_cmd(project_id: str, name: str, target_date: str):
    click.echo(json.dumps(create_milestone(project_id, name, target_date)))


@cli.command("update-milestone-description")
@click.argument("milestone_id")
@click.option("--description", required=True)
def update_milestone_description_cmd(milestone_id: str, description: str):
    click.echo(json.dumps(update_milestone_description(milestone_id, description)))


@cli.command("get-project-content")
@click.argument("project_id")
def get_project_content_cmd(project_id: str):
    click.echo(project_content(project_id) or "")


@cli.command("update-project-content")
@click.argument("project_id")
@click.option("--content", required=True)
def update_project_content_cmd(project_id: str, content: str):
    click.echo(json.dumps(update_project_content(project_id, content)))


@cli.command("min-backlog-sort-order")
@click.argument("project_id")
def min_backlog_sort_order_cmd(project_id: str):
    click.echo(json.dumps(min_backlog_sort_order(project_id)))


@cli.command("set-sort-order")
@click.argument("issue_id")
@click.option("--sort-order", type=float, required=True)
def set_sort_order_cmd(issue_id: str, sort_order: float):
    click.echo(json.dumps(set_sort_order(issue_id, sort_order)))


@cli.command("state-drift")
@click.option("--team", "team_key", default=None, help="Team key (e.g. WB); defaults to the key's first team")
def state_drift_cmd(team_key: str):
    click.echo(json.dumps(state_drift(team_key)))


@cli.command("provision-states")
@click.option("--team", "team_key", default=None, help="Team key (e.g. WB); defaults to the key's first team")
def provision_states_cmd(team_key: str):
    click.echo(json.dumps(provision_states(team_key)))


if __name__ == "__main__":
    cli()
