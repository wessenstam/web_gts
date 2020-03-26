#!/usr/bin/env sh

# Script to pull the latest of the web_server into the container on start
mkdir -p /github
cd /github
git clone https://github.com/wessenstam/web_gts

ln -s /json /github/web_gts/json

# Start the application
export FLASK_APP=/github/web_gts/app.py
export FLASK_DEBUG=True
flask run --host=0.0.0.0