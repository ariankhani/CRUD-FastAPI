#!/bin/sh
exec python -m uvicorn  --host 0.0.0.0 --port 8000 app.main:app --reload