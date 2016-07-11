#!/usr/bin/env bash
set -e
source ./venv/bin/activate
exec env $(cat ./env | xargs) ./gunicorn.sh $@
