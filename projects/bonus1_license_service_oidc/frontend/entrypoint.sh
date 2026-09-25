#!/bin/sh
set -eu

mkdir -p /app/.streamlit
COOKIE_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
sed "s/^cookie_secret = .*/cookie_secret = \"$COOKIE_SECRET\"/" \
    /run/secrets/streamlit-secrets.toml > /app/.streamlit/secrets.toml

exec uv run streamlit run app.py --server.address=0.0.0.0 --server.port=8501
