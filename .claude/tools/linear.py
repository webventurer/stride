#!/usr/bin/env python3
# /// script
# dependencies = ["requests"]
# ///
"""Linear GraphQL client — the library the /linear:* skills' CLI sits on.

Talks Linear's GraphQL API directly via `requests`. Reads the bearer
token from `LINEAR_API_KEY` (canonical) or `LINCTL_API_KEY` (legacy
compat).

This module is import-only — for the CLI front-end, see `linear_cli.py`.
"""

import json
import os
import re
import time
from pathlib import Path

import requests

API_URL = "https://api.linear.app/graphql"

STATUSES_PATH = (
    Path(__file__).resolve().parent.parent / "commands/linear/linear_statuses.json"
)


# ---- GraphQL primitives ----


class LinearError(Exception):
    """Raised when a Linear API call fails — HTTP, network, or GraphQL errors."""


# Legacy alias — older callers/tests reference this name.
LinctlError = LinearError


def graphql(
    api_key: str, query: str, variables: dict | None = None, retries: int = 3
) -> dict:
    body = {"query": query}
    if variables:
        body["variables"] = variables
    for attempt in range(retries):
        try:
            return post_and_check(api_key, body, query)
        except (requests.ConnectionError, requests.Timeout) as e:
            if attempt == retries - 1:
                raise LinearError(
                    f"connection failed after {retries} attempts on "
                    f"{operation_name(query)}: {e}"
                ) from e
            time.sleep(2**attempt)


def post_and_check(api_key: str, body: dict, query: str) -> dict:
    resp = requests.post(
        API_URL,
        json=body,
        headers={"Authorization": api_key, "Content-Type": "application/json"},
    )
    raise_for_http(resp, query)
    data = resp.json()
    raise_for_graphql_errors(data, query)
    return data


def raise_for_http(resp: requests.Response, query: str):
    if resp.status_code >= 400:
        raise LinearError(
            f"HTTP {resp.status_code} on {operation_name(query)}: {resp.text[:200]}"
        )


def raise_for_graphql_errors(data: dict, query: str):
    errors = data.get("errors")
    if errors:
        msgs = "; ".join(e.get("message", "?") for e in errors)
        raise LinearError(f"GraphQL errors on {operation_name(query)}: {msgs}")


def operation_name(query: str) -> str:
    match = re.search(r"(?:mutation|query)\s*(\w+)?\s*[\(\{]", query)
    if match and match.group(1):
        return match.group(1)
    inner = re.search(r"\{\s*(\w+)", query)
    return inner.group(1) if inner else "?"


def require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Env var {name} is not set")
    return val


LINEAR_PROJECT_PATH = Path(".linear_project")


def parse_project_config(text: str) -> dict:
    config: dict = {}
    for line in config_lines(text):
        absorb_config_line(config, line)
    return config


def config_lines(text: str) -> list:
    return [s for s in (raw.strip() for raw in text.splitlines()) if s and not s.startswith("#")]


def absorb_config_line(config: dict, line: str):
    if "=" in line:
        k, v = line.split("=", 1)
        config[k.strip()] = v.strip()
    elif "project" not in config:
        # Backward compat: bare project name on first non-comment line.
        config["project"] = line


def project_config() -> dict:
    return parse_project_config(LINEAR_PROJECT_PATH.read_text()) if LINEAR_PROJECT_PATH.exists() else {}


def token_from_project_config() -> str | None:
    env_name = project_config().get("api_key_env")
    return os.environ.get(env_name) if env_name else None


def bearer_token() -> str:
    token = (
        os.environ.get("LINEAR_API_KEY")
        or os.environ.get("LINCTL_API_KEY")
        or token_from_project_config()
    )
    if not token:
        raise LinearError(
            "No Linear credentials. Set LINEAR_API_KEY in ~/.env, name an "
            "api_key_env in .linear_project, or set LINCTL_API_KEY (legacy)."
        )
    return token


def linctl_graphql(query: str, variables: dict) -> dict:
    """Run a GraphQL query, return the `data` payload.

    Name kept for backward compat — was a subprocess wrapper around
    `linctl graphql`, now hits Linear directly via requests.
    """
    return graphql(bearer_token(), query, variables)["data"]


# ---- Mutations: issues ----

ISSUE_FULL_FIELDS = """
    id identifier title description priority url branchName createdAt updatedAt
    state { id name type color description position }
    assignee { id name email }
    team { id key name }
    project { id name }
    projectMilestone { id name }
    parent { id identifier title state { name type } }
    labels { nodes { id name color } }
"""

CREATE_ISSUE_QUERY = f"""mutation($input: IssueCreateInput!) {{
    issueCreate(input: $input) {{
        issue {{ {ISSUE_FULL_FIELDS} }}
    }}
}}"""


