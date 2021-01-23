# GTS Tools

This Repo exists out of four tools

1. app.py, webinterface for lookup table using a GSheet
2. server.py, server side of the measurement tool
3. probe.py, probe side of the measurement tool
4. Independent InfluxDB for storing measurement data

## app.py

This app is capable of reading a GSheet that holds all the data for a training where attendees have their cluster assignments via a webinterface.

### Usage



## server.py


### Usage


## probe.py


### Usage
When starting the probe.py script, it needs environmental variables. These variables are:
1. server_ip = IP of the server part (server.py) of the measurement tool
2. server_prt= port on which the server is listening (default 5000, FLASK port)
3. check_ip = What is the IP of the Nuutanix CLuster that needs to be checked?
4. user_name = The username for the connection to the Nutanix Cluster (admin)
5. passwd = Corresponding password for the connection ot the Nutanix Cluster

All parameters can be put in an env.list file and be called by **docker run <IMAGE_NAME> --env-file <NAME OF THE ENV FILE>**


## InfluxDB

### Usage