"""
A simple script to find all callables in a Python project that do not have a
return type annotation. We can then add return type annotations to these
callables manually. It's easier than running mypy.ini and Pylance doesn't (yet)
have a way to report on missing return type annotations.
"""

import ast
import os
import re

import click


def load_file(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()


def get_callables_without_return_type(tree: ast.AST) -> list[str]:
    """ast.FunctionDef picks up both standalone functions and class methods."""

    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.returns is None
    ]


SKIP_PATTERNS = [
    "^test_.*",
    "^setUp$",
    "^tearDown$",
    "^root$",
]


def skip_callables_that_match_regex(callables: list[str]) -> list[str]:
    return [
        c for c in callables if not any(re.match(r, c) for r in SKIP_PATTERNS)
    ]


def process_file_for_missing_return_types(file: str) -> None:
    tree = ast.parse(load_file(file))
    callables = get_callables_without_return_type(tree)
    if filtered_callables := skip_callables_that_match_regex(callables):
        print(f"{file:<40} Missing return types: {filtered_callables}")


IGNORE_PATHS = ["venv", ".venv", "type_checks"]


def filter_dirs(dirs: list[str]) -> list[str]:
    return [d for d in dirs if d not in IGNORE_PATHS]


def process_files(directory: str) -> None:
    for root, dirs, files in os.walk(directory):
        dirs[:] = filter_dirs(dirs)
        for file in files:
            if file.endswith(".py"):
                process_file_for_missing_return_types(os.path.join(root, file))


@click.command()
@click.argument("path", required=True, default=".")
def main(path: str) -> None:
    process_files(path)


if __name__ == "__main__":
    main()
