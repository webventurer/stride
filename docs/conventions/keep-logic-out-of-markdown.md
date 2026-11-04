# Keep logic out of markdown

> A command file says when to run code; the code lives in a script, where a test can run it as it ships.

## The check

Before adding a shell block to a command file, ask:

1. **Does the block branch, loop or check an exit code?** An `if`, a `for`, a `case`, or `|| exit 1` makes it a program
2. **Does it run code in another language?** `python -c` and `node -e` put a program inside a string
3. **Could a test run the exact text the agent runs?** If the only way is to cut the block out of the markdown, it belongs in a script

<mark>Logic in markdown reads like documentation, so nobody thinks to test it.</mark>

## Problem

A step in a command file grows a code block that does real work: a loop over paths, a chain of tests, a few lines of Python that import the Linear client and print a table. It looks like documentation, but it is a program, and it gets none of what a program gets. A test has to cut the block out of the markdown and run a copy, or the block goes untested. `shellcheck` and `ruff` never see it. And the reader who only wants to know when to run the step has to read the whole block to find out.

## The convention

- A shell code block in a command file (tagged `bash` or `sh`, or an untagged block of shell commands) holds only commands to run
- A branch or loop, an exit-code check such as `|| exit 1`, or inline code through `python -c` or `node -e` goes in a script under `.claude/tools/`
- The markdown names the script, says when to run it and what to pass it, and says what its output and exit code mean
- A single command, or a short list of plain commands, stays in the markdown: it is what the reader runs
- A keyword inside a comment or a quoted string isn't logic, and blocks tagged `graphql`, `text` or `json` aren't covered

`test/command-logic.test.mjs` reads every command file stride tracks and fails on a shell block that holds logic.

## Example

### Before

```text
Run this block only after those checks pass:

    jq -e 'type == "object"' "$main_repo/.stride.json" >/dev/null || exit 1
    for settings_repo in "$main_repo" "$worktree"; do
      if git -C "$settings_repo" ls-files --error-unmatch .stride.json …; then
        printf 'Tracked .stride.json in %s; …' "$settings_repo" >&2
        exit 1
      fi
      …
    done
```

### After

```text
Run the settings script only after those checks pass:

    "$main_repo/.claude/tools/share_stride_settings.sh" "$main_repo" "$worktree"

It exits zero once .stride.json in the worktree is a link to the main
checkout's copy, whether it made the link or the link was already
there. For a tracked file it prints "Tracked .stride.json in <path>",
and for a taken path "Existing .stride.json in <path>". On a non-zero
exit, stop before the handoff.
```

`.claude/tools/tests/test_worktree_settings.py` runs that script directly, case by case.

## Why this is useful

- The test runs the code the agent runs, so a regression in it fails the suite
- Linters see the code, so quoting bugs and unset variables are caught
- A reader learns when to run a step from one line instead of seventeen

## When to avoid

- A one-off a person runs by hand, where a script would cost more than it saves; keep it as a plain command and say it is run by hand
- An example inside a document about code, which shows code rather than running it

## Related conventions

- **[Give each responsibility one visible home](give-each-responsibility-one-visible-home.md)**: the markdown owns when a step runs; the script owns what it does

---

_If a test has to cut it out of the markdown to run it, it was never documentation._
