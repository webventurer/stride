# Contributing

## Add updates to this project

- Create a new branch for each new feature you wish to add e.g. `fly.io` if, for example, you're adding a branch and specific code to roll out to the fly.io cloud service.

- Only add the **new** modules you are interested in. There's no need to keep the modules which are already in `requirements.in` and `requirements-dev.in` in the `main` branch. Only add the new modules (if any) which are relevant to the new branch.

- The same thing applies to this README.md file. You don't need this text as it only applies to the `main` branch to let you know how to add new branches to the project. Only add the relevant section to the README.md for the new branch, otherwise if you make a change to this file in `main`, you will need to sync the changes to the new branch too.

- There's no need to check in `requirements.txt` or `requirements-dev.txt` as they can be generated on the fly with `make update` from the Makefile.

For future research: Is there a way to only add the parts we are interested in without a merge conflict?
