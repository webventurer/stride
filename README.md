# Python Project Template

You can use this repository as a template when creating a new repository on GitHub, to get my preferred setup for a Python project.

## Choosing an OS

The setup script works on **macOS**, **Ubuntu**, and **Debian**. On **Windows**, use [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install) and follow the Linux instructions below.

Debian is what Ubuntu is based on, so the script works the same way. **Ubuntu** is the easier choice — more beginner-friendly with broader community support and pre-configured defaults. **Debian** favours stability and minimalism, making it a better fit for servers and experienced users.

## Prerequisites

You need brew, direnv, and Python 3 installed before running setup. See [MANUAL-SETUP.md](MANUAL-SETUP.md) for installation instructions.

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

## Further reading

- [DEVELOPMENT.md](DEVELOPMENT.md) — coding conventions (relative imports)
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to add features to this template
- [MANUAL-SETUP.md](MANUAL-SETUP.md) — step-by-step setup without the script
