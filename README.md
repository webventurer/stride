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

## Further reading

- [DEVELOPMENT.md](DEVELOPMENT.md) — coding conventions (relative imports)
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to add features to this template
- [MANUAL-SETUP.md](MANUAL-SETUP.md) — step-by-step setup without the script
