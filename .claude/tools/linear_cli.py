#!/usr/bin/env python3
# /// script
# dependencies = ["click", "requests"]
# ///
"""CLI front-end for the Linear GraphQL client in `linear.py`.

Every command outputs JSON. stride's slash commands parse JSON; ad-hoc
terminal use pipes through `| jq`. The library lives in `linear.py`;
this file is click wiring + a handful of name → UUID resolvers.

    LINEAR_API_KEY=$LINEAR_<WORKSPACE>_API_KEY \\
        uv run .claude/tools/linear_cli.py search-by-project \\
        --project "<project>" --text "<terms>"
"""

import json
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent))

from linear import (  # noqa: E402
    bearer_token,
    create_attachment,
    create_comment,
    create_issue,
    create_milestone,
    create_project,
    get_issue,
    get_project,
    get_team,
    list_by_parent,
    list_by_project_state,
    list_by_project_state_type,
    list_comments,
    list_labels,
    list_milestones,
    list_projects,
    list_team_states,
    list_teams,
    milestone_open_issues,
    min_backlog_sort_order,
    project_content,
    provision_states,
    read_text_arg,
    resolve_labels_for_team,
    resolve_project_id,
    resolve_state_for_issue,
    search_by_project,
    set_project_view_manual,
    set_sort_order,
    state_drift,
    update_issue,
    update_milestone_description,
    update_project,
    update_project_content,
    whoami,
)


@click.group()
def cli():
    """Linear GraphQL client + the operations the /linear:* skills need."""


# ---- Flat commands: ops the existing /linear:* skills already use ----


@cli.command("search-by-project")
@click.option("--project", required=True)
@click.option("--text", required=True)
def search_by_project_cmd(project: str, text: str):
    echo_json(search_by_project(project, text))


@cli.command("list-by-project-state")
@click.option("--project", required=True)
@click.option("--state", required=True)
@click.option("--since", default=None, help="ISO8601 duration/datetime, e.g. -P1W")
def list_by_project_state_cmd(project: str, state: str, since: str):
    echo_json(list_by_project_state(project, state, since))


@cli.command("list-by-project-state-type")
@click.option("--project", required=True)
@click.option(
    "--type",
    "state_type",
    required=True,
    help="State type: started, unstarted, backlog, completed, canceled",
)
def list_by_project_state_type_cmd(project: str, state_type: str):
    echo_json(list_by_project_state_type(project, state_type))


@cli.command("list-by-parent")
@click.argument("parent_id")
def list_by_parent_cmd(parent_id: str):
    echo_json(list_by_parent(parent_id))


@cli.command("list-milestones")
@click.argument("project_id")
def list_milestones_cmd(project_id: str):
    echo_json(list_milestones(project_id))


@cli.command("milestone-open-issues")
@click.argument("milestone_id")
def milestone_open_issues_cmd(milestone_id: str):
    echo_json(milestone_open_issues(milestone_id))


@cli.command("create-milestone")
@click.option("--project", "project_id", required=True)
@click.option("--name", required=True)
@click.option("--target-date", default=None, help="TimelessDate, e.g. 2026-12-31")
def create_milestone_cmd(project_id: str, name: str, target_date: str):
    echo_json(create_milestone(project_id, name, target_date))


@cli.command("update-milestone-description")
@click.argument("milestone_id")
@click.option("--description", required=True)
def update_milestone_description_cmd(milestone_id: str, description: str):
    echo_json(update_milestone_description(milestone_id, description))


@cli.command("get-project-content")
@click.argument("project_id")
def get_project_content_cmd(project_id: str):
    click.echo(project_content(project_id) or "")


@cli.command("update-project-content")
@click.argument("project_id")
@click.option(
    "--content",
    required=True,
    help="Inline text, @path to read a file, or - to read stdin",
)
def update_project_content_cmd(project_id: str, content: str):
    echo_json(update_project_content(project_id, read_text_arg(content)))


@cli.command("min-backlog-sort-order")
@click.argument("project_id")
def min_backlog_sort_order_cmd(project_id: str):
    echo_json(min_backlog_sort_order(project_id))


@cli.command("set-sort-order")
@click.argument("issue_id")
@click.option("--sort-order", type=float, required=True)
def set_sort_order_cmd(issue_id: str, sort_order: float):
    echo_json(set_sort_order(issue_id, sort_order))


