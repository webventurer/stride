"""Inspect Python code for for specific patterns we can fix manually"""

import ast
import os
import sys
from typing import Callable, Self, TypeGuard

from . import export


class CodeBlock:
    @classmethod
    def from_file(cls, filename: str) -> Self:
        with open(filename, "r") as f:
            return cls(f.read())

    def __init__(self, code: str):
        self.code = code

    @property
    def tree(self) -> ast.Module:
        return ast.parse(self.code)

    @property
    def lines(self) -> list[str]:
        return self.code.splitlines()

    @property
    def nodes(self) -> list[ast.AST]:
        return list(ast.walk(self.tree))

    @property
    def func_defs(self) -> list[ast.FunctionDef]:
        return [n for n in self.nodes if isinstance(n, ast.FunctionDef)]

    def match_all_cond(self, f: ast.FunctionDef, conds: list[Callable]) -> bool:
        return all(cond(f, self.lines) for cond in conds)

    def is_variable_node(self, node: ast.AST) -> TypeGuard[ast.Name]:
        return isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)

    def matches_any_pattern(self, node: ast.AST, patterns: list) -> bool:
        return any(pattern(node) for pattern in patterns)

    def get_variable_nodes(self) -> list[ast.Name]:
        return [node for node in self.nodes if self.is_variable_node(node)]

    def get_matching_names(self, nodes: list[ast.Name], patterns: list) -> list:
        return [n.id for n in nodes if self.matches_any_pattern(n, patterns)]

    def find_matching_functions(self, funcs: list[Callable]) -> list[str]:
        return [f.name for f in self.func_defs if self.match_all_cond(f, funcs)]

    def find_matching_variables(self, patterns: list[Callable]) -> list[str]:
        return self.get_matching_names(self.get_variable_nodes(), patterns)


# Function definition filters


@export
def has_docstring(node: ast.FunctionDef, *args: tuple) -> bool:
    return ast.get_docstring(node) is not None


@export
def docstring_adjacent_to_code(node: ast.FunctionDef, lines: list[str]) -> bool:
    if (docstring_end_lineno := node.body[0].end_lineno) is None:
        return False
    return bool(
        docstring_end_lineno < len(lines)
        and lines[docstring_end_lineno].strip()
    )


def is_node_with_lineno(node: ast.AST) -> TypeGuard[ast.stmt | ast.expr]:
    """Only ast.stmt and ast.expr types guaranteed to have lineno attribute."""

    return isinstance(node, (ast.stmt, ast.expr))


@export
def no_type_ignore_comment(node: ast.AST, lines: list[str]) -> bool:
    if not is_node_with_lineno(node):
        return False
    return "# type: ignore" not in lines[node.lineno - 1]


@export
def callables_with_return_values(node: ast.FunctionDef, *args: tuple) -> bool:
    return any(
        isinstance(subnode, ast.Return) and subnode.value is not None
        for subnode in ast.walk(node)
    )


@export
def no_return_type_annotation(node: ast.FunctionDef, *args: tuple) -> bool:
    return node.returns is None


# Variable filters


@export
def vars_that_start_with_df(node: ast.AST, starts_with: str = "df_") -> bool:
    return isinstance(node, ast.Name) and node.id.startswith(starts_with)


@export
def has_type_prefix(node: ast.AST) -> bool:
    pf = ("str_", "dict_", "list_", "int_", "float_", "bool_")
    return isinstance(node, ast.Name) and any(node.id.startswith(p) for p in pf)


@export
def has_type_suffix(node: ast.AST) -> bool:
    sf = ("_str", "_dict", "_list", "_int", "_float", "_bool")
    return isinstance(node, ast.Name) and any(node.id.endswith(p) for p in sf)


@export
def is_generic_name(node: ast.AST) -> bool:
    generic_names = {"data", "info", "result", "temp"}
    return isinstance(node, ast.Name) and node.id in generic_names


@export
def shadows_builtin(node: ast.AST) -> bool:
    builtin_names = {"list", "dict", "str", "min", "max", "id", "type", "def"}
    return isinstance(node, ast.Name) and node.id in builtin_names


@export
def is_meaningless_name(node: ast.AST) -> bool:
    meaningless = {"thing", "stuff", "xyz"}
    return isinstance(node, ast.Name) and node.id in meaningless


@export
def has_number_in_name(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and any(c.isdigit() for c in node.id)


@export
def is_too_long(node: ast.AST, max_length: int = 30) -> bool:
    return isinstance(node, ast.Name) and len(node.id) > max_length


@export
def is_confusing_abbreviation(node: ast.AST) -> bool:
    abbreviations = {"num", "val", "calc", "arr", "tmp", "usr", "cfg"}
    return isinstance(node, ast.Name) and node.id in abbreviations


@export
def has_bad_plural(node: ast.AST) -> bool:
    bad_plurals = {"datas", "informations", "content_stuff"}
    return isinstance(node, ast.Name) and node.id in bad_plurals


@export
def has_mixed_case(node: ast.AST) -> bool:
    if not isinstance(node, ast.Name):
        return False
    has_camel = any(c.isupper() for c in node.id[1:])
    has_screaming = node.id.isupper() and "_" in node.id
    return has_camel or has_screaming


# File processing


def is_test_context() -> bool:
    test_runners = {"test_", "unittest", "nose2", "pytest"}
    path_parts = sys.argv[0].split(os.sep)
    return any(runner in path for path in path_parts for runner in test_runners)


def read_ignore_file(path: str) -> list[str]:
    with open(path, "r") as f:
        return [line.strip() for line in f]


def filter_ignore_lines(lines: list[str]) -> list[str]:
    return [line for line in lines if not line.startswith("#")]


def load_ignore_paths(path: str = ".inspectignore") -> list[str]:
    return filter_ignore_lines(read_ignore_file(path))


IGNORE_PATHS = [] if is_test_context() else load_ignore_paths()


def filter_dirs(dirs: list[str]) -> list[str]:
    return [d for d in dirs if d not in IGNORE_PATHS]


def process_files(directory: str, file_processor: Callable):
    for root, dirs, files in os.walk(directory):
        dirs[:] = filter_dirs(dirs)
        for file in (f for f in files if f.endswith(".py")):
            file_processor(os.path.join(root, file))
