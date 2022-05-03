FROM python:3.9-slim-buster as python-base

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Add git if you need to install dependencies from source
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl build-essential

# Do not install using pip, otherwise this will mess up the virtual env
RUN curl -sSL https://install.python-poetry.org | python3 -

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache poetry install

COPY ./api ./api

ARG git_sha=""
ARG git_branch=""

LABEL git_sha=${git_sha}
LABEL git_branch=${git_branch}

ENV GIT_SHA=${git_sha}
ENV GIT_BRANCH=${git_branch}

EXPOSE 8000
CMD ["uvicorn", "--reload", "--host=0.0.0.0", "--port=8000", "api.main:app", "--no-access-log"]
