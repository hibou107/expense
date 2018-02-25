from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
import itertools
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


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
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class ExpenseService:

    REPORT_LINE = 5

    def __init__(self, service, spreadsheet_id):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.data = []
        self.tag = []

    def get_all(self):
        range_name = "transactions!A1:D100000"
        range_values = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        r = []
        for index, row in enumerate(range_values.get('values', [])):
            print(row)
            if index == 0:
                continue
            date = datetime.datetime.strptime(row[0], "%d/%m/%Y")
            value = float(row[2])
            category = row[3]
            r.append({'date': date, 'desc': row[1], 'value': value, 'category': category})
        self.data = r

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
        self.tag = d

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

    def report(self):
        max_date = max(map(lambda x: x['date'], self.data))
        min_date = max_date - datetime.timedelta(30)
        ll = self.report_range("Last 30 days", min_date, max_date, self.REPORT_LINE)
        this_month = datetime.datetime(max_date.year, max_date.month, 1)
        self.report_range("This month", this_month, max_date, ll + 3)

    def report_range(self, report_name, date_from, date_to, start_line):
        max_date = date_to
        min_date = date_from
        filtered_data = filter(lambda x: min_date <= x['date'] <= max_date, self.data)
        result = {}
        for row in filtered_data:
            category = row['category']
            if category:
                current = result.get(category, 0.0)
                result[category] = current + row['value']

        total_expense = sum(v for v in result.values() if v < 0)
        total_income = sum(v for v in result.values() if v > 0)
        headers = ["Category", "Sum", "percent"]
        r = [[report_name], headers]
        for k, v in result.items():
            r.append([k, v, v / total_income * 100 if v > 0 else v / total_expense * 100])

        max_line = len(r) - 1

        variable_expense = ["shopping", "restaurant", "cash", "trip", "gift"]
        variable_expense_sum = sum(result[v] for v in variable_expense)

        sum_values = [[],
                      ["TOTAL VARIABLE EXPENSE", variable_expense_sum],
                      ["TOTAL EXPENSE", total_expense],
                      ["TOTAL INCOME", total_income]
                      ]

        body = {
            'values': r + sum_values
        }
        last_line = start_line + max_line + len(sum_values)
        range_name = "board!B{}:D{}".format(start_line, last_line)
        self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range_name,
                                                    valueInputOption="RAW", body=body).execute()
        return last_line

    def analyze(self):
        data = reversed(self.data)
        income = 0
        expense = 0
        start_date = None
        for x in data:
            if not start_date:
                start_date = x['date']
            if (start_date - x['date']).days > 30:
                print("end date")
                print(x['date'])
                break
            if x['value'] > 0:
                income = income + x['value']
            else:
                expense = expense + x['value']
        print(income)
        print(expense)


def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1TRFpanqxt3jnL4xQ-IoTv5vtBDCF3lEacn63EL2gLxE'
    service = ExpenseService(service, spreadsheetId)
    service.get_all()
    service.get_tags()
    # service.set_tags()
    service.report()


if __name__ == '__main__':
    main()