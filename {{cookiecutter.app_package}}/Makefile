SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

install:  ## Install the app locally
	poetry install
.PHONY: install

reset-db:  ## Reset the db
	poetry run python bin/setup_db.py
.PHONY: reset-db

start:  ## Start the app locally
	poetry run uvicorn {{cookiecutter.app_package}}.main:app --reload
.PHONY: start

python:  ## Start Python shell
	poetry run python
.PHONY: python

sql:  ## Start SQL shell
	poetry run bin/sql_shell.py
.PHONY: sql

##@ Tests

ci: typecheck lint test ## Run all checks (test, lint, typecheck)
.PHONY: ci

lci: lint-fix ci  ## Autofix then run CI
.PHONY: lci

test:  ## Run tests
	DOTENV=.env.test poetry run pytest .
.PHONY: test

test-cov:  ## Run tests with coverage
	DOTENV=.env.test poetry run pytest . --cov-report html
	@echo "Coverage report written to ./.htmlcov/"
	python -m webbrowser -t "file://$(abspath htmlcov)/index.html"
.PHONY: test

lint:  ## Run linting
	poetry run black --check .
	poetry run isort -c .
	poetry run flake8 .
	poetry run pydocstyle .
.PHONY: lint

lint-fix:  ## Run autoformatters
	poetry run black .
	poetry run isort .
.PHONY: lint-fix

typecheck:  ## Run typechecking
	poetry run mypy --show-error-codes --pretty .
.PHONY: typecheck

.DEFAULT_GOAL := help
help: Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[\/\.a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
