# Use what already exists before building something new (leverage existing mechanisms)

> Before building something, check whether the tools you are building on already do it.

Every tool, library and framework sits on top of capabilities that already exist, from the language's standard library to the database, the operating system and the command-line tools underneath. Before building new functionality, find out what the layer beneath you already provides. Most of the time the capability is there, and the job is to find it and use it properly. A home-made version has to be written, tested, documented and kept working by you, and it meets in production the edge cases the built-in one handled long ago. The built-in one also follows the patterns its users already know.

## The test

Before writing any new code, ask: **am I about to rebuild something that already exists in the systems I'm using?** If the answer might be yes, look first.

- **Read the full reference, not the quick start.** Check the complete list of flags and options, the help output and the recent release notes, and search them for words like "repeatable" or "multiple".
- **Try it instead of assuming a limit.** Does the flag work when given twice? Does the option take a list? Is there a config file?
- **Treat "this feels like it should already exist" as a red flag.** Simple needs, such as formatting a date or passing several values, are the most likely to be built in.

## Worked example: passing several folders to a tool

A tool runs Claude Code inside a container, and its users want to make several folders available in the container's workspace. Claude Code's `--add-dir` flag takes a folder, so the plan is a wrapper that accepts a list of paths and parses it.

```bash
# Before: our own wrapper parses space-separated paths
claude --add-dir /path/to/dir1 /path/to/dir2 /path/to/dir3

# After: the flag is repeatable by design, so pass it once per folder
claude --add-dir /path/to/dir1 --add-dir /path/to/dir2 --add-dir /path/to/dir3
```

Reading the reference showed that `--add-dir` can be given more than once, and that it already handles validation, error cases and edge conditions. No new code was needed, just the flag passed several times. The wrapper and its path parsing were never written, so there was nothing extra to maintain and no bugs from home-made parsing, and the tool follows Claude Code's established patterns instead of inventing its own.

## Where it stops

<mark>Using what exists doesn't rule out building your own; it rules out building it before you have looked.</mark> Build your own only when the existing mechanism genuinely doesn't solve the problem, or has a serious limit on performance, security or compatibility, and the new version gives users enough to be worth looking after for as long as it lives.

Nor does it mean wrapping the native feature in a layer of your own, such as a "folder manager" around `--add-dir`. That is the same mistake in a quieter form: when the built-in feature is enough, pass straight through to it. When nothing suitable exists, [Do the simplest thing that works](simplest-thing-that-works.md) takes over.

## Related

- [Do the simplest thing that works](simplest-thing-that-works.md): the simplest thing is often the one already built.
- [Make code do what a reader expects](least-surprise.md): a standard mechanism surprises readers less than a home-made one.
- [Don't build it until you need it](yagni.md): both principles keep the amount of code you own small.

## Source

Distilled from codefu's `.claude/docs/principles/leverage-existing-mechanisms.md`, which also holds a step-by-step discovery process, a checklist, a table comparing existing and custom solutions, and further examples such as a database's built-in full-text search and git's pre-commit hooks.