def create_issue(
    api_key: str,
    team_id: str,
    title: str,
    project_id: str | None = None,
    state_id: str | None = None,
    description: str = "",
    label_ids: list | None = None,
    parent_id: str | None = None,
    project_milestone_id: str | None = None,
    priority: int | None = None,
) -> dict:
    input_data = {"teamId": team_id, "title": title, "description": description}
    if project_id:
        input_data["projectId"] = project_id
    if state_id:
        input_data["stateId"] = state_id
    if label_ids:
        input_data["labelIds"] = label_ids
    if parent_id:
        input_data["parentId"] = parent_id
    if project_milestone_id:
        input_data["projectMilestoneId"] = project_milestone_id
    if priority is not None:
        input_data["priority"] = priority
    data = graphql(api_key, CREATE_ISSUE_QUERY, variables={"input": input_data})
    return data["data"]["issueCreate"]["issue"]


UPDATE_ISSUE_QUERY = f"""mutation($id: String!, $input: IssueUpdateInput!) {{
    issueUpdate(id: $id, input: $input) {{
        issue {{ {ISSUE_FULL_FIELDS} }}
    }}
}}"""


def update_issue(
    api_key: str,
    issue_id: str,
    title: str | None = None,
    description: str | None = None,
    state_id: str | None = None,
    label_ids: list | None = None,
    parent_id: str | None = None,
    priority: int | None = None,
) -> dict:
    input_data = {}
    if title is not None:
        input_data["title"] = title
    if description is not None:
        input_data["description"] = description
    if state_id is not None:
        input_data["stateId"] = state_id
    if label_ids is not None:
        input_data["labelIds"] = label_ids
    if parent_id is not None:
        input_data["parentId"] = parent_id
    if priority is not None:
        input_data["priority"] = priority
    data = graphql(
        api_key,
        UPDATE_ISSUE_QUERY,
        variables={"id": issue_id, "input": input_data},
    )
    return data["data"]["issueUpdate"]["issue"]


CREATE_ATTACHMENT_QUERY = """mutation($input: AttachmentCreateInput!) {
    attachmentCreate(input: $input) {
        attachment { id }
    }
}"""


def create_attachment(
    api_key: str,
    issue_id: str,
    title: str,
    url: str,
    subtitle: str | None = None,
    metadata: dict | None = None,
) -> str:
    input_data = {"issueId": issue_id, "title": title, "url": url}
    if subtitle:
        input_data["subtitle"] = subtitle
    if metadata:
        input_data["metadata"] = metadata
    data = graphql(api_key, CREATE_ATTACHMENT_QUERY, variables={"input": input_data})
    return data["data"]["attachmentCreate"]["attachment"]["id"]


# ---- Mutations: projects ----

CREATE_PROJECT_QUERY = """mutation($input: ProjectCreateInput!) {
    projectCreate(input: $input) {
        project { id }
    }
}"""


def create_project(
    api_key: str,
    team_id: str,
    name: str,
    description: str | None = None,
    content: str | None = None,
) -> str:
    input_data = {"name": name, "teamIds": [team_id]}
    if description is not None:
        input_data["description"] = description
    if content is not None:
        input_data["content"] = content
    data = graphql(api_key, CREATE_PROJECT_QUERY, variables={"input": input_data})
    return data["data"]["projectCreate"]["project"]["id"]


UPDATE_PROJECT_QUERY = """mutation($id: String!, $input: ProjectUpdateInput!) {
    projectUpdate(id: $id, input: $input) {
        project { id }
    }
}"""


def update_project(
    api_key: str,
    project_id: str,
    description: str | None = None,
    content: str | None = None,
) -> str:
    input_data = {}
    if description is not None:
        input_data["description"] = description
    if content is not None:
        input_data["content"] = content
    data = graphql(
        api_key,
        UPDATE_PROJECT_QUERY,
        variables={"id": project_id, "input": input_data},
    )
    return data["data"]["projectUpdate"]["project"]["id"]


# ---- Queries: list helpers ----

LIST_PROJECTS_QUERY = """{{
    projects(first: 50 {after}) {{
        nodes {{
            id name
            teams {{ nodes {{ id name }} }}
        }}
        pageInfo {{ hasNextPage endCursor }}
    }}
}}"""


def list_projects(api_key: str, team_id: str | None = None) -> list:
    projects, cursor = [], None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = graphql(api_key, LIST_PROJECTS_QUERY.format(after=after))
        page = data["data"]["projects"]
        projects.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return filter_by_team(projects, team_id) if team_id else projects


def filter_by_team(projects: list, team_id: str) -> list:
    return [p for p in projects if any(t["id"] == team_id for t in p["teams"]["nodes"])]


LIST_LABELS_QUERY = """{{
    issueLabels(first: 250 {after}) {{
        nodes {{ id name color team {{ id }} }}
        pageInfo {{ hasNextPage endCursor }}
    }}
}}"""


def list_labels(api_key: str, team_id: str | None = None) -> list:
    labels, cursor = [], None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = graphql(api_key, LIST_LABELS_QUERY.format(after=after))
        page = data["data"]["issueLabels"]
        labels.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return labels_for_team(labels, team_id) if team_id else labels


def labels_for_team(labels: list, team_id: str) -> list:
    return [lbl for lbl in labels if lbl.get("team") and lbl["team"]["id"] == team_id]


# ---- Read: issues, projects, teams, comments, viewer ----


