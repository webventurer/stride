# Python Project Template

You can use this repository as a template when creating a new repository on GitHub, to get my preferred setup for a Python project.

After creating the new project, there are a few things you'll need to configure.

## Install brew (if you haven't already)

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Or install using the .pkg installer from [here](https://github.com/Homebrew/brew/releases/).

[1] https://brew.sh

## Install direnv

Load/unload environment variables from your .envrc. In this case we use it to set the $PYTHONPATH without resorting to sys.path.insert hacks.

```sh
brew install direnv
```

[1] https://formulae.brew.sh/formula/direnv

## Rename the main package

You'll need to rename the package from "mylib" to something sensible:

```sh
git mv mylib newname
sed -i '' -e 's/mylib/newname/' tests/* .projections.json .github/workflows/python-app.yml .envrc
```

## Choosing the Python version

The version of Python that your project uses is needed by the GitHub Action that runs the tests, and perhaps by your local Python installation tool.

You can create it like this:

```sh
echo 3.12.6 > .python-version
```

## Reviewing the license

The open source MIT license is used by default (see the `LICENSE` file). [Is it appropriate](https://choosealicense.com/) for this project?

If it is, don't forget to set the year and the name of the copyright holder:

```sh
sed -i '' -e "s,<YEAR>,$(date +%Y)," LICENSE
FULL_NAME="$(getent passwd $USER | cut -d : -f 5 | cut -d , -f 1)"
sed -i '' -e "s,<COPYRIGHT HOLDER>,$FULL_NAME," LICENSE
```

If you're on OS X use:

```sh
FULL_NAME="$(bin/osx/getent-passwd.sh $USER | cut -d : -f 5 | cut -d , -f 1)"
```

## Install packages

You need to get everything installed, and that first test running. Start by creating a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Now we can install our development tools:

```sh
pip install --upgrade pip
pip install pip-tools
make install
```

As you add new development or production dependencies (or both), you can run this command to install them:

```sh
make compile && make sync
```

## Run a linter & format your code on check in

Ruff is a standalone package which runs a linter and a formatter over your code, replacing the need for Black, isort or flake8. Althoug you can add the Ruff extension to your VSCode (editor), you can also add it to your .pre-commit-config.yaml to check your code on a git commit.

```sh
pre-commit install
```

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

## Update the README

Now delete all the docs that you've just followed, and write something suitable for your new project!
