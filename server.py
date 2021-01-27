# Python Flask server for the probe to have their measurements writen into a InfluxDB for use with Grafana
# Willem Essenstam - Nutanix - 23-01-2021

import json
from flask import *
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

# Get the InfluxDB Client session up and running
# You can generate a Token from the "Tokens Tab" in the UI
token = os.environ['token']
org = "TE"
bucket = "gts2021"
client = InfluxDBClient(url="http://127.0.0.1:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Get the json data from the probes into a dataframe.
@app.route("/", methods=['POST'])
def input_json():
    json_data=request.get_json()
    cluster_name=json_data['cluster_name']
    vm_nr=json_data['vms']
    cpu=json_data['cpu']
    ram=json_data['ram']
    io_lat=json_data['io_lat']
    clus_ip=json_data['cl_ip']
    timestamp=datetime.now(tz=None)
    # Define the payload, based on the received data.
    return_payload = {
                      'Cluster Name': cluster_name,
                      'VMs': vm_nr,
                      'CPU': cpu,
                      'RAM': ram,
                      'IO_Lat': io_lat,
                      'Clus_ip': clus_ip,
                      'Timestamp': timestamp
                      }
    #print(return_payload)
    write_api.write(bucket, org, [
        {"measurement": "cpu", "tags": {"clustername": cluster_name,"cluster_ip": clus_ip}, "fields": {"cpu_load": float(cpu)}}])
    write_api.write(bucket, org, [
        {"measurement": "ram", "tags": {"clustername": cluster_name, "cluster_ip": clus_ip}, "fields": {"ram_load": float(ram)}}])
    write_api.write(bucket, org, [
        {"measurement": "io_lat", "tags": {"clustername": cluster_name, "cluster_ip": clus_ip}, "fields": {"latency": float(io_lat)}}])
    write_api.write(bucket, org, [
        {"measurement": "vm_nr", "tags": {"clustername": cluster_name, "cluster_ip": clus_ip}, "fields": {"vms": int(vm_nr)}}])

    return json.dumps(return_payload)
# *************************************************************************************************
if __name__ == "main":
    # start the app
    app.run()