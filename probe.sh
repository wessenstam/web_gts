#!/usr/bin/env sh

# Script to pull the latest of the web_server into the container on start
rm -Rf /github
mkdir -p /github
cd /github
git clone https://github.com/wessenstam/web_gts

# Start the application
python3 web_gts/probe.py