@cli.command("set-project-view-manual")
@click.argument("project_id")
def set_project_view_manual_cmd(project_id: str):
    echo_json(set_project_view_manual(project_id))


@cli.command("state-drift")
@click.option(
    "--team",
    "team_key",
    default=None,
    help="Team key (e.g. WB); defaults to the key's first team",
)
def state_drift_cmd(team_key: str):
    echo_json(state_drift(team_key))


@cli.command("provision-states")
@click.option(
    "--team",
    "team_key",
    default=None,
    help="Team key (e.g. WB); defaults to the key's first team",
)
def provision_states_cmd(team_key: str):
    echo_json(provision_states(team_key))


# ---- Issue / comment / team / project / label / whoami subgroups ----


@cli.command("whoami")
def whoami_cmd():
    echo_json(whoami(bearer_token()))


@cli.group("issue")
def issue_group():
    pass


@issue_group.command("get")
@click.argument("identifier")
def issue_get_cmd(identifier: str):
    issue = get_issue(bearer_token(), identifier)
    if not issue:
        raise click.ClickException(f"Issue not found: {identifier}")
    echo_json(issue)


@issue_group.command("create")
@click.option("-t", "--team", required=True, help="Team key (e.g. WB)")
@click.option("--project", "project_name", default=None, help="Project name or UUID")
@click.option(
    "--project-milestone",
    "milestone_name",
    default=None,
    help="Project milestone name or UUID",
)
@click.option(
    "--state",
    "state_name",
    default=None,
    help="State name (defaults to team default)",
)
@click.option("--title", required=True)
@click.option(
    "--description",
    default="",
    help="Inline text, @path to read a file, or - to read stdin",
)
@click.option("--priority", type=int, default=None, help="0-4 (3=Medium default)")
@click.option("--labels", default=None, help="Comma-separated label names")
@click.option(
    "--parent", "parent_identifier", default=None, help="Parent issue identifier"
)
def issue_create_cmd(
    team: str,
    project_name: str | None,
    milestone_name: str | None,
    state_name: str | None,
    title: str,
    description: str,
    priority: int | None,
    labels: str | None,
    parent_identifier: str | None,
):
    api = bearer_token()
    team_obj = team_or_fail(api, team)
    project_id = resolve_project_id(api, project_name) if project_name else None
    echo_json(create_issue(
        api,
        team_id=team_obj["id"],
        title=title,
        description=read_text_arg(description),
        project_id=project_id,
        priority=priority,
        state_id=state_id_for_create(api, team, state_name),
        project_milestone_id=milestone_id_for_create(api, project_id, milestone_name),
        label_ids=label_ids_for_create(api, team_obj["id"], labels),
        parent_id=parent_id_or_none(api, parent_identifier),
    ))


@issue_group.command("update")
@click.argument("identifier")
@click.option("--state", "state_name", default=None, help="State name (e.g. Doing)")
@click.option(
    "--parent", "parent_identifier", default=None, help="Parent issue identifier"
)
@click.option("--title", default=None)
@click.option("--description", default=None)
@click.option("--labels", default=None, help="Comma-separated label names (replaces)")
@click.option("--priority", type=int, default=None)
def issue_update_cmd(
    identifier: str,
    state_name: str | None,
    parent_identifier: str | None,
    title: str | None,
    description: str | None,
    labels: str | None,
    priority: int | None,
):
    api = bearer_token()
    issue_uuid = get_issue(api, identifier)["id"]
    echo_json(update_issue(
        api,
        issue_uuid,
        title=title,
        description=description,
        priority=priority,
        state_id=state_id_for_update(api, identifier, state_name),
        parent_id=parent_id_or_none(api, parent_identifier),
        label_ids=label_ids_for_update(api, identifier, labels),
    ))


@issue_group.command("attach")
@click.argument("identifier")
@click.option("--url", required=True)
@click.option(
    "--title",
    "attach_title",
    default=None,
    help="Attachment title (defaults to the URL)",
)
def issue_attach_cmd(identifier: str, url: str, attach_title: str | None):
    api = bearer_token()
    issue_uuid = get_issue(api, identifier)["id"]
    attachment_id = create_attachment(
        api,
        issue_uuid,
        title=attach_title or url,
        url=url,
    )
    echo_json({"id": attachment_id, "url": url})


@cli.group("comment")
def comment_group():
    pass


@comment_group.command("list")
@click.argument("issue_identifier")
def comment_list_cmd(issue_identifier: str):
    echo_json(list_comments(bearer_token(), issue_identifier))


