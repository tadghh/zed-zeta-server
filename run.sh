#!/usr/bin/env bash
set -e
uv python install 3.14
if [ ! -d ".venv" ]; then
    uv venv --python 3.14
fi

source .venv/bin/activate
uv sync

uvicorn sync.server:app --host 0.0.0.0 --port 9000
