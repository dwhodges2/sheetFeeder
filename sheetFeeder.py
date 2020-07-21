from googleapiclient import discovery
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json
import re
import os.path
import csv
import uuid


# If modifying these scopes, delete the file token.json.
# SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'


# Credentials
my_path = os.path.dirname(__file__)
CREDENTIALS = os.path.join(my_path, 'credentials.json')
TOKEN = os.path.join(my_path, 'token.json')


# Classes and Methods

class dataSheet:
    def __init__(self, id, range):
        self.id = id
        self.range = range
        self.initInfo = getSheetInfo(id)
        self.initTabs = getSheetTabs(id)
        self.url = getSheetURL(id, range)

    def clear(self):
        sheetClear(self.id, self.range)

    def getData(self):
        return getSheetData(self.id, self.range)

    def getDataColumns(self):
        return getSheetDataColumns(self.id, self.range)

    def getDataSeries(self):
        return getSheetDataSeries(self.id, self.range)

    def appendData(self, data):
        return sheetAppend(self.id, self.range, data)

    def lookup(self, search_str, col_search, col_result):
        return sheetLookup(self.id, self.range, search_str, col_search, col_result)

    def matchingRows(self, queries, regex=True, operator='or'):
        return getMatchingRows(self.id, self.range, queries, regex=True, operator='or')

    def importCSV(self, csv, delim=',', quote='NONE'):
        return sheetImportCSV(self.id, self.range, csv, delim, quote)

    # TODO: add validation method.
    # def validate(self,rule):
    #     return sheetValidate(self.id,self.range,rule)


def main():

    # Test some code here if you like.

    the_sheet = dataSheet(
        'd1YzM1dinagfoTUirAoA2hHBfnhSM1PsPt8TkwTT9KlgQ', 'Sheet1!A:Z')
    # print(the_sheet.getData())
    print(the_sheet.getDataColumns())
    # x = the_sheet.matchingRows([['BIBID', '4079432'], ['Title', '.*Humph.*']])
    # print(x)

    quit()


def getSheetInfo(sheet):
    # Return data about a spreadsheet.
    service = googleAuth()
    spreadsheet_id = sheet
    request = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, includeGridData=False)
    response = request.execute()
    return response


def getSheetTabs(sheet):
    # Return a list of tab names for a given sheet.
    service = googleAuth()
    spreadsheet_id = sheet
    request = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, includeGridData=False)
    sheet_data = request.execute()
    the_sheets = sheet_data['sheets']
    the_tabs = []
    for s in the_sheets:
        the_title = s['properties']['title']
        the_tabs.append(the_title)

    return the_tabs


def getSheetData(sheet, range):
    # Return sheet data as list of rows.
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    value_render_option = 'FORMATTED_VALUE'
    # https://developers.google.com/sheets/api/reference/rest/v4/DateTimeRenderOption
    date_time_render_option = 'SERIAL_NUMBER'
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_,
                                                  valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
    the_data = request.execute()
    if "values" in the_data:
        response = the_data["values"]
    else:
        response = []
    return response


def getSheetDataColumns(sheet, range):
    # Return sheet data in columns instead of rows.
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    value_render_option = 'FORMATTED_VALUE'
    # https://developers.google.com/sheets/api/reference/rest/v4/DateTimeRenderOption
    date_time_render_option = 'SERIAL_NUMBER'
    major_dimension = 'COLUMNS'
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_,
                                                  valueRenderOption=value_render_option, majorDimension=major_dimension, dateTimeRenderOption=date_time_render_option)
    the_data = request.execute()
    if "values" in the_data:
        response = the_data["values"]
    else:
        response = []
    return response


def getSheetDataSeries(sheet, range):
    # Get data columns as a dict with key and series.
    # Note that series keys must be unique; if column heads are duplicated a UUID will be appended to key in output.
    the_cols = getSheetDataColumns(sheet, range)
    the_series = {}
    for col in the_cols:
        if len(col) > 0:
            key = col.pop(0)
            if key in the_series:
                key_new = str(key) + '_' + str(uuid.uuid1())
                print("Warning: Duplicate column heading " +
                      str(key) + ". Renaming as " + key_new)
                the_series[key_new] = col
            else:
                the_series[key] = col
    return the_series


def getSheetURL(sheet, range):
    # Pull the title of tab from the range
    tab_name = range.split('!')[0]
    sheet_info = getSheetInfo(sheet)['sheets']
    # Look for sheet matching name and get its ID
    sheet_id = next(i['properties']['sheetId']
                    for i in sheet_info if i['properties']['title'] == tab_name)
    the_url = 'https://docs.google.com/spreadsheets/d/' + \
        str(sheet) + '/edit#gid=' + str(sheet_id)
    return the_url


def sheetClear(sheet, range):
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    clear_values_request_body = {
        # TODO: Add desired entries to the request body.
    }
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id,
                                                    range=range_, body=clear_values_request_body)
    response = request.execute()
    return response


def sheetAppend(sheet, range, data):
    # Append rows to end of detected table.
    # Note: the range is only used to identify a table; values will be appended at the end of table, not at end of range.
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
    value_input_option = 'USER_ENTERED'
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption
    insert_data_option = 'OVERWRITE'
    value_range_body = {'values': data}
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()

    return response


