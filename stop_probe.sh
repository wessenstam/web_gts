#!/bin/bash

# Get the data from the file

for i in `cat cluster_gts.txt`
do
	var=(${i//,/ })
	docker stop probe-${var[0]}
done