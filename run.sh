#!/bin/sh
if [ -d ".venv" ]; then
    . .venv/bin/activate
fi
env `cat .env` gunicorn app:app $@