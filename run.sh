#!/usr/bin/env bash

if [ ! -d ".venv" ]; then
    uv venv
fi

source .venv/bin/activate
uv sync

uvicorn sync.server:app --host 0.0.0.0 --port 9000
