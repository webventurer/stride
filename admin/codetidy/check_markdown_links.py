"""Check markdown files for broken internal links"""

__package__ = __import__("config").infer_package(__file__)  # Allow rel imports


import os
import re
from pathlib import Path
from typing import Callable
from urllib.parse import unquote

import click


def is_markdown_file(filename: str) -> bool:
    return filename.endswith(".md")


def read_file_content(filepath: Path) -> str:
    return filepath.read_text(encoding="utf-8")


def extract_md_links(content: str) -> list[str]:
    return re.findall(r"\]\(([^)]+\.md)\)", content)


def decode_link(link: str) -> str:
    return unquote(link)


def resolve_target(source: Path, link: str) -> Path:
    return (source.parent / decode_link(link)).resolve()


def link_exists(source: Path, link: str) -> bool:
    return resolve_target(source, link).exists()


def broken_links_in(filepath: Path) -> list[str]:
    content = read_file_content(filepath)
    links = extract_md_links(content)
    return [link for link in links if not link_exists(filepath, link)]


class LinkReport:
    def __init__(self):
        self.files_checked = 0
        self.links_checked = 0
        self.broken_count = 0

    def add_file(self, filepath: str):
        path = Path(filepath)
        self.files_checked += 1
        self.check_links(path, filepath)

    def check_links(self, path: Path, filepath: str):
        links = extract_md_links(read_file_content(path))
        self.links_checked += len(links)
        self.report_broken(path, filepath, links)

    def report_broken(self, path: Path, filepath: str, links: list[str]):
        for link in links:
            if not link_exists(path, link):
                self.broken_count += 1
                print(f"{filepath}: {link}")

    def summary(self) -> str:
        status = "All valid" if self.broken_count == 0 else "BROKEN"
        return f"{self.files_checked} files, {self.links_checked} links, {self.broken_count} broken ({status})"


def process_markdown_files(directory: str, processor: Callable[[str], None]):
    for root, _, files in os.walk(directory):
        for file in files:
            if is_markdown_file(file):
                processor(os.path.join(root, file))


@click.command()
@click.argument("path", required=True, default=".")
@click.option("--summary", "-s", is_flag=True, help="Show summary stats")
def main(path: str, summary: bool):
    """Check markdown files for broken internal links."""

    report = LinkReport()
    process_markdown_files(path, report.add_file)
    if summary:
        print(f"\n{report.summary()}")


if __name__ == "__main__":
    main()
