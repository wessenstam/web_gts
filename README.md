# GTS Tools

This Repo exists out of five tools

1. server.py, server side of the measurement tool
2. probe.py, probe side of the measurement tool
3. Alertserver, keeps track of the thresholds and warns via Slack that a server has reached the threshold
4. Independent InfluxDB for storing measurement data
5. Independent Grafana for showing dashboards

The order of starting/configuring is NOT the order in which the five tools are mentioned.
Order is:
1. InfluxDB and Grafana and configure
2. Grab the InfluxDB Token, Org and Bucket
3. Change the parameters to reflect these new values and start in order:
    
    1. probe-server (server.py)
    2. probes (probe.py)
    3. alertserver
## server.py
Server side of the probeing solution for the performance of the clusters we manage. Receives data from the probes and stores it into an InfluxDB. Can be run containerized and if needed native on the VM.
### Usage
Run the probing server using the below command where the following parameters must be set:

1. token; token for the connection to the InfluxDB container
2. db_server; the IP address of the InfluxDB server
3. org; the Organuisation as defined in InfluxDB 
4. bucket; the bucket in which the data has to be stored

``docker run -d --rm --name probe-server -e token="INFLUXDB TOKEN" -e db_server="INFLUXDB IP" -e org=<ORG> -e bucket=<BUCKET> -p 5000:5000 wessenstam/gts2021-probe_server``
## probe.py
Probe side that grabs the performance info from the cluster it checks and sends the data to the server side. Checks data every 5 minutes. Every probe will be checking 1 cluster. THis coud lead into many probe containers to be active at one time
### Usage
Make sure the file called ``cluster.txt`` has the correct parameters:
``Cluster Name|IP Addresses for the PE``

When starting the probe.py script, it needs environmental variables. These variables are:
1. server_ip = IP of the server part (server.py) of the measurement tool
2. server_prt= port on which the server is listening (default 5000, FLASK port)
3. check_ip = What is the IP of the Nuutanix CLuster that needs to be checked?
4. user_name = The username for the connection to the Nutanix Cluster (admin)
5. passwd = Corresponding password for the connection ot the Nutanix Cluster

All parameters must be put in a file called **env.list**. This file is being used by the **start_probe.sh** script

``start_probe.sh``

If the probes need to be stopped, run

``stop_probe.sh``

## Alertserver
This alertserver is polling every minute the data in the InfluxDB server and checks to see if there is a Cluster which is crossing the threshold as set in the alertserver.env file (example is in the REPO). This file also holds the IP address and connection token for the InfluxDB. Besides these, also the Slack Token is mentioned in the file. The default parameters, for performance checing, are

1. cpu_load=75 ; 75% CPU load
2. ram_load=80 ; 80% RAM load
3. io_load=10 ; 10ms IO Latency

The values have to cross the threshold for 5 consequtive times before the error is throw and an alert is send to the Slack channel. The alertserver has to be run on the same VM as a docker container.
### Usage
To start the alertserver run:

``docker run -d --rm --name alertserver --env-file alertserver.env wessenstam/alertserver:latest``

## InfluxDB and Grafana
Both InfluxDB and Grafana can be started using the docker-compose.yaml file using:

This will start InfluxDB first and than the Grafana infra. Configuration has to be done afterwards.
### Usage
After installation of docker and docker-compose run:

``docker-compose up -d``

This will start the InfluxDB at port 8086 and Grafana at port 3000. Bith will have to be configured as a clean install if started for the first time.
