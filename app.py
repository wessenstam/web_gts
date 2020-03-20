# Python Flask server for attendee look up
# Willem Essenstam - Nutanix - 19 March 2020
# ToDo: Create a more dynamic way of getting the json file
#       - Enumerate a dir, if then not, ask via a webpage.
# ToDo: Create a way to use probes (small countainer systems) that will sned data into csv and a DF so we can pull detailed info
# ToDo: Use MathLib to show the trend/progress
# ToDo: Which parameters do we want to see/have


import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    submit = SubmitField('Find me...')


# Grabbing the initial data from gsheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('gts-gsheet-pandas-flask.json',scope)  # Change location as soon as it comes into prod
gc = gspread.authorize(credentials)
wks = gc.open("Sanity Check - EMEA").sheet1  # get the Gsheet
data = wks.get_all_values()
headers = data.pop(0)
# Drop all data in a dataframe
df = pd.DataFrame(data, columns=headers)

# Get the json data from the probes.
@app.route("/input", methods=['POST'])
def input_json():
    json_data=request.get_json()
    cluster_name=json_data['cluster_name']
    nr_vms=json_data['vms']
    cpu=json_data['cpu']
    ram=json_data['ram']
    iops=json_data['iops']
    ip=json_data['ip']
    audits_nr=json_data['audits_nr']
    netw_nr=json_data['netw']
    ip=json_data['ip']
    return "Received the following data:\n\n" \
            +str()+" for the IOPS\n" \
            +str(nr_vms)+" for the amount of VMs\n" \
            +str(cpu)+" for the COU load\n" \
            +str(ram)+" for the amount of used RAM\n" \
            "From PC with IP address: "+str(ip)

@app.route("/update")
def update_df():
    # Reload the data from the Gsheet
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('gts-gsheet-pandas-flask.json',scope)  # Change location as soon as it comes into prod
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
    # If data from the form is valid, we try to get the data..
    if form.validate_on_submit():
        df_user_info = df[df['Email'].str.match(form.email.data)]
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
                             'vpn_user': user_info[0]['Beam Lab User Name'],
                             'user_nw_era': 'Eramanaged',
                             'vlan_id_era': era_info[0]['VLAN ID'],
                             'gw_ip_era': era_info[0]['Gateway IP'],
                             'user_nw_sub_era': era_info[0]['Network Address/Prefix'],
                             'dns_era': era_info[0]['Domain Name Server'],
                             'dhcp_strt_era': era_info[0]['DHCP Start'],
                             'dhcp_end_era': era_info[0]['DHCP End']
                             }
                form.email.data=""
            except IndexError:
                error = {'message' : 'Unknown email address', 'email' : form.email.data }


    # Send the output to the webbrowser
    return render_template('web_form.html', title='GTS 2020 - EMEA Cluster lookup', user=user_data, form=form, error=error)


if __name__ == "main":
    # start the app
    app.run()