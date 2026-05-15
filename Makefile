RUN := uv run
export PYTHONPATH := $(CURDIR)

fmt:
	$(RUN) ruff format
	$(RUN) ruff check --fix

lint:
	$(RUN) ruff check

typecheck:
	$(RUN) basedpyright tifonator/

security:
	uv tool run bandit -r tifonator/ -ll -ii

hooks:
	uv tool install pre-commit
	pre-commit install
	pre-commit install --hook-type pre-push

release-patch:
	$(RUN) bump-my-version bump patch

release-minor:
	$(RUN) bump-my-version bump minor

release-major:
	$(RUN) bump-my-version bump major

test:
	$(RUN) python -m pytest tests/unit/

test-cov:
	$(RUN) python -m pytest --cov=tifonator tests/unit/

test-integration:
	$(RUN) python -m pytest tests/integration/

test-integration-cov:
	$(RUN) python -m pytest --cov=tifonator tests/integration/
