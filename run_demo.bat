@echo off
python -m backend.seed
uvicorn backend.main:app --reload
