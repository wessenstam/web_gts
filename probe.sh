#!/usr/bin/env sh

sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g'

# Restart SSH daemon
sudo /etc/init.d/sshd stop
sudo /etc/init.d/sshd -D start
# Script to pull the latest of the web_server into the container on start
mkdir -p /github
cd /github
git clone https://github.com/wessenstam/web_gts

# Start the application
python3 web_gts/probe.py