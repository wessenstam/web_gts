#!/usr/bin/env sh

# Start the application
export FLASK_APP=probe_server.py
export FLASK_DEBUG=True
export FLASK_RUN_PORT=5000
flask run --host=0.0.0.0
