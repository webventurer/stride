#!/usr/bin/env python3
"""
Decide whether a Bash command may run, for block_bare_git_commit.sh.

Reads the hook's JSON on stdin (tool_input.command, cwd). Exits 0 to allow.
Exits 2 with a message on stderr to refuse. Only a commit the command really
runs counts: the words inside a quoted string, a heredoc body or a comment, or
passed to another program, are not a commit. A commit is allowed only when git
positively reports a repository other than the project's for the folder the
commit runs in; anything the guard cannot work out is refused, and a command
whose structure it cannot read has every occurrence of the words treated as a
commit.
"""

import json
import os
import re
import shlex
import subprocess
import sys

STATEMENT_BREAKS = re.compile(r"&&|\|\||[;|&\n()]")
OPERATORS = ("&&", "||", ";", "|", "&", "(", ")")
HEREDOC = re.compile(r"<<(-?)\s*(?:'([^']*)'|\"([^\"]*)\"|(\\?[\w.-]+))")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
LEADING_WORDS = {
    "!",
    "{",
    "then",
    "do",
    "else",
    "elif",
    "if",
    "while",
    "until",
    "time",
    "command",
    "exec",
    "env",
    "sudo",
    "nohup",
}
REDIRECTION = re.compile(r"\d*[<>]")
BARE_REDIRECTION = re.compile(r"\d*(>>?|<)")
BARE_COMMIT = re.compile(r"\bgit\s+commit\b")
GIT_REDIRECT = re.compile(r"GIT_(DIR|WORK_TREE)")
OPTIONS_WITH_VALUE = {
    "-C",
    "-c",
    "--namespace",
    "--exec-path",
    "--config-env",
    "--attr-source",
    "--super-prefix",
    "--git-dir",
    "--work-tree",
}
REDIRECTING_OPTIONS = ("--git-dir", "--work-tree")
SCOPE_MARKERS = re.compile(r"[(){}`|]|(?<!&)&(?!&)")
SUBSTITUTION = re.compile(r"\$\(|`")


def main():
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    start = payload.get("cwd") or os.getcwd()

    refusal = refusal_for(command, start, project_repository())
    if refusal:
        sys.stderr.write(refusal_message(refusal))
        sys.exit(2)


def refusal_for(command, start, project):
    statements = read_statements(command)
    loose = statements is None
    if loose:
        statements = loose_statements(command)
    commits, last_folder = commits_in(statements, start, command, loose)
    if loose and BARE_COMMIT.search(command):
        commits.append(last_folder)
    if not commits:
        return None
    if GIT_REDIRECT.search(command):
        return "redirected"
    for folder in commits:
        placement = placement_of(folder, project)
        if placement:
            return placement
    return None


def read_statements(command):
    statements, words, word = [], [], None
    pending = []
    index = 0
    while index < len(command):
        char = command[index]
        rest = command[index:]
        if rest.startswith("\\\n"):
            index += 2
        elif char == "\\":
            word = (word or "") + command[index + 1 : index + 2]
            index += 2
        elif char == "'":
            end = command.find("'", index + 1)
            if end == -1:
                return None
            word = (word or "") + command[index + 1 : end]
            index = end + 1
        elif char == '"':
            end = closing_quote(command, index + 1)
            if end == -1 or SUBSTITUTION.search(command[index:end]):
                return None
            word = (word or "") + command[index + 1 : end]
            index = end + 1
        elif SUBSTITUTION.match(rest):
            return None
        elif char == "#" and word is None:
            newline = command.find("\n", index)
            index = len(command) if newline == -1 else newline
        elif rest.startswith("<<") and not rest.startswith("<<<"):
            found = HEREDOC.match(rest)
            if not found:
                return None
            quoted = found.group(4) is None or found.group(4).startswith("\\")
            delimiter = found.group(2) or found.group(3) or found.group(4)
            pending.append((delimiter.lstrip("\\"), found.group(1), quoted))
            index += found.end()
        elif char == "&" and (
            command[index - 1 : index] in ("<", ">") or rest.startswith("&>")
        ):
            word = (word or "") + char
            index += 1
        elif char == "\n" or rest.startswith(OPERATORS):
            if word is not None:
                words.append(word)
                word = None
            if words:
                statements.append(words)
                words = []
            index += 1 if char == "\n" else operator_length(rest)
            if char == "\n" and pending:
                after = after_heredocs(command, index, pending)
                if after is None:
                    return None
                index = after
                pending = []
        elif char in " \t":
            if word is not None:
                words.append(word)
                word = None
            index += 1
        else:
            word = (word or "") + char
            index += 1
    if pending:
        return None
    if word is not None:
        words.append(word)
    if words:
        statements.append(words)
    return statements


