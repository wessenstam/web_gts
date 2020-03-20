# This script is to check the deployed clusters for the Tech Summits to see if everything has been deployed as it should be.
# 16-02-2020: Willem Essenstam - Initial version 0.1
# Order:
# 1. Check the PE deployment:   a) Eula
#                                b) Pulse
#                                c) Network
#                                d) is AD configured
#                                e) DNS servers
#                                f) NTP servers
# 2. Check PC deployment:       a) DNS servers
#                                b) is AD integrated
#                                c) is Calm enabled
#                                d) is Karbon enabled
#                                e) is Objects enabled
#                                f) has LCM run
#                                g) has flow been enabled
#                                h) do we have the blueprints?
#                                    1. CICD
#                                    2. Citrix
#                                    3. Era deployment
#                                i) Do we have the images uploaded?

import requests
import json
import urllib3
import time
import os
import datetime

#####################################################################################################################################################################
# This function is to get the to see if the initialisation of the cluster has been run (EULA, PULSE, Network)
#####################################################################################################################################################################
def get_json_data(ip_address,get_url,json_data,method,user,passwd,value):
    #Get the URL and compose the command to get the request from the REST API of the cluster
    if not "http:" in get_url:
        url="https://"+ip_address+":9440/"+get_url
    else:
        url=get_url

    header_post = {'Content-type': 'application/json'}
    # if method is not set assume GET
    if method=="":
        method="get"

    # Set the right requests based on GET or POST
    if method=="get":
        try:
            page=requests.get(url,verify=False,auth=(user,passwd),timeout=15)
            page.raise_for_status()
            if value != "":
                json_data = extract_values(json.loads(page.text), value)
            else:
                json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps Error: Something Else", err)
            return err
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)

    else:
        try:
            page=requests.post(url, verify=False, auth=(user, passwd), data=json_data, headers=header_post,timeout=15)
            page.raise_for_status()
            json_data = json.loads(page.text)
            return json_data
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)

#####################################################################################################################################################################
# Data grabs from the server
#####################################################################################################################################################################

def grab_data(server_ip,user,passwd):

    server_ip_pc = server_ip[:len(server_ip) - 2] + "39"
    value = ""
    method = "POST"

    # What is the name of cluster so we can search in the data we send?
    url = "api/nutanix/v3/clusters/list"
    payload = '{"kind":"cluster","length":500,"offset":0}'
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    #print(json_search)
    cluster_name = json_search['entities'][0]['status']['name']
    bp_uuid=json_search['entities'][0]['metadata']['uuid']

    # How many VMs did we have on the PC?
    url = "api/nutanix/v3/vms/list"
    payload = '{}'
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    #print(json_search)
    vm_nr = json_search['metadata']['total_matches']

    # What is the current CPU load on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"cluster","entity_ids":["'+str(bp_uuid)+\
              '"],"grouping_attribute":"cluster","group_member_attributes":' \
              '[{"attribute":"hypervisor_cpu_usage_ppm"}]}'
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    #print(json_search)
    cpu = json_search['group_results'][0]['entity_results'][0]['data'][0]['values'][0]['values'][0]

    # What is the current RAM load on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"cluster","entity_ids":["' + str(bp_uuid) + \
              '"],"grouping_attribute":"cluster","group_member_attributes":' \
              '[{"attribute":"hypervisor_memory_usage_ppm"}]}'
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    #print(json_search)
    ram = json_search['group_results'][0]['entity_results'][0]['data'][0]['values'][0]['values'][0]

    # What is the amount of IOPS load on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"cluster","entity_ids":["' + str(bp_uuid) + \
              '"],"grouping_attribute":"cluster","group_member_attributes":' \
              '[{"attribute":"controller_num_iops"}]}'
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    #print(json_search)
    iops = json_search['group_results'][0]['entity_results'][0]['data'][0]['values'][0]['values'][0]

    # What is the amount of Networks on the PC?
    url = "api/nutanix/v3/subnets/list"
    payload = '{}'
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    #print(json_search)
    netw_nr = json_search['metadata']['total_matches']

    # What is the amount of Audit lines on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"audit","filter_criteria":"type_id!=RecoveryPlanJobAudit"}'
    json_search = get_json_data(server_ip_pc, url, payload, method, user, passwd, value)
    #print(json_search)
    audits_nr = json_search['filtered_entity_count']

    # Get all the data into a json file and return that to the main loop.
    json_payload='{"cluster_name":"'+str(cluster_name)+\
                 '","vms":"'+str(vm_nr)+\
                 '","cpu":"'+str(cpu)+\
                 '","ram":"'+str(ram)+\
                 '","iops":"'+str(iops)+\
                 '","netw":"'+str(netw_nr)+\
                 '","ip":"'+str(server_ip_pc)+\
                 '","audits_nr":"'+str(audits_nr)+\
                 '","time":"'+str(datetime.datetime.utcnow())+\
                 '"}'


    return json_payload

#####################################################################################################################################################################
# __main__
#####################################################################################################################################################################
# Take the SSL warning out of the screen
urllib3.disable_warnings()

# Grab the environmental data we have received when we started the container
server_ip=os.environ['server_ip']
check_ip=os.environ['check_ip']
user_name=os.environ['user_name']
passwd=os.environ['passwd']
value=''
method='POST'
url="http://"+str(server_ip)+"/input"

while True:
    json_return=grab_data(check_ip,user_name,passwd)
    print(json_return)
    #get_json_data(server_ip, url, json_return, method, user_name, passwd, value)
    # Sleep 5 minutes before grabbing the next data link
    time.sleep(300)
