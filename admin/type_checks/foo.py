def a_function(a: int, b: int):
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
