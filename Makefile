PY_DIRECTORIES=hibob_monitor/ tests/

.PHONY: upgrade-lock-requirements
upgrade-lock-requirements:
	uv sync --upgrade

.PHONY: format
format:
	uv run ruff format ${PY_DIRECTORIES}
	uv run ruff check --fix ${PY_DIRECTORIES}

.PHONY: check-format
check-format:
	uv run ruff check ${PY_DIRECTORIES}
	uv run ruff format --check ${PY_DIRECTORIES}

.PHONY: check-typing
check-typing:
	uv run mypy ${PY_DIRECTORIES}

.PHONY: check-tests
check-tests:
	uv run pytest -v tests/unit/

.PHONY: check-it-tests
check-it-tests:
	uv run pytest -v tests/integration/

.PHONY: checks
checks: check-format check-typing check-tests check-it-tests

.PHONY: clean
clean:
	rm -rf ./.venv/

