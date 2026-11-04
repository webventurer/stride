#!/usr/bin/env python3
# /// script
# dependencies = ["click", "python-dotenv", "requests"]
# ///
"""Commands for recovering team-scoped labels in a stride workspace.

The label recovery runbook needs two things the stride CLI doesn't expose:
a list of team-scoped labels, and a way to send any GraphQL query or
mutation. Both go through stride's Linear client in `linear.py`.

    LINEAR_API_KEY=$LINEAR_<WORKSPACE>_API_KEY \\
        uv run .claude/tools/label_recovery.py team-labels
"""

import click
from linear import bearer_token, graphql_data, list_labels

NO_VARIABLES: dict = {}


@click.group()
def cli():
    pass


@cli.command("graphql")
@click.argument("query")
def graphql_cmd(query: str):
    """Print what Linear returns for QUERY."""
    click.echo(graphql_data(query, NO_VARIABLES))


@cli.command("team-labels")
def team_labels_cmd():
    """Print each team-scoped label as `<id> | <name> | <colour>`."""
    for label in team_scoped_labels(list_labels(bearer_token())):
        click.echo(label_line(label))


def team_scoped_labels(labels: list) -> list:
    return [label for label in labels if label.get("team")]


def label_line(label: dict) -> str:
    return f"{label['id']} | {label['name']} | {label['color']}"


if __name__ == "__main__":
    cli()