def operator_length(rest):
    return 2 if rest.startswith(("&&", "||")) else 1


def closing_quote(command, index):
    while index < len(command):
        if command[index] == "\\":
            index += 1
        elif command[index] == '"':
            return index
        index += 1
    return -1


def after_heredocs(command, index, pending):
    for delimiter, dash, quoted in pending:
        body_start = index
        while True:
            if index >= len(command):
                return None
            end = command.find("\n", index)
            end = len(command) if end == -1 else end
            line = command[index:end]
            index = end + 1
            if (line.lstrip("\t") if dash else line) == delimiter:
                break
        if not quoted and SUBSTITUTION.search(command[body_start:index]):
            return None
    return index


def loose_statements(command):
    return [words_in(part) for part in STATEMENT_BREAKS.split(command)]


def words_in(statement):
    try:
        return shlex.split(statement)
    except ValueError:
        return statement.split()


def commits_in(statements, start, command, loose):
    folder = start
    scoped = bool(SCOPE_MARKERS.search(command))
    commits = []
    ran_other = False
    for tokens in statements:
        first = command_index(tokens)
        if first is None:
            continue
        if tokens[first] in ("cd", "pushd", "popd"):
            folder = after_cd(tokens[first:], folder, scoped or ran_other)
            continue
        ran_other = True
        for index in range(len(tokens)) if loose else [first]:
            if os.path.basename(tokens[index]) == "git":
                found = commit_folder(tokens[index + 1 :], folder)
                if found is not False:
                    commits.append(found)
    return commits, folder


def command_index(tokens):
    skip_next = False
    for index, token in enumerate(tokens):
        if skip_next:
            skip_next = False
        elif BARE_REDIRECTION.fullmatch(token):
            skip_next = True
        elif not (
            REDIRECTION.match(token)
            or ASSIGNMENT.match(token)
            or token in LEADING_WORDS
        ):
            return index
    return None


def after_cd(tokens, folder, scoped):
    if scoped or tokens[0] != "cd" or len(tokens) != 2:
        return None
    return join_folder(folder, tokens[1], logical=True)


def commit_folder(arguments, folder):
    index = 0
    redirected = False
    while index < len(arguments) and arguments[index].startswith("-"):
        option = arguments[index]
        if option.startswith(REDIRECTING_OPTIONS):
            redirected = True
        if option == "-C":
            folder = join_folder(
                folder,
                arguments[index + 1] if index + 1 < len(arguments) else "",
            )
        index += 2 if option in OPTIONS_WITH_VALUE else 1
    if index < len(arguments) and arguments[index] == "commit":
        return None if redirected else folder
    return False


def join_folder(folder, target, logical=False):
    target = os.path.expanduser(target)
    if folder is None or not target or re.search(r"[$`*?\[]", target):
        return None
    joined = os.path.join(folder, target)
    return os.path.normpath(joined) if logical else joined


def placement_of(folder, project):
    repository = repository_of(folder)
    if repository is None or project is None:
        return "unknown"
    return "project" if repository == project else None


def project_repository():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    return repository_of(root)


def repository_of(folder):
    if folder is None or not os.path.isdir(folder):
        return None
    environment = {
        k: v for k, v in os.environ.items() if not k.startswith("GIT_")
    }
    result = subprocess.run(
        ["git", "-C", folder, "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        env=environment,
    )
    if result.returncode != 0:
        return None
    return os.path.realpath(os.path.join(folder, result.stdout.strip()))


def refusal_message(reason):
    detail = {
        "project": 'BLOCKED: "git commit" into this project (or one of its worktrees) is not allowed.',
        "unknown": 'BLOCKED: could not work out which repository this "git commit" lands in.',
        "redirected": 'BLOCKED: "git commit" with GIT_DIR or GIT_WORK_TREE set is not allowed.',
    }[reason]
    return (
        f"{detail}\n\n"
        "You MUST invoke the /commit skill using the Skill tool before committing.\n"
        "Do not call do_commit.sh directly — follow the multi-pass workflow first.\n"
        "A commit is only allowed when git shows it lands in a repository outside this project;\n"
        "one whose folder cannot be worked out is refused.\n"
    )


if __name__ == "__main__":
    main()
