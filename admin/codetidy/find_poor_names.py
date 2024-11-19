"""Find poor variable name patterns in the codebase"""

__package__ = __import__("config").infer_package(__file__)  # Allow rel imports


import click

from . import inspector

filters = [
    inspector.vars_that_start_with_df,
    inspector.has_type_prefix,
    inspector.has_type_suffix,
    inspector.shadows_builtin,
    inspector.is_meaningless_name,
    inspector.has_bad_plural,
]

filters_for_later = [
    inspector.is_generic_name,
    inspector.has_number_in_name,
    inspector.is_too_long,
    inspector.is_confusing_abbreviation,
]


def find_poor_names(file: str):
    block = inspector.CodeBlock.from_file(file)
    for name in block.find_matching_variables(filters):
        print(f"{file:<60} Poor name: {name}")


@click.command()
@click.argument("path", required=True, default=".")
def main(path: str):
    inspector.process_files(path, find_poor_names)


if __name__ == "__main__":
    main()
