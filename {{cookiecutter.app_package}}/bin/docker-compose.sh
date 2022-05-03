#!/bin/bash

env=$1
shift;

if [[ ! "$env" =~ ^(prod|dev)$ ]]; then
    echo "$env is not a valid env (expected prod or dev)"
    exit 1
fi

args=()

if [[ "$env" = "prod" ]]; then
    args+=(-f docker-compose.prod.yml)
elif [[ "$env" = "dev" ]]; then
    args+=(-f docker-compose.local.yml)
fi

set -x

ENV=$env DOCKER_BUILDKIT=1 COMPOSE_PROJECT_NAME=app docker compose -f docker-compose.yml "${args[@]}" $@
