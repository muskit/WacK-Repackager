#!/bin/sh

# if ! [ -d ".venv" ]; then
#   echo ".venv does not exist; creating virtual environment..."
#   python3 -m venv .venv
# fi

# source .venv/bin/activate
# python3 -m pip install -r requirements.txt

cd src
python3 main.py