#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
if ! python -c 'import streamlit,numpy,pandas,plotly' >/dev/null 2>&1; then
  python -m pip install -r requirements.txt
fi
streamlit run app.py
