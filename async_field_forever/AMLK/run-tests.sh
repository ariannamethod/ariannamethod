#!/usr/bin/env bash
set -e

flake8 .
black --check .
pytest "$@"
