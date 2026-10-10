#!/usr/bin/env bash
set -e
python -m backend.seed
uvicorn backend.main:app --reload
