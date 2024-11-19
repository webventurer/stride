"""
A simple script to find all callables in a Python project that do have something
to return, however there is no return type annotation. We can then add return
type annotations to these callables manually. We specifically avoid adding "->
None:" to functions/methods which return nothing as it clutters up the page while not adding anything helpful.

Note: Also do a manual search for "-> None:" so you can remove them for
readability.

It's easier than running mypy.ini and Pylance doesn't (yet) have a way to report
on missing return type annotations.
"""

__package__ = __import__("config").infer_package(__file__)  # Allow rel imports

import re

import click

from . import inspector

filters = [
    inspector.no_type_ignore_comment,
    inspector.no_return_type_annotation,
    inspector.callables_with_return_values,
]


SKIP_PATTERNS = [
    "^test_.*",
    "^setUp$",
    "^tearDown$",
    "^root$",
]


def matches_skip_pattern(callable_name: str) -> bool:
    return any(re.match(pattern, callable_name) for pattern in SKIP_PATTERNS)


def skip_callables_that_match_regex(callables: list[str]) -> list[str]:
    return [c for c in callables if not matches_skip_pattern(c)]


def find_missing_return_types(file: str):
    block = inspector.CodeBlock.from_file(file)
    callables = block.find_matching_functions(filters)
    if filtered_callables := skip_callables_that_match_regex(callables):
        print(f"{file:<40} No return type: {filtered_callables}")


@click.command()
@click.argument("path", required=True, default=".")
def main(path: str):
    inspector.process_files(path, find_missing_return_types)


if __name__ == "__main__":
    main()
