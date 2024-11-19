# ruff: noqa

from typing import Callable

__all__: list[str] = []


def export(defn: Callable) -> Callable:
    """Add this decorator to any func you wish to import into this namespace"""

    globals()[defn.__name__] = defn
    __all__.append(defn.__name__)
    return defn


# Needed for Pylance type checks or it will complain about missing imports
def __getattr__(name: str) -> Callable:
    if name in globals():
        return globals()[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")


from . import inspector
