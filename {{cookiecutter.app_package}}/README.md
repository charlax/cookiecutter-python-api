# {{cookiecutter.app_package}}

## Prerequisites

Make sure you have those dependencies installed:

- Python 3.9+
- Makefile
- [Poetry](https://python-poetry.org/docs/)
- [Docker](https://docs.docker.com/get-docker/)

## Installation

```bash
make install
```

## Run

```bash
make start
```

### Quick actions

```bash
# Launch db console
make sql

# Run only one test
poetry run pytest app/test_replaceme.py
```

### Credits

This repo was created based on this template: https://github.com/charlax/cookiecutter-python-api