def get_issue(api_key: str, identifier: str) -> dict:
    query = f"query($id: String!) {{ issue(id: $id) {{ {ISSUE_FULL_FIELDS} }} }}"
    return graphql(api_key, query, {"id": identifier})["data"]["issue"]


def get_project(api_key: str, identifier: str) -> dict:
    query = """query($id: String!) { project(id: $id) {
        id name description content url state startDate targetDate progress
        teams { nodes { id key name } }
    } }"""
    return graphql(api_key, query, {"id": identifier})["data"]["project"]


def whoami(api_key: str) -> dict:
    query = "{ viewer { id name email avatarUrl } }"
    user = graphql(api_key, query)["data"]["viewer"]
    return {"authenticated": True, "user": user}


def list_teams(api_key: str) -> list:
    query = """{ teams(first: 250) { nodes {
        id key name description icon color private issueCount
        cyclesEnabled cycleStartDay cycleDuration upcomingCycleCount
    } } }"""
    return graphql(api_key, query)["data"]["teams"]["nodes"]


def get_team(api_key: str, key: str) -> dict | None:
    query = """query($key: String!) { teams(filter: { key: { eq: $key } }, first: 1) { nodes {
        id key name description issueCount
    } } }"""
    nodes = graphql(api_key, query, {"key": key})["data"]["teams"]["nodes"]
    return nodes[0] if nodes else None


def list_team_states(api_key: str, team_key: str) -> list:
    query = """query($key: String!) { teams(filter: { key: { eq: $key } }, first: 1) { nodes {
        states { nodes { id name type color position description } }
    } } }"""
    nodes = graphql(api_key, query, {"key": team_key})["data"]["teams"]["nodes"]
    return nodes[0]["states"]["nodes"] if nodes else []


def list_comments(api_key: str, issue_id: str) -> list:
    query = """query($id: String!) { issue(id: $id) { comments(first: 250) { nodes {
        id body createdAt updatedAt
        user { id name email }
    } } } }"""
    return graphql(api_key, query, {"id": issue_id})["data"]["issue"]["comments"][
        "nodes"
    ]


CREATE_COMMENT_QUERY = """mutation($input: CommentCreateInput!) {
    commentCreate(input: $input) { comment { id body createdAt
        user { id name email }
    } }
}"""


def create_comment(api_key: str, issue_uuid: str, body: str) -> dict:
    data = graphql(
        api_key,
        CREATE_COMMENT_QUERY,
        variables={"input": {"issueId": issue_uuid, "body": body}},
    )
    return data["data"]["commentCreate"]["comment"]


# ---- Resolvers: name/identifier → UUID lookups for the CLI ----


def resolve_project_id(api_key: str, name_or_id: str) -> str:
    if looks_like_uuid(name_or_id):
        return name_or_id
    query = (
        "query($name: String!) { projects(filter: { name: { eq: $name } }, first: 1) "
        "{ nodes { id } } }"
    )
    nodes = graphql(api_key, query, {"name": name_or_id})["data"]["projects"]["nodes"]
    if not nodes:
        raise LinearError(f"Project not found: {name_or_id!r}")
    return nodes[0]["id"]


def resolve_state_for_issue(
    api_key: str, issue_identifier: str, state_name: str
) -> tuple[str, str]:
    query = """query($id: String!) { issue(id: $id) {
        id team { states { nodes { id name } } }
    } }"""
    issue = graphql(api_key, query, {"id": issue_identifier})["data"]["issue"]
    if not issue:
        raise LinearError(f"Issue not found: {issue_identifier!r}")
    for state in issue["team"]["states"]["nodes"]:
        if state["name"] == state_name:
            return issue["id"], state["id"]
    raise LinearError(f"State {state_name!r} not found on team for {issue_identifier}")


def resolve_labels_for_team(api_key: str, team_id: str, names: list) -> list:
    labels = list_labels(api_key, team_id)
    by_name = {lbl["name"]: lbl["id"] for lbl in labels}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise LinearError(f"Labels not found on team: {missing}")
    return [by_name[n] for n in names]


def looks_like_uuid(value: str) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", value or ""
        )
    )


# ---- Issue queries (existing /linear:* operations) ----

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


# ---- Milestones ----

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


# ---- Project content (Vision lives in `content`, not `description`) ----


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


# ---- Board order ----


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


# ---- Workflow-state drift ----


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


# ---- Provision workflow states ----

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
    return linctl_graphql(query, {"input": state})["workflowStateCreate"][
        "workflowState"
    ]


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
    return positioned_in_order(
        [n for n in orderable_sequence(states) if n in present], board
    )


def missing_states(states: dict, board: list) -> list:
    types = {n: t for t, names in states.items() for n in names}
    present = {s["name"] for s in board}
    return [
        {"name": n, "type": types[n]}
        for n in canonical_sequence(states)
        if n not in present
    ]


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
    extra = [
        s for s in board if s["name"] not in canon and s["type"] not in RESERVED_TYPES
    ]
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
        raise LinearError(f"no team found for key {team_key!r}")
    states = load_statuses()["states"]
    if team["has_issues"]:
        return advise_report(states, team["states"])
    return setup_empty_team(team["id"], states, team["states"])
