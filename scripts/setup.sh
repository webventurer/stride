#!/bin/bash
set -euo pipefail

# ──────────────────────────────────────────────────────────────
# Setup script for python-template
#
# Automates every step in README.md:
#   1. Check prerequisites (brew, direnv, python3)
#   2. Gather user input (package name, Python version, license)
#   3. Rename package directory to match project name
#   4. Set Python version (install via pyenv if available)
#   5. Update LICENSE with year and author
#   6. Create virtual environment and install dependencies
#   7. Install pre-commit hooks
# ──────────────────────────────────────────────────────────────

# --- Helpers -------------------------------------------------------

red()   { printf "\033[31m%s\033[0m\n" "$1"; }
green() { printf "\033[32m%s\033[0m\n" "$1"; }
bold()  { printf "\033[1m%s\033[0m\n" "$1"; }
dim()   { printf "\033[2m%s\033[0m\n" "$1"; }

bail() { red "Error: $1"; exit 1; }

check_command() {
    command -v "$1" > /dev/null 2>&1 || bail "$1 is not installed. $2"
}

prompt_with_default() {
    local prompt="$1" default="$2" answer
    printf "%s [%s]: " "$prompt" "$default"
    read -r answer
    echo "${answer:-$default}"
}

# --- Prerequisites -------------------------------------------------

bold "Checking prerequisites..."

check_command brew    "Install from https://brew.sh"
check_command direnv  "Run: brew install direnv"
check_command python3 "Install Python 3 first"
check_command git     "Install git first"

if [ ! -d "mylib" ]; then
    bail "mylib/ directory not found — has setup already been run?"
fi

green "All prerequisites found."
echo

# --- Gather user input ---------------------------------------------

bold "Project configuration"
echo

# Package name
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
SANITISED_DEFAULT=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
PROJECT_NAME=$(prompt_with_default "Package name" "$SANITISED_DEFAULT")
PROJECT_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr '-' '_')

if [ "$PROJECT_NAME" = "mylib" ]; then
    bail "Please choose a real project name, not 'mylib'"
fi

# Python version
if command -v pyenv > /dev/null 2>&1; then
    echo
    dim "Available Python versions (pyenv):"
    pyenv versions --bare 2>/dev/null | grep -E '^\d' | tail -5
    echo
    PYENV_LATEST=$(pyenv versions --bare 2>/dev/null | grep -E '^\d+\.\d+\.\d+$' | tail -1)
    DEFAULT_VERSION="${PYENV_LATEST:-$(python3 --version | awk '{print $2}')}"
else
    DEFAULT_VERSION=$(python3 --version | awk '{print $2}')
fi
CHOSEN_VERSION=$(prompt_with_default "Python version" "$DEFAULT_VERSION")

# License holder
if grep -q '<YEAR>' LICENSE 2>/dev/null; then
    if [ "$(uname)" = "Darwin" ]; then
        DEFAULT_NAME=$(bin/osx/getent-passwd.sh "$USER" | cut -d : -f 5 | cut -d , -f 1)
    else
        DEFAULT_NAME=$(getent passwd "$USER" | cut -d : -f 5 | cut -d , -f 1)
    fi
    FULL_NAME=$(prompt_with_default "License holder" "$DEFAULT_NAME")
    UPDATE_LICENSE=true
else
    UPDATE_LICENSE=false
fi

echo
bold "Configuration:"
echo "  Package name:    $PROJECT_NAME"
echo "  Python version:  $CHOSEN_VERSION"
if [ "$UPDATE_LICENSE" = true ]; then
    echo "  License holder:  $FULL_NAME"
fi
echo

printf "Proceed? [Y/n]: "
read -r CONFIRM
if [ "${CONFIRM:-Y}" != "Y" ] && [ "${CONFIRM:-y}" != "y" ]; then
    echo "Aborted."
    exit 0
fi
echo

# --- Rename package ------------------------------------------------

bold "Renaming package to: $PROJECT_NAME"

git mv mylib "$PROJECT_NAME"

FILES_TO_UPDATE=(
    "tests/context.py"
    ".projections.json"
    ".github/workflows/python-app.yml"
    ".envrc"
    "pyproject.toml"
    "pyrightconfig.json"
)

for file in "${FILES_TO_UPDATE[@]}"; do
    [ -f "$file" ] && sed -i '' -e "s/mylib/$PROJECT_NAME/g" "$file"
done

green "Package renamed."
echo

# --- Python version ------------------------------------------------

bold "Setting Python version..."

echo "$CHOSEN_VERSION" > .python-version

# Install via pyenv if available and version is missing
if command -v pyenv > /dev/null 2>&1; then
    if ! pyenv versions --bare 2>/dev/null | grep -qx "$CHOSEN_VERSION"; then
        bold "Installing Python $CHOSEN_VERSION via pyenv..."
        pyenv install "$CHOSEN_VERSION"
    fi
    PYTHON_BIN="$(pyenv prefix "$CHOSEN_VERSION")/bin/python3"
else
    PYTHON_BIN="python3"
fi

green "Set .python-version to $CHOSEN_VERSION."
echo

# --- License -------------------------------------------------------

if [ "$UPDATE_LICENSE" = true ]; then
    bold "Updating LICENSE..."

    YEAR=$(date +%Y)
    sed -i '' -e "s/<YEAR>/$YEAR/" LICENSE
    sed -i '' -e "s/<COPYRIGHT HOLDER>/$FULL_NAME/" LICENSE

    green "LICENSE updated: $YEAR, $FULL_NAME."
    echo
fi

# --- Virtual environment -------------------------------------------

bold "Creating virtual environment..."

"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1
pip install pip-tools > /dev/null 2>&1

green "Virtual environment created."
echo

# --- Install dependencies ------------------------------------------

bold "Installing dependencies..."

make update

green "Dependencies installed."
echo

# --- Pre-commit hooks ----------------------------------------------

bold "Installing pre-commit hooks..."

pre-commit install

green "Pre-commit hooks installed."
echo

# --- Done ----------------------------------------------------------

echo
bold "Setup complete!"
echo
echo "Next steps:"
echo "  1. Run 'direnv allow' to activate the environment"
echo "  2. Run './test' to verify everything works"
echo "  3. Install VS Code extensions: ruff, pylance"
echo "  4. Replace README.md with content for your new project"
echo
