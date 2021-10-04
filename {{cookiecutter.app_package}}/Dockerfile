FROM python:3.9-slim-buster as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN buildDeps="build-essential" \
    && apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && apt-get install -y --no-install-recommends $buildDeps \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR /app
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev

COPY ./api ./api

EXPOSE 8000
CMD ["uvicorn", "--reload", "--host=0.0.0.0", "--port=8000", "api.main:app"]