def sheetLookup(sheet, range, search_str, col_search, col_result):
    # Provide sheet, range to search, string to match, the column to match in, and col(s) to return. The col_result can either be an integer or a list of integers, e.g., col_search=0, col_result=[1,2], which will return an array of results. Will return multiple matches in a list.
    # theData = getSheetData(sheet,range).get("values")
    theData = getSheetData(sheet, range)
    theResults = []
    returnCols = []
    if isinstance(col_result, list):
        # print("yes!")
        returnCols = col_result
    else:
        # print("no!")
        returnCols.append(col_result)
    for aRow in theData:
        if aRow[col_search] == search_str:
            # matching result
            theResultSet = []
            for y in returnCols:
                theResultSet.append(aRow[y])
            theResults.append(theResultSet)
    return theResults


def sheetImportCSV(sheet, range, a_csv, delim=',', quote='NONE'):
    # Note: will clear contents of sheet range first.
    #  delim (optional): comma by default, can be pipe, colon, etc.
    #  quote (optional): NONE by default. Can be:
    #       ALL, MINIMAL, NONNUMERIC, NONE
    sheetClear(sheet, range)

    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range

    # Process optional quote handling instruction.
    if quote == 'ALL':
        quote_param = csv.QUOTE_ALL
    elif quote == 'MINIMAL':
        quote_param = csv.QUOTE_MINIMAL
    elif quote == 'NONNUMERIC':
        quote_param = csv.QUOTE_NONNUMERIC
    else:
        quote_param = csv.QUOTE_NONE

    # TODO: Improve ability to pass parameters through to csv dialect options. See https://docs.python.org/3/library/csv.html
    csv.register_dialect('my_dialect', delimiter=delim, quoting=quote_param)

    data = []

    with open(a_csv) as the_csv_data:
        for row in csv.reader(the_csv_data, 'my_dialect'):
            data.append(row)
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
    value_input_option = 'USER_ENTERED'
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption
    insert_data_option = 'OVERWRITE'
    value_range_body = {'values': data}
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
    return response


def batchGetByDataFilter(sheet, datafilters):
    # TODO: Doesn't work. Make this work!
    service = googleAuth()
    spreadsheet_id = sheet

    batch_get_values_by_data_filter_request_body = {
        'value_render_option': 'FORMATTED_VALUE',
        'data_filters': datafilters,
        'date_time_render_option': 'SERIAL_NUMBER'
        # TODO: Add desired entries to the request body.
    }

    request = service.spreadsheets().values().batchGetByDataFilter(
        spreadsheetId=spreadsheet_id, body=batch_get_values_by_data_filter_request_body)
    response = request.execute()

    return response


def getMatchingRows(sheet, range, queries, regex=True, operator='or'):
    # Return a list of rows for which at least one queried column matches regex query. Assumes the first row contains heads.
    # Queries are pairs of column heads and matching strings, e.g., [['ID','123'],['Author','Yeats']]. They are regex by default and can be joined by either 'and' or 'or' logic.

    the_data = getSheetData(sheet, range)
    # use first row as heads
    the_heads = the_data[0]

    the_results = []

    # Generate combined query/target pairs to evaluate in rows.
    # Will look like [ [ query_str1, [col_a,col_b] ], [ query_str2, [col_c,col_d] ] ]
    the_query_pairs = []
    for q in queries:
        # Get list of column indexes for which the head matches query (should usually be just one or none).
        the_col_indexes = [ind for ind,
                           txt in enumerate(the_heads) if txt == q[0]]
        the_query_pairs.append([q[1], the_col_indexes])

    # Process each row testing against all query pairs; result is a list of booleans.
    for row_num, row_data in enumerate(the_data):

        # Adjust list to match row numbers in sheet, starting with 1
        row_num = row_num + 1

        res = []
        for p in the_query_pairs:
            the_col_data = [row_data[c] for c in p[1]]
            if regex == True:
                the_pattern = re.compile(p[0])
                res_list = list(filter(the_pattern.search, the_col_data))
            else:
                res_list = the_col_data.count(p[0])
                # TODO: this works but is clunky, diff type of object.

            if res_list:  # if there is any matches...
                res.append(True)
            else:
                res.append(False)

        # Determine if row matches, depending on and/or junction
        is_hit = False
        if operator == 'and':  # and: all must be True
            if not(False in res):
                is_hit = True

        else:  # default 'or' junction: at least one must be True
            if True in res:
                is_hit = True

        if is_hit == True:

            # Check if the row is alredy in the results, and add if not.
            if not([r["row"] for r in the_results if r["row"] == row_num]):
                the_row_info = {}
                the_row_info["row"] = row_num
                the_row_info["data"] = row_data
                # add the row to the results.
                the_results.append(the_row_info)

    if len(the_results) > 0:
        # Add heads as first row.
        the_results.insert(0, {'row': 1, 'data': the_heads})
        # sort the results by row number.
        the_results = sorted(the_results, key=lambda k: k['row'])

    # Result (if any) will be list of dicts, with head row as first item for further processing if needed.
    # Each dict is of form {'row': <integer>, 'data': [<col1_data>, <col2_data>, etc.]}
    return the_results


def googleAuth():
    # General function to authenticate
    store = file.Storage(TOKEN)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CREDENTIALS, SCOPES)
        creds = tools.run_flow(flow, store)

    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service


if __name__ == '__main__':
    main()
