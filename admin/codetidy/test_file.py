"""Some test functions to run the validator scripts against"""


def a_function(a: int, b: int):
    return a + b


def function_returns_none():
    pass


def a_func_with_a_docstring_and_no_space_after(a: int, b: int) -> int:
    """
    This is a docstring.
    """
    return a + b


def a_func_with_a_docstring_and_a_newline_after(a: int, b: int) -> int:
    """This is a docstring"""

    return a + b


class Foo:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def bar(self) -> int:
        return self.a + self.b

    def baz(self):
        return self.a * self.b

    def test_function(self):
        return a_function(self.a, self.b)
