Python Project Template
=======================

You can use this repository as a template when creating a new repository on GitHub, to get my preferred setup for a Python project.

After creating the new project, there are a few things you'll need to configure.

## Rename the main package

You'll need to rename the package from "mylib" to something sensible:

```sh
git mv mylib newname
sed -i'' -e 's/mylib/newname/' tests/* .projections.json
```

## Choosing the Python version

The version of Python that your project uses is needed by the GitHub Action that runs the tests, and perhaps by your local Python installation tool.

You can create it like this:

```sh
echo 3.11.3 > .python-version  # 3.11.3 is just an example
```

## Reviewing the license

The open source MIT license is used by default (see the `LICENSE` file). [Is it appropriate](https://choosealicense.com/) for this project?

If it is, don't forget to set the year and the name of the copyright holder:

```sh
sed -i'' -e "s,<YEAR>,$(date +%Y)," LICENSE
FULL_NAME="$(getent passwd $USER | cut -d : -f 5 | cut -d , -f 1)"
sed -i'' -e "s,<COPYRIGHT HOLDER>,$FULL_NAME," LICENSE
```

## Run the tests locally

You need to get everything installed, and that first test running. Start by creating a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Now we can install our development tools:

```sh
pip install --upgrade pip
pip install pip-tools
pip-sync dev-requirements.txt
```

Once you've got non-development dependencies you can specify them in `requirements.in`, running these commands to install them alongside your development dependencies:

```sh
pip-compile requirements.in
pip-sync requirements.txt dev-requirements.txt
```

## Update the README

Now delete all the docs that you've just followed, and write something suitable for your new project!
