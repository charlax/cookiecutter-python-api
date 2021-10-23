FROM python:3.9-slim-buster as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl build-essential

# Do not install using pip, otherwise this will mess up the virtual env
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev
# TODO: uvicorn is in the dev dependencies, need a multi-stage build

# TODO: add a way to share cached packages with host

COPY ./api ./api

EXPOSE 8000
CMD ["uvicorn", "--reload", "--host=0.0.0.0", "--port=8000", "api.main:app"]
