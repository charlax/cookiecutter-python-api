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

start:  ## Start the app within Docker
	git_sha=$(shell git rev-parse --short HEAD) git_branch=$(shell git rev-parse --abbrev-ref HEAD) ./bin/docker-compose.sh dev up --build --exit-code-from api --remove-orphans
.PHONY: start

start-db:  ## Start only the db
	./bin/docker-compose.sh dev up db -d
.PHONY: start-db

start-local:  ## Start the app locally
	poetry run uvicorn {{cookiecutter.app_package}}.main:app --reload
.PHONY: start-local

python:  ## Start Python shell
	poetry run python
.PHONY: python

##@ DB

db-reset:  ## Reset the DB (local and Docker)
	DOTENV=.env.dev poetry run {{cookiecutter.app_package}}/bin/create_db.py --user dbuser --password dbpassword --name dbname
	DOTENV=.env.devlocal poetry run alembic upgrade head
.PHONY: db-reset

db-test-reset:  ## Reset the test db
	DOTENV=.env.dev poetry run api/bin/create_db.py --user user_test --password password_test --name db_test
	DOTENV=.env.test poetry run alembic upgrade head
.PHONY: db-test-reset

db-migrate:  ## Migrate the dev db
	DOTENV=.env.dev poetry run alembic upgrade head
.PHONY: db-migrate

db-show-migration:  ## Show latest migration
	poetry run alembic upgrade head --sql
.PHONY: db-show-migration

sql:  ## Start SQL shell
	poetry run bin/sql_shell.py
.PHONY: sql

##@ Tests

ci: typecheck lint test ## Run all checks (test, lint, typecheck)
.PHONY: ci

lci: lint-fix ci  ## Autofix then run CI
.PHONY: lci

test: db-test-rest  ## Run tests
	DOTENV=.env.test poetry run pytest .
.PHONY: test

test-cov: db-test-reset ## Run tests with coverage
	DOTENV=.env.test poetry run pytest . --cov-report html
	@echo "Coverage report written to ./.htmlcov/"
	python -m webbrowser -t "file://$(abspath htmlcov)/index.html"
.PHONY: test-cov

lint:  ## Run linting
	poetry run flake8 .
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
