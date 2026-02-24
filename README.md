# Python Project Template

You can use this repository as a template when creating a new repository on GitHub, to get my preferred setup for a Python project.

## Prerequisites

You need [brew](https://brew.sh), [direnv](https://formulae.brew.sh/formula/direnv), and Python 3 installed before running setup.

## Getting started

```sh
./scripts/setup.sh
```

The script will:

1. Check prerequisites (brew, direnv, python3, git)
2. Rename the `mylib/` package to match your project name
3. Set the Python version in `.python-version`
4. Update the LICENSE with the current year and your name
5. Create a virtual environment and install dependencies
6. Install pre-commit hooks

After setup, run `direnv allow` to activate the environment and `./test` to verify everything works.

Then replace this README with content for your new project.

## Package naming convention

The convention is for the package directory name to match your project name. If users write `import tempo`, the directory is `tempo/`. Avoid generic names like `app`, `lib`, `core`, or `utils` — they collide with other packages and say nothing about what your code does.

## VS Code plugins

Make sure you install

- ruff
- pylance

Note: Pylance incorporates the Pyright type checker so you only need to install Pylance. When Pylance is installed, the Pyright extension will disable itself.

## VIM plugins

The .projections.json is config for Vim projectionist plugin [1].

This config makes it easy to switch between "alternate" files in the Vim
editor; you can easily jump between a Python module and its test file.

[1] https://github.com/tpope/vim-projectionist.

## Allow explicit relative imports

Absolute imports are brittle and a little cumbersone to write it out. The sweet spot is about one (max two) layers deep in the hierarchy, so `import foo` or `import foo.bar`. Absolute imports make sense when one package talks to another, however when you're inside a package they are not very useful. After you add some typing, you'll quickly find the first way to save space is to loosen your adherence to absolute imports.

Why not try out explicit relative imports like this:

```
from . import foo, bar
```

```
from .foo import baz
```

```
from .. import foo
```

They're easier to work with as they make it clear you're importing from within the same package.

However, if you add explicit relative imports and run these scripts from the command line you'll get an error like this:

```
ImportError: attempted relative import with no known parent package.
```

The reason for the relative import with no known parent package error is because **package** is set to None, and it needs to be set to something!

If you don't want to use `python -m` to specify a module or package as the main program then add this line to the top of your script when you need it:

`__package__ = __import__("config").infer_package(__file__)`

As a general rule, use explicit relative imports when you are working within the same package, and use absolute imports for external packages.

Says David M. Beazley and he's probably right. See Modules and Packages: Live and Let Die! - PyCon 2015 [1].

Relative imports not only leave you free to rename your package later without changing dozens of internal imports, but they can help with circular imports or namespace packages, because they do not send Python "back to the top" to start the search for the next module all over again from the top-level namespace.

[1] https://www.youtube.com/watch?v=0oTh1CXRaQ0

## Add updates to this project

- Create a new branch for each new feature you wish to add e.g. `fly.io` if, for example, you're adding a branch and specific code to roll out to the fly.io cloud service.

- Only add the **new** modules you are interested in. There's no need to keep the modules which are already in `requirements.in` and `requirements-dev.in` in the `main` branch. Only add the new modules (if any) which are relevant to the new branch.

- The same thing applies to this README.md file. You don't need this text as it only applies to the `main` branch to let you know how to add new branches to the project. Only add the relevant section to the README.md for the new branch, otherwise if you make a change to this file in `main`, you will need to sync the changes to the new branch too.

- There's no need to check in `requirements.txt` or `requirements-dev.txt` as they can be generated on the fly with `make update` from the Makefile.

For future research: Is there a way to only add the parts we are interested in without a merge conflict?

Prefer to run each step manually? See [MANUAL-SETUP.md](MANUAL-SETUP.md).
