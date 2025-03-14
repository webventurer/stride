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
sed -i '' -e 's/mylib/newname/' tests/* .projections.json .github/workflows/python-app.yml .envrc pyproject.toml pyrightconfig.json
```

## Choosing the Python version

The version of Python that your project uses is needed by the GitHub Action that runs the tests, and perhaps by your local Python installation tool.

You can create it like this:

```sh
echo 3.13.2 > .python-version
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
make update
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

## Allow explicit relative imports

Absolute imports are brittle and a little cumbersone to write it out. The sweet spot is about one (max two) layers deep in the hierarchy, so `import foo` or `import foo.bar`. Absolute imports make sense when one package talks to another, however when you're inside a package they are not very useful. After you add some typing, you'll quickly find the first way to save space is to loosen your adherence to absolute imports.

Why not try out `explicit relative imports` like this:

```
from . import foo, bar
```

```
from .foo import baz
```

```
from .. import foo
```

They're easier to work. They're also clear because you're importing from within the same package.

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

## Update the README

Now delete all the docs that you've just followed, and write something suitable for your new project!

```

```
