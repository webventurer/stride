.PHONY: install compile sync update default lint format types test

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

update:
	make compile && make sync


check: lint format types

lint:
	ruff check --show-source .

format:
	ruff format --check .

types:
	pyright .

test:
	sh -c 'pytest tests || ([ $$? = 5 ] && exit 0 || exit $$?)'
