#!/usr/bin/env bash

set -e
source venv/bin/activate
exec gunicorn --bind=unix:/tmp/gunicorn.sock -w 1 brocante.wsgi -t 0