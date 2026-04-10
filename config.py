import os
import pathlib
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)


def infer_package(path: str) -> str:
    """Return the package path with dots (.) for a given file path"""

    path_obj = pathlib.Path(path).resolve()
    relative = path_obj.parent.relative_to(project_root)
    return str(relative).replace(os.sep, ".")
