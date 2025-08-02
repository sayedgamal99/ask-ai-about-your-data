#!/bin/sh
uvicorn src.main:app --host 0.0.0.0 --port 5599 &
python -m http.server 9999 --directory src/frontend