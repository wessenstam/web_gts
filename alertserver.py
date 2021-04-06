# Python InfluxDB GTS2021 alert server for the probe to have their measurements writen into a InfluxDB for use with Grafana
# Willem Essenstam - Nutanix - 28-01-2021

from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import requests
import time
import os


# *******************************************************************************************************************
# Get the InfluxDB Client session up and running
# You can generate a Token from the "Tokens Tab" in the UI
token = os.environ['influxdb_token']
db_server=os.environ['db_server']
org = os.environ['org]
bucket = os.environ['bucket']
client = InfluxDBClient(url="http://"+db_server+":8086", token=token)

# Slack part
slack_token = os.environ['slack_token']
slack_url = "https://hooks.slack.com/services/"+slack_token
slack_channel = '#general'
slack_icon_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuGqps7ZafuzUsViFGIremEL2a3NR0KO0s0RTCMXmzmREJd5m4MA&s'
slack_user_name = 'Performance monitor'

# Rest of the needed variables
# Set the measurements list that needs to be run
checks = ["cpu", "ram", "io_lat"]
counter=0

# Get the alert thresholds from the environment setting
alert_cpu=os.environ['cpu_load']
alert_ram=os.environ['ram_load']
alert_io=os.environ['io_load']

# *******************************************************************************************************************
# Functions
# *******************************************************************************************************************
# Value checker
def check_value(counter,measurement,clustername,alert_threshold):

    # If counter is above the set threshold throw message to Slack
    if measurement == "cpu":
        type_load="CPU Load"
    elif measurement == "ram":
        type_load="RAM Load"
    else:
        type_load = "IO Latency"

    if counter > int(alert_threshold):
        # Build the alert message
        alert_message = "Cluster *"+clustername+"* - "+type_load+" has been more than the set threshold of: " + \
            str(alert_threshold)+" for the last 5 minutes.. Please follow this link: <http://"+db_server+":3000/d/vQwXYMYMz/overall-cluster-dashboard?orgId=1&refresh=1m&from=now-30m&to=now&var-clustername="+clustername+"|*Grafana page for cluster "+clustername+"*>"
        # send the webhook to Slack
        post_message_to_slack(alert_message)



# send the Slack message

def post_message_to_slack(text):
    data = {'text': text}
    data_json = json.dumps(data)
    return requests.post(slack_url, data=data_json)


# *******************************************************************************************************************
# Main calls
# *******************************************************************************************************************
while True:
    # Read the clusters from the Database for the queries to see what we have
    query = ' from(bucket:"'+bucket+'")\
            |> range(start: -5m)\
            |> filter(fn:(r) => r._measurement == "cpu")\
            |> keep(columns: ["clustername"])\
            |> distinct()'

    result = client.query_api().query(org=org, query=query)

    # Create the list of clusters to check in the InfluxDB
    results_clustername = []
    for table in result:
        for record in table.records:
            results_clustername.append(record.values.get("clustername"))

    # run the check per cluster
    for clustername in results_clustername:
        # Run the measurements for the cluster in question
        for measurement in checks:

            # Make sure we query for the correct value
            if measurement == "cpu":
                value_load = "cpu_load"
                alert_threshold = alert_cpu
            elif measurement == "ram":
                value_load = "ram_load"
                alert_threshold = alert_ram
            else:
                value_load = "latency"
                alert_threshold = alert_io

            # Create the query for checking the values
            query = ' from(bucket:"'+bucket+'")\
                    |> range(start: -5m)\
                    |> filter(fn:(r) => r._measurement == "'+measurement+'")\
                    |> filter(fn:(r) => r.clustername == "'+clustername+'")\
                    |> filter(fn:(r) => r._field == "'+value_load+'")'

            result = client.query_api().query(org=org, query=query)
            results = []

            for table in result:
                for record in table.records:
                    results.append(record.get_value())

            # Count how many of the values in the result are above the set threshold
            counter=sum(value > 5 for value in results)

            # Send the information to the check function
            check_value(counter,measurement,clustername,alert_threshold)

            # Reset the counter so we don't get false positives
            counter=0

    # Wait 60 seconds before we rerun the tests
    time.sleep(60)