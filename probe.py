# This script is to probed the to be checked cluster
# 19-03-2020: Willem Essenstam - Initial version 0.1

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
        method="post"

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
    # Set some variables
    pe_ip = server_ip[:len(server_ip) - 2] + "37"
    method=""

    # What is the name of cluster so we can search in the data we send?
    # Use the cluster on the Prism Central for ease of use ;0>
    url = "api/nutanix/v3/clusters/list"
    payload = '{"kind":"cluster","length":500,"offset":0}'
    json_search = get_json_data(pe_ip, url, payload, method, user, passwd, value)
    cluster_name = json_search['entities'][0]['status']['name']
    clus_uuid=json_search['entities'][0]['metadata']['uuid']

# *********************************** Overall performance numbers **************************************
    # What is the current CPU load on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"cluster","entity_ids":["'+str(clus_uuid)+\
              '"],"grouping_attribute":"cluster","group_member_attributes":' \
              '[{"attribute":"hypervisor_cpu_usage_ppm"}]}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    cpu = json_search['group_results'][0]['entity_results'][0]['data'][0]['values'][0]['values'][0]

# *********************************************************************************************************
    # What is the current RAM load on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"cluster","entity_ids":["' + str(clus_uuid) + \
              '"],"grouping_attribute":"cluster","group_member_attributes":' \
              '[{"attribute":"hypervisor_memory_usage_ppm"}]}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    ram = json_search['group_results'][0]['entity_results'][0]['data'][0]['values'][0]['values'][0]

# *********************************************************************************************************
    # What is the amount of IOPS load on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"cluster","entity_ids":["' + str(clus_uuid) + \
              '"],"grouping_attribute":"cluster","group_member_attributes":' \
              '[{"attribute":"controller_num_iops"}]}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    #print(json_search)
    iops = json_search['group_results'][0]['entity_results'][0]['data'][0]['values'][0]['values'][0]

# *********************************************************************************************************
    # What is the amount of Audit lines on the PC?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"audit","filter_criteria":"type_id!=RecoveryPlanJobAudit"}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    # print(json_search)
    audits_nr = json_search['filtered_entity_count']

# *********************************** Overall and detailed information **************************************

    # How many VMs did we have on the PC and what are their names?
    url = "api/nutanix/v3/vms/list"
    payload = '{}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    vm_nr = json_search['metadata']['total_matches']

    # Grabbing the names of the VMs
    # Get the variables defined
    count=0
    vm_name_list=[]
    while count < len(json_search['entities']):
        vm_name=json_search['entities'][count]['status']['name']
        vm_name_list.append(vm_name)
        count+=1
    vm_name_json=json.dumps(vm_name_list)

# *********************************************************************************************************
    # What is the amount of Networks on the PC and what are their names?
    url = "api/nutanix/v3/subnets/list"
    payload = '{}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    netw_nr = json_search['metadata']['total_matches']

    # Grabbing the names of the networks
    count=0
    netw_name_list = []
    while count < len(json_search['entities']):
        netw_name = json_search['entities'][count]['status']['name']
        netw_name_list.append(netw_name)
        count += 1
    netw_name_json = json.dumps(netw_name_list)

# *********************************************************************************************************
    # What is the amount of Networks on the PC and what are their names?
    url = "api/nutanix/v3/subnets/list"
    payload = '{}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    netw_nr = json_search['metadata']['total_matches']

    # Grabbing the names of the networks
    count = 0
    netw_name_list = []
    while count < len(json_search['entities']):
        netw_name = json_search['entities'][count]['status']['name']
        netw_name_list.append(netw_name)
        count += 1
    netw_name_json = json.dumps(netw_name_list)

# *********************************************************************************************************
    # What are the names of BPs?
    url = "api/nutanix/v3/blueprints/list"
    payload = '{}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    # Grabbing the names of the BPs
    count = 0
    bp_name_list = []
    while count < len(json_search['entities']):
        bp_name = json_search['entities'][count]['status']['name']
        bp_name_list.append(bp_name)
        count += 1
    bp_name_json = json.dumps(bp_name_list)

# *********************************************************************************************************
    # What is the amount of Apps, their names and status?
    url = "api/nutanix/v3/apps/list"
    payload = '{}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)

    # Grabbing the names of the Apps
    count = 0
    app_json_list = []
    while count < len(json_search['entities']):
        app_name = json_search['entities'][count]['status']['name']
        app_state = json_search['entities'][count]['status']['state']
        app_json_list.append(app_name)
        app_json_list.append(app_state)
        count += 1
    app_json=json.dumps(app_json_list)

