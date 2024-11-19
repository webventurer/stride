"""
A simple script to find all functions in a Python project that have a docstring
but do not have a blank line immediately following the docstring. We can then
add the blank line manually for better readability.
"""

__package__ = __import__("config").infer_package(__file__)  # Allow rel imports


import click

from . import inspector

filters = [inspector.has_docstring, inspector.docstring_adjacent_to_code]


def find_functions_without_blank_line(file: str):
    block = inspector.CodeBlock.from_file(file)
    if callables := block.find_matching_functions(filters):
        print(f"{file:<40} No blank line after docstring: {callables}")


@click.command()
@click.argument("path", required=True, default=".")
def main(path: str):
    inspector.process_files(path, find_functions_without_blank_line)


if __name__ == "__main__":
    main()
