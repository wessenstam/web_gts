#!/usr/bin/env bash

# Script to pull the latest of the web_server into the container on start
mkdir -p /github
cd /github
git clone https://github.com/wessenstam/web_gts

# Start the application
export FLASK_APP=/github/web_gts/app.py
FLASK run