# *********************************************************************************************************
    # What are the Flow policies?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"network_security_rule","query_name":"eb:data-1581845820262","group_member_attributes":[{"attribute":"name"}]}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    # Grabbing the names of the Apps
    count = 0
    flow_json_list = []
    helper_json=json_search['group_results'][0]
    while count < len(helper_json['entity_results']):
        flow_json_list.append(helper_json['entity_results'][count]['data'][0]['values'][0]['values'][0])
        count += 1
    flow_json = json.dumps(flow_json_list)

# *********************************************************************************************************
    # What are the Categories and their values?
    url = "api/nutanix/v3/groups"
    payload = '{"entity_type":"category","query_name":"eb:data:General-1585233140773","grouping_attribute":"abac_category_key","group_sort_attribute":"name","group_attributes":[{"attribute":"name","ancestor_entity_type":"abac_category_key"},{"attribute":"description","ancestor_entity_type":"abac_category_key"}],"group_member_attributes":[{"attribute":"name"},{"attribute":"value"}]}'
    json_search = get_json_data(server_ip, url, payload, method, user, passwd, value)
    # Grabbing the names of the Apps
    count = 0
    count1=0
    count2=0

    cat_list = []
    key_value_list=[]

    # Loop through the group_results from the json
    while count < len(json_search['group_results']):
        # Loop through the entity_results in the returned json
        # Get the name of the category and add to the list
        cat_name = json_search['group_results'][count]['group_summaries']['sum:name']['values'][0]['values'][0]
        cat_list.append(cat_name)

        # Empty the list for the next run
        key_value_list = []

        while count1 < len(json_search['group_results'][count]['entity_results']):
            # Loop through the data int he returned json so we get the values of the category
            while count2 < len(json_search['group_results'][count]['entity_results'][count1]['data']):
                key_name=json_search['group_results'][count]['entity_results'][count1]['data'][count2]['name']
                if key_name=="value":
                    key_value_list.append(json_search['group_results'][count]['entity_results'][count1]['data'][count2]['values'][0]['values'][0])
                count2+=1

            # Reset counter for next loop
            count2 = 0
            count1+=1

        # Merge the cat_values with the list from the inner loops
        cat_list.append(key_value_list)

        # Reset counter for next loop
        count1 = 0
        count+=1

    cat_json=json.dumps(cat_list)

# *************Change the method to get as this is a V1 callset*******************************************************************************
    # What are the share names and their consumed data?
    # This needs to be run against the cluster in the PC
    url = "PrismGateway/services/rest/v1/vfilers/shares"
    payload = ''
    method="get"
    json_search = get_json_data(pe_ip, url, payload, method, user, passwd, value)
    #print(json_search)
    # Grabbing the names of the Apps
    count = 0
    share_json_list = []
    while count < len(json_search['entities']):
        share_name = json_search['entities'][count]['name']
        share_size = json_search['entities'][count]['usageStats']['share_used_bytes']
        share_json_list.append(share_name)
        share_json_list.append(share_size)
        count += 1
    share_json = json.dumps(share_json_list)
    print(share_json)


# *********************************************************************************************************
    # Get all the data into a json file and return that to the main loop.
    json_payload='{"cluster_name":"'+str(cluster_name)+\
                 '","vms":"'+str(vm_nr)+\
                 '","cpu":"'+str(cpu)+\
                 '","ram":"'+str(ram)+\
                 '","iops":"'+str(iops)+\
                 '","netw":"'+str(netw_nr)+\
                 '","ip":"'+str(server_ip)+\
                 '","audits_nr":"'+str(audits_nr)+\
                 '","time":"'+str(datetime.datetime.utcnow())+ \
                 '","vmnames":' + str(vm_name_json) + \
                 ',"netnames":' + str(netw_name_json) + \
                 ',"bpnames":' + str(bp_name_json) + \
                 ',"apps":' + str(app_json) + \
                 ',"share":' + str(share_json) + \
                 ',"flow":' + str(flow_json) + \
                 ',"cat":' + str(cat_json) + \
                 '}'
    #print(json_payload)
    return json_payload

#####################################################################################################################################################################
# __main__
#####################################################################################################################################################################
# Take the SSL warning out of the screen
urllib3.disable_warnings()

# Grab the environmental data we have received when we started the container
server_ip=os.environ['server_ip']
server_prt=os.environ['server_prt']
check_ip=os.environ['check_ip']
user_name=os.environ['user_name']
passwd=os.environ['passwd']
value=''
method='POST'
url="http://"+str(server_ip)+":"+str(server_prt)+"/input"

while True:
    json_return=grab_data(check_ip,user_name,passwd)
    print(get_json_data(server_ip, url, json_return, method, user_name, passwd, value))
    # Sleep 5 minutes before grabbing the next data link
    time.sleep(300)