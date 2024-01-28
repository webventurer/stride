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

.PHONY: update
update:
	make compile && make sync


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
	pyright .

.PHONY: test
test:
	sh -c 'pytest tests || ([ $$? = 5 ] && exit 0 || exit $$?)'
