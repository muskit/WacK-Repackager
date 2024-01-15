#!/bin/sh

cd "$(dirname "$0")"

# if ! [ -d ".venv" ]; then
#   echo ".venv does not exist; creating virtual environment..."
#   python3 -m venv .venv
# fi

# source .venv/bin/activate
# python3 -m pip install -r requirements.txt

python3 src/main.py