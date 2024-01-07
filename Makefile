install:
	@pip install \
	-r requirements.txt \
	-r requirements-dev.txt

compile:
	@rm -f requirements*.txt
	@pip-compile requirements.in
	@pip-compile requirements-dev.in

sync:
	@pip-sync requirements*.txt


.PHONY: default
check: lint format types

.PHONY: lint
lint:
	ruff check --show-source .

.PHONY: format
format:
	ruff format --check .

.PHONY: types
types:
	mypy .
