import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('FILE_WITH_CREDENTIALS.json', scope)
client = gspread.authorize(credentials)

worksheet_name = str(input("Set new worksheet's name: "))
sheet = client.open('EXIST_SHEET_NAME').add_worksheet(worksheet_name, 1000, 26)
sheet.append_row(["Comment1", "Comment2", "Comment3", "Number", "Company", "A", "Name", "e-mail", "Rate", "Min rate",
                  "Max rate", "My rate", "Van", "Length", "Origin", "Date pick", "Time", "Time thru", "Destination",
                  "Date drop", "Time", "Time thru", "Weight", "Commodity"])


def add_load(params):
    """Add new load position to the worksheet"""
    sheet.append_row(params)



