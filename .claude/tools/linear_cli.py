#!/usr/bin/env python3
# /// script
# dependencies = ["click"]
# ///
"""Linear operations the /linear:* skills need that linctl can't express.

Vendored module — no support, no versioning, no PyPI. Copy and adapt
to your needs. See .claude/tools/README.md for the usage contract.

linctl's typed commands cover most of Linear, but not project/parent-scoped
issue queries, project milestones, or board `sortOrder`. Each helper below
builds a GraphQL query and runs it through `linctl graphql`, inheriting
linctl's auth (LINCTL_API_KEY). No second auth path, no `requests`.

    Issue queries
        search_by_project(project, text)              text search in a project
        list_by_project_state(project, state, since)  project + state, opt.
                                                      created since (e.g. -P1W)
        list_by_project_state_type(project, type)     project + state TYPE
                                                      (started/unstarted/...) —
                                                      spans all states in a group
        list_by_parent(parent_id)                     sub-issues of a parent
    Milestones
        list_milestones(project_id)                   {id, name} per milestone
        milestone_open_issues(milestone_id)           non-Done issues in it
        create_milestone(project_id, name, target)    -> {id, name}
        update_milestone_description(id, description)  -> success bool
    Project content
        project_content(project_id)                   project `content` (Vision doc)
        update_project_content(project_id, content)   -> success bool
    Board order
        min_backlog_sort_order(project_id)            lowest Backlog sortOrder
        set_sort_order(issue_id, sort_order)          -> success bool

Usage (deps auto-installed by uv; LINCTL_API_KEY for the workspace):
    LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py \\
        search-by-project --project "<project>" --text "<terms>"

Requires Python 3.10+ and `linctl` on PATH.
"""

import json
import subprocess

import click


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
        raise LinctlError(f"linctl graphql failed: {result.stderr.strip()}")


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


if __name__ == "__main__":
    cli()