@comment_group.command("create")
@click.argument("issue_identifier")
@click.option(
    "--body",
    required=True,
    help="Inline text, @path to read a file, or - to read stdin",
)
def comment_create_cmd(issue_identifier: str, body: str):
    api = bearer_token()
    issue_uuid = get_issue(api, issue_identifier)["id"]
    echo_json(create_comment(api, issue_uuid, read_text_arg(body)))


@cli.group("team")
def team_group():
    pass


@team_group.command("list")
def team_list_cmd():
    echo_json(list_teams(bearer_token()))


@team_group.command("state")
@click.option("-t", "--team", required=True, help="Team key (e.g. WB)")
def team_state_cmd(team: str):
    echo_json(list_team_states(bearer_token(), team))


@cli.group("project")
def project_group():
    pass


@project_group.command("list")
def project_list_cmd():
    echo_json(list_projects(bearer_token()))


@project_group.command("create")
@click.option("-t", "--team", required=True, help="Team key (e.g. WB)")
@click.option("--name", required=True)
@click.option("--description", default=None, help="Project subtitle")
@click.option("--content", default=None, help="Long-form project body (Vision)")
def project_create_cmd(
    team: str,
    name: str,
    description: str | None,
    content: str | None,
):
    api = bearer_token()
    team_obj = team_or_fail(api, team)
    project_id = create_project(
        api, team_obj["id"], name, description=description, content=content,
    )
    echo_json(get_project(api, project_id))


@project_group.command("get")
@click.argument("identifier")
def project_get_cmd(identifier: str):
    api = bearer_token()
    echo_json(get_project(api, resolve_project_id(api, identifier)))


@project_group.command("update")
@click.argument("identifier")
@click.option("--description", default=None, help="Project subtitle")
def project_update_cmd(identifier: str, description: str | None):
    if description is None:
        raise click.ClickException("Nothing to update — pass --description")
    api = bearer_token()
    update_project(api, resolve_project_id(api, identifier), description=description)
    echo_json({"identifier": identifier, "updated": True})


@cli.group("label")
def label_group():
    pass


@label_group.command("list")
@click.option("-t", "--team", required=True, help="Team key (e.g. WB)")
def label_list_cmd(team: str):
    api = bearer_token()
    echo_json(list_labels(api, team_or_fail(api, team)["id"]))


# ---- CLI-only helpers ----


def echo_json(payload: dict | list) -> None:
    click.echo(json.dumps(payload))


def team_or_fail(api_key: str, team_key: str) -> dict:
    team = get_team(api_key, team_key)
    if not team:
        raise click.ClickException(f"Team not found: {team_key!r}")
    return team


def parent_id_or_none(api_key: str, parent_identifier: str | None) -> str | None:
    if parent_identifier is None:
        return None
    return get_issue(api_key, parent_identifier)["id"]


def state_id_for_create(
    api_key: str,
    team_key: str,
    state_name: str | None,
) -> str | None:
    if state_name is None:
        return None
    for state in list_team_states(api_key, team_key):
        if state["name"] == state_name:
            return state["id"]
    raise click.ClickException(f"State {state_name!r} not found on team {team_key!r}")


def state_id_for_update(
    api_key: str,
    identifier: str,
    state_name: str | None,
) -> str | None:
    if state_name is None:
        return None
    return resolve_state_for_issue(api_key, identifier, state_name)[1]


def milestone_id_for_create(
    api_key: str,
    project_id: str | None,
    name: str | None,
) -> str | None:
    if not (name and project_id):
        return None
    for milestone in list_milestones(project_id):
        if milestone["name"] == name:
            return milestone["id"]
    raise click.ClickException(f"Milestone {name!r} not found on project")


def label_ids_for_create(
    api_key: str,
    team_id: str,
    labels: str | None,
) -> list | None:
    if not labels:
        return None
    return resolve_labels_for_team(
        api_key,
        team_id,
        [n.strip() for n in labels.split(",")],
    )


def label_ids_for_update(
    api_key: str,
    identifier: str,
    labels: str | None,
) -> list | None:
    if labels is None:
        return None
    issue = get_issue(api_key, identifier)
    return resolve_labels_for_team(
        api_key,
        issue["team"]["id"],
        [n.strip() for n in labels.split(",")],
    )


if __name__ == "__main__":
    cli()
