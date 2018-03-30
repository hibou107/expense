import datetime

import tools


class School:
    def __init__(self, service, spreadsheet_id):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.holidays = self.get_public_holidays()
        self.school_holidays = self.get_school_holidays()

    def get_public_holidays(self):
        range_name = "school_data!U2:U"
        range_values = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        r = []
        for row in range_values.get('values', []):
            date = datetime.datetime.strptime(row[0], "%d/%m/%Y")
            r.append(date)
        return r

    def get_school_holidays(self):
        range_name = "school_data!X2:X"
        range_values = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        values = [datetime.datetime.strptime(x[0], "%d/%m/%Y") for x in range_values.get('values', [])]
        grouped = tools.chunks(values, 2)
        r = list(grouped)
        return r

    def is_holidays(self, date):
        for start, end in self.school_holidays:
            if start <= date <= end:
                return True
        return False

    def compute_date(self, date):
        is_holiday = self.is_holidays(date)
        is_weekend = True if date.weekday() >= 5 else False
        is_holiday_at_school = is_holiday and (not is_weekend)
        is_normal_day_at_school = not(is_holiday or is_weekend)
        result = {}
        if is_holiday_at_school:
            result['matin'] = False
            result['restaurant'] = False
            result['soiree'] = False
            result['vacance'] = True
            result['demi_journee'] = False
        elif is_normal_day_at_school:
            if date.weekday() == 2:
                result['matin'] = True
                result['restaurant'] = False
                result['soiree'] = False
                result['vacance'] = False
                result['demi_journee'] = True
            else:
                result['matin'] = True
                result['restaurant'] = True
                result['soiree'] = True
                result['vacance'] = False
                result['demi_journee'] = False
        else:
            result['matin'] = False
            result['restaurant'] = False
            result['soiree'] = False
            result['vacance'] = False
            result['demi_journee'] = False
        return result

    def compute_all(self):
        range_name = "school_data!A2:F"
        range_values = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        r = []
        for row in range_values.get('values', []):
            date = datetime.datetime.strptime(row[0], "%d/%m/%Y")
            if len(row) > 1:
                r.append(row)
            else:
                by_date = self.compute_date(date)
                r.append([row[0], by_date['matin'], by_date['restaurant'], by_date['soiree'],
                          by_date['vacance'], by_date['demi_journee']])
        body = {
            'values': r
        }
        self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range_name,
                                                    valueInputOption="RAW", body=body).execute()
