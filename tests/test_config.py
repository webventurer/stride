import unittest
import config


class TestInferPackage(unittest.TestCase):
    def setUp(self):
        config.project_root = "/foo/bar"

    def test_absolute_path(self):
        path = "/foo/bar/foo/bar.py"

        result = config.infer_package(path)

        expected = "foo"
        self.assertEqual(result, expected)

    def test_absolute_path_with_relative_section(self):
        path = "/foo/bar/baz/biz/../boz.py"

        result = config.infer_package(path)

        expected = "baz"
        self.assertEqual(result, expected)

    def test_current_directory(self):
        path = "/foo/bar/foo.py"

        result = config.infer_package(path)

        expected = "."
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
