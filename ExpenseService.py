import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
import itertools

from ExpenseSchool import School

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class ExpenseService:

    def __init__(self):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                         'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discovery_url)

        spreadsheet_id = '1TRFpanqxt3jnL4xQ-IoTv5vtBDCF3lEacn63EL2gLxE'

        self.service = service
        self.spreadsheet_id = spreadsheet_id

        """
        {
        'date': ...,
        'desc':  ...
        'value': ...
        'category': ...
        }
        """
        self.data = self.get_all()
        self.tag = self.get_tags()
        self.school_service = School(service, spreadsheet_id)

    def get_all(self):
        """
        Getting all the transactions
        """
        range_name = "transactions!A1:D100000"
        range_values = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        r = []
        for index, row in enumerate(range_values.get('values', [])):
            if index == 0:
                continue
            date = datetime.datetime.strptime(row[0], "%d/%m/%Y")
            value = float(row[2])
            category = row[3] if len(row) >= 4 else None
            r.append({'date': date, 'desc': row[1], 'value': value, 'category': category})
        return r
    '''
    Getting existing tags
    '''
    def get_tags(self):
        range_name = "filters!A1:B100"
        range_values = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        d = {}
        for row in range_values.get('values', []):
            tag = row[0]
            keywords = row[1].split(";")
            for kw in keywords:
                d[kw] = tag
        return d

    def set_tags(self):
        range_name = "transactions!A1:D100000"
        range_values = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        range_tag_name ="transactions!D:D"
        range_tags = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_tag_name).execute()
        keywords = self.tag.keys()
        result = []
        for row, tag in itertools.zip_longest(range_values.get('values', []), range_tags.get('values', [])):
            updated_tag = ''
            if not tag:
                desc = row[1]
                for k in keywords:
                    if k in desc:
                        updated_tag = self.tag[k]
                        break
            else:
                updated_tag = tag[0]
            result.append([updated_tag])
        body = {
            'values': result
        }
        self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range_tag_name,
                                                    valueInputOption="RAW", body=body).execute()

