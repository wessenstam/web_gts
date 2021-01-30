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
db_server=os.environ['db_server']
org = os.environ['org']
bucket = os.environ['bucket']

client = InfluxDBClient(url="http://"+db_server+":8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)


# Get the json data from the probes into a dataframe.
@app.route("/", methods=['POST'])
def input_json():
    json_data=request.get_json()
    if "temp" in json_data:

        temp=json_data['temp']
        name=json_data['name']
        return_payload={'Name': name,'Temp': temp}
        write_api.write(bucket, org, [
            {"measurement": "temp", "tags": {"hostname": name}, "fields": {"temp": float(temp)}}])
    else:
        ping=json_data['ping']
        upload=json_data['upload']
        download=json_data['download']

        return_payload={
                    'ping': ping,
                    'upload': upload,
                    'download': download
        }
        write_api.write(bucket, org, [
            {"measurement": "internet", "tags": {"speed":"speed"}, "fields": {"ping": float(ping),"upload":float(upload),"download":float(download)}}])
    return json.dumps(return_payload)

@app.route("/", methods=['GET'])
def input():

    return " "
# *************************************************************************************************
if __name__ == "main":
    # start the app
    app.run()