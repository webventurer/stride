__package__ = "admin.codetidy.tests"

import ast
import dataclasses
import sys
import unittest
from typing import Callable

from .. import inspector

this = sys.modules[__name__]


@dataclasses.dataclass
class TestCase:
    filters: list[Callable]
    expected: list[str]
    code: str


func_with_docstring = TestCase(
    filters=[inspector.has_docstring],
    expected=["foo"],
    code='''
def foo():
    """This is a docstring."""
    pass
''',
)

docstring_adjacent_to_code = TestCase(
    filters=[inspector.has_docstring, inspector.docstring_adjacent_to_code],
    expected=["foo"],
    code='''
def foo():
    """This is a docstring."""
    pass
''',
)

class_with_docstring_adjacent_to_code = TestCase(
    filters=[inspector.has_docstring, inspector.docstring_adjacent_to_code],
    expected=["__init__"],
    code='''
class Foo:
    def __init__(self):
        """This is a docstring for __init__"""
        pass
''',
)


class TestCaseMixin:
    """Mixin for test cases that check names against patterns"""

    @property
    def test_names(self) -> list[str]:
        raise NotImplementedError

    @property
    def filter_func(self) -> str:
        raise NotImplementedError

    def check_names(self, test_key: str):
        test_case = getattr(this, test_key)

        block = inspector.CodeBlock(test_case.code)
        poor_names = getattr(block, self.filter_func)(test_case.filters)

        self.assertEqual(test_case.expected, poor_names)  # type: ignore

    def test_all_cases(self):
        if self.__class__.__name__ == "TestCaseMixin":
            return
        for test_name in self.test_names:
            self.check_names(test_name)


class CodeBlockTest(unittest.TestCase):
    def extract_names(self, funcs: list[ast.FunctionDef]) -> list[str]:
        return [f.name for f in funcs]

    def test_fetch_functions(self):
        block = inspector.CodeBlock(func_with_docstring.code)

        self.assertEqual(["foo"], self.extract_names(block.func_defs))

    def test_fetch_functions_in_class(self):
        block = inspector.CodeBlock(class_with_docstring_adjacent_to_code.code)

        self.assertEqual(["__init__"], self.extract_names(block.func_defs))


class DocstringTest(TestCaseMixin, unittest.TestCase):
    @property
    def test_names(self) -> list[str]:
        return [
            "func_with_docstring",
            "docstring_adjacent_to_code",
            "class_with_docstring_adjacent_to_code",
        ]

    @property
    def filter_func(self) -> str:
        return "find_matching_functions"


func_with_no_return_value = TestCase(
    filters=[inspector.callables_with_return_values],
    expected=[],
    code="""
def foo():
    pass
""",
)

func_with_return_value = TestCase(
    filters=[inspector.callables_with_return_values],
    expected=["foo"],
    code="""
def foo():
    return 1
""",
)

func_with_no_return_type_annotation = TestCase(
    filters=[inspector.no_return_type_annotation],
    expected=["foo"],
    code="""
def foo():
    pass
""",
)

func_with_return_type_annotation = TestCase(
    filters=[inspector.no_return_type_annotation],
    expected=[],
    code="""
def foo() -> int:
    return 1
""",
)

func_with_type_ignore_comment = TestCase(
    filters=[inspector.no_type_ignore_comment],
    expected=[],
    code="""
def foo(): # type: ignore
    pass
""",
)


func_with_no_type_ignore_comment = TestCase(
    filters=[inspector.no_type_ignore_comment],
    expected=["foo"],
    code="""
def foo():
    pass
""",
)


class ReturnValuesTest(TestCaseMixin, unittest.TestCase):
    @property
    def test_names(self):
        return [
            "func_with_no_return_value",
            "func_with_return_value",
            "func_with_no_return_type_annotation",
            "func_with_return_type_annotation",
            "func_with_type_ignore_comment",
            "func_with_no_type_ignore_comment",
        ]

    @property
    def filter_func(self) -> str:
        return "find_matching_functions"


# Type prefix/suffix patterns
db_prefix = TestCase(
    filters=[inspector.vars_that_start_with_df],
    expected=["df_data"],
    code="""

def foo() -> int:
    df_data = pd.DataFrame()

    """,
)

type_prefix = TestCase(
    filters=[inspector.has_type_prefix],
    expected=["str_name", "list_items", "dict_config"],
    code="""

def foo() -> int:
    str_name = "foo"
    list_items = []
    dict_config = {}

     """,
)

type_suffix = TestCase(
    filters=[inspector.has_type_suffix],
    expected=["name_str", "items_list", "config_dict"],
    code="""

def foo() -> int:
    name_str = "foo"
    items_list = []
    config_dict = {}

    """,
)

# Generic/meaningless patterns
generic_names = TestCase(
    filters=[inspector.is_generic_name],
    expected=["data", "info", "result", "temp"],
    code="""

def foo() -> int:
    data = 1
    info = {}
    result = []
    temp = 0

""",
)

meaningless_names = TestCase(
    filters=[inspector.is_meaningless_name],
    expected=["thing", "stuff"],
    code="""
def foo() -> int:
     foo = 1
     bar = 2
     thing = 3
     stuff = 4
""",
)

# Built-in conflicts
builtin_shadows = TestCase(
    filters=[inspector.shadows_builtin],
    expected=["list", "dict", "str", "min"],
    code="""
def foo() -> int:
     list = []
     dict = {}
     str = "text"
     min = 0
 """,
)

# Bad naming patterns
numbered_names = TestCase(
    filters=[inspector.has_number_in_name],
    expected=["item1", "string2", "data3"],
    code="""
def foo() -> int:
    item1 = "first"
    string2 = "second"
    data3 = "third"
""",
)

long_names = TestCase(
    filters=[inspector.is_too_long],
    expected=[
        "calculate_total_sum_of_all_user_transactions",
        "get_normalized_customer_address_data",
    ],
    code="""
def foo() -> int:
    calculate_total_sum_of_all_user_transactions = 0
    get_normalized_customer_address_data = ""
""",
)

# Poor naming conventions
abbreviated_names = TestCase(
    filters=[inspector.is_confusing_abbreviation],
    expected=["num", "val", "calc", "arr"],
    code="""
def foo() -> int:
     num = 1
     val = 2
     calc = 3
     arr = []
""",
)

bad_plurals = TestCase(
    filters=[inspector.has_bad_plural],
    expected=["datas", "informations", "content_stuff"],
    code="""
def foo() -> int:
     datas = []
     informations = {}
     content_stuff = ""
""",
)

mixed_case = TestCase(
    filters=[inspector.has_mixed_case],
    expected=["userId", "customerNAME", "DB_Config"],
    code="""
def foo() -> int:
     userId = 1
     customerNAME = "test"
     DB_Config = {}
 """,
)


class VariableNameTest(TestCaseMixin, unittest.TestCase):
    @property
    def type_pattern_names(self) -> list[str]:
        return ["db_prefix", "type_prefix", "type_suffix"]

    @property
    def naming_pattern_names(self) -> list[str]:
        return ["generic_names", "meaningless_names", "builtin_shadows"]

    @property
    def bad_name_pattern_names(self) -> list[str]:
        return [
            "numbered_names",
            "long_names",
            "abbreviated_names",
            "bad_plurals",
            "mixed_case",
        ]

    @property
    def test_names(self) -> list[str]:
        return [
            *self.type_pattern_names,
            *self.naming_pattern_names,
            *self.bad_name_pattern_names,
        ]

    @property
    def filter_func(self) -> str:
        return "find_matching_variables"


if __name__ == "__main__":
    unittest.main()
