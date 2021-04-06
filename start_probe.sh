#!/bin/bash

# Get the data from the file

for i in `cat cluster.txt`
do
	var=(${i//,/ })
	docker run -d --rm --name probe-${var[0]} --env-file ./env.list -e check_ip=${var[1]} wessenstam/probe