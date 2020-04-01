# Python Flask server for attendee look up
# Willem Essenstam - Nutanix - 19 March 2020
# ToDo: Create a more dynamic way of getting the json file
#       - Enumerate a dir, if then not, ask via a webpage.
# ToDo: show the graphs of the clusters
#


from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import json
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from csv import writer
import os.path
import gspread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

# Geting the Forms ready to be used
class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    submit = SubmitField('Find me...')

# Grabbing the initial data from gsheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('json/gts-gsheet-pandas-flask.json',scope)  # Change location as soon as it comes into prod
gc = gspread.authorize(credentials)
wks = gc.open("Sanity Check - EMEA").sheet1  # get the Gsheet
data = wks.get_all_values()
headers = data.pop(0)
# Drop all data in a dataframe
df = pd.DataFrame(data, columns=headers)

# Check to see if we have a csv already. If so delete it.. and clean it with headers.
if os.path.exists("json/usage_vgts.csv"):
    os.remove("json/usage_vgts.csv")

with open('json/usage_vgts.csv', 'a+', newline='') as file:
    writer(file).writerow(['Time','Cluster Name','IP','VMs','VM names','CPU','RAM','IOPS','Audits','Networks','Network Names','Applications','Blueprints','Shares','Flow','Categories','Databases'])

def create_plot():
    df = pd.read_csv("usage_vgts.csv")
    fig=make_subplots(rows=1, cols=2)
    data=[
        go.Bar(x=df['Time'],
            y=df['IOPS']
        )
    ]

    graphJSON=json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

# Load the routes we need for the Flask webpage.
@app.route("/usage")
def output_df_usage_data():
    bar = create_plot()
    return render_template('web_graph.html', plot=bar)


# Get the json data from the probes into a dataframe.
@app.route("/input", methods=['POST'])
def input_json():
    json_data=request.get_json()
    print(json_data)
    cluster_name=json_data['cluster_name']
    vm_nr=json_data['vms']
    cpu=json_data['cpu']
    ram=json_data['ram']
    iops=json_data['iops']
    ip=json_data['ip']
    audits_nr=json_data['audits_nr']
    netw_nr=json_data['netw']
    time=json_data['time']
    vm_names=json_data['vmnames']
    netw_name=json_data['netnames']
    apps=json_data['apps']
    bps=json_data['bpnames']
    share=json_data['share']
    flow=json_data['flow']
    cats=json_data['cat']
    dbs=json_data['dbs']

    # Define the payload, based on the received data.
    return_payload = {'Cluster Name': cluster_name ,
                      'VMs': vm_nr,
                      'CPU': cpu,
                      'RAM': ram,
                      'IOPS': iops,
                      'IP': ip,
                      'Audits': audits_nr,
                      'Networks': netw_nr,
                      'Time': time,
                      'VM Names': vm_names,
                      'Network Names': netw_name,
                      'Applications': apps,
                      'Blueprints': bps,
                      'Shares': share,
                      'Flow': flow,
                      'Categories': cats,
                      'Databases' : dbs
                      }
    #write dat in a csv for later analyses..
    with open('json/usage_vgts.csv', 'a+', newline='') as file:
        writer(file).writerow([time,cluster_name,ip,vm_nr,vm_names,cpu,ram,iops,audits_nr,netw_nr,netw_name,apps,bps,share,flow,cats,dbs])

    # get the data into a new df and append afterwards to a csv file
    return json.dumps(return_payload)

@app.route("/update")
def update_df():
    # Reload the data from the Gsheet
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('json/gts-gsheet-pandas-flask.json', scope)  # Change location as soon as it comes into prod
    gc = gspread.authorize(credentials)
    wks = gc.open("Sanity Check - EMEA").sheet1  # get the Gsheet
    data = wks.get_all_values()
    headers = data.pop(0)
    # Drop all data in a dataframe
    df.update(pd.DataFrame(data, columns=headers))
    return render_template('web_update.html', title='GTS 2020 - EMEA Cluster lookup')

@app.route("/", methods=['GET', 'POST'])
def show_form_data():
    # Show the form
    error=''
    form = LoginForm()
    user_data=''
    #
    if form.validate_on_submit():
        df_user_info = df[df['Email'].str.match(form.email.data.lower())]
        # Change the df into a dict so we can grab the data
        if str(df_user_info):
            user_info = df_user_info.to_dict('records')
            try:
                era_info = df[(df['Domain Name Server'] == user_info[0]['Domain Name Server']) & (df['User Network Name'] == "EraManaged")].to_dict('records')
                # Assigning the user data to variables that we need to show
                user_data = {'attendee_name': user_info[0]['First Name'] + ' ' + user_info[0]['Last Name'],
                             'attendee_id': user_info[0]['Attendee ID'],
                             'cluster_name': user_info[0]['Cluster Name'],
                             'pe_vip': user_info[0]['Prism Element VIP'],
                             'pc_vip': user_info[0]['Prism Central IP'],
                             'user_nw': user_info[0]['User Network Name'],
                             'vlan_id': user_info[0]['VLAN ID'],
                             'gw_ip': user_info[0]['Gateway IP'],
                             'user_nw_sub': user_info[0]['Network Address/Prefix'],
                             'dns': user_info[0]['Domain Name Server'],
                             'dhcp_strt': user_info[0]['DHCP Start'],
                             'dhcp_end': user_info[0]['DHCP End'],
                             'beam_user': user_info[0]['Beam Lab User Name'],
                             'vpn_user': user_info[0]['Lab VPN Username'],
                             'user_nw_era': 'Eramanaged',
                             'vlan_id_era': era_info[0]['VLAN ID'],
                             'gw_ip_era': era_info[0]['Gateway IP'],
                             'user_nw_sub_era': era_info[0]['Network Address/Prefix'],
                             'dns_era': era_info[0]['Domain Name Server'],
                             'dhcp_strt_era': era_info[0]['DHCP Start'],
                             'dhcp_end_era': era_info[0]['DHCP End']
                             }
                # Write data to a csv.
                with open('json/user_access.csv', 'a+', newline='') as file:
                    writer(file).writerow([form.email.data])

                form.email.data=""
            except IndexError:
                error = {'message' : 'Unknown email address', 'email' : form.email.data }
                # Write data to a csv.
                with open('json/user_error.csv', 'a+', newline='') as file:
                    writer(file).writerow([form.email.data])

    # Send the output to the webbrowser
    return render_template('web_form.html', title='GTS 2020 - EMEA Cluster lookup', user=user_data, form=form, error=error)


if __name__ == "main":
    # start the app
    app.run()