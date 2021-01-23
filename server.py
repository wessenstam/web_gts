# Python Flask server for the probe to have their measurements writen into a InfluxDB for use with Grafana
# Willem Essenstam - Nutanix - 23-01-2021

import json
from flask import *
from datetime import datetime

#from urllib3 import request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

# Get the json data from the probes into a dataframe.
@app.route("/", methods=['POST'])
def input_json():
    json_data=request.get_json()
    print(json_data)
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
    #write data received to the InfluxDB TO BE BUILD!!!!

    print(json.dumps(return_payload))
    # get the data into a new df and append afterwards to a csv file
    return json.dumps(return_payload)

# *************************************************************************************************
if __name__ == "main":
    # start the app
    app.run()