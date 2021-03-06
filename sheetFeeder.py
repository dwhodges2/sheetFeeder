from googleapiclient.discovery import build
import googleapiclient.errors
from httplib2 import Http
from oauth2client import file, client, tools, clientsecrets
import re
import os.path
import csv
import uuid
import time
import random
import urllib3
import io


# If modifying these scopes, delete the file token.json.
# SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPES = "https://www.googleapis.com/auth/spreadsheets"


# Credentials
MY_PATH = os.path.dirname(__file__)
CREDENTIALS = os.path.join(MY_PATH, "credentials.json")
TOKEN = os.path.join(MY_PATH, "token.json")


# Globals

# Set defaults for how to handle http errors.
RETRY_DEFAULT = True
INTERVAL_DEFAULT = 0.5
MAX_TRIES_DEFAULT = 5


# Classes and Methods

class sheetFeederError(Exception):
    pass


class dataSheet:
    def __init__(self, id, range):
        self.id = id
        self.range = range
        self.initInfo = getSheetInfo(id)
        self.initTabs = getSheetTabs(id)
        self.url = getSheetURL(id, range)

    def clear(self):
        sheetClear(self.id, self.range)

    def getData(self, filter_queries=None, filter_regex=True, filter_operator="or"):
        return getSheetData(self.id, self.range, filter_queries, filter_regex, filter_operator)

    def getDataColumns(self):
        return getSheetDataColumns(self.id, self.range)

    def getDataSeries(self):
        return getSheetDataSeries(self.id, self.range)

    def appendData(self, data):
        return sheetAppend(self.id, self.range, data)

    def lookup(self, search_str, col_search, col_result):
        return sheetLookup(self.id, self.range, search_str, col_search, col_result)

    def matchingRows(self, queries, regex=True, operator="or"):
        return getMatchingRows(self.id, self.range, queries, regex, operator)

    def importCSV(self, csv, delim=",", quote="NONE"):
        return sheetImportCSV(self.id, self.range, csv, delim, quote)

    # TODO: add validation method.
    # def validate(self,rule):
    #     return sheetValidate(self.id,self.range,rule)


def main():

    # Test some code here if you like.

    # the_sheet = dataSheet(
    #     "19zHqOJt9XUGfrfzAXzOcr4uARgCGbyYiOtoaOCAMP7s", "Sheet1!A:Z")

    # print(the_sheet.getData())

    quit()
###############


def backoff(num, multiplier=2):
    # incremental backoff function for retries
    return (num * multiplier) + (random.randint(0, 1000) / 1000)


def execute_request(
    request, retry=RETRY_DEFAULT, interval=INTERVAL_DEFAULT, max_tries=MAX_TRIES_DEFAULT
):
    attempt = 1
    if not retry:
        max_tries = 1
    while attempt < max_tries:
        try:
            return request.execute()
        except googleapiclient.errors.HttpError as e:
            # Keep retrying until max retries hit.
            print("Warning: API error encountered: " + str(e))
            print("Retrying after " + str(interval) + " sec ...")
            time.sleep(interval)
            interval = backoff(interval)
            attempt += 1
    # Failed all attempts.
    raise sheetFeederError(
        "Could not complete request "
        + str(request)
        + " after "
        + str(attempt)
        + " tries."
    )


def find_matches(array, queries, regex=True, operator="or"):

    # use first row as heads
    the_heads = array[0]
    col_count = len(the_heads)

    the_results = []

    the_query_pairs = []
    for q in queries:
        # Get list of column indexes for which the head matches query (should usually be just one or none).
        the_col_indexes = [ind for ind,
                           txt in enumerate(the_heads) if txt == q[0]]
        the_query_pairs.append([q[1], the_col_indexes])

    # Process each row testing against all query pairs; result is a list of booleans.
    for row_num, row_data in enumerate(array):

        # Adjust list to match row numbers in sheet, starting with 1
        row_num = row_num + 1

        res = []
        for p in the_query_pairs:
            # get cell data for each row in the target columns;
            # when the row has empty cells at end, return empty result
            # if the target col exceeds length of row.
            the_cell_data = [row_data[c]
                             for c in p[1] if (c + 1) <= len(row_data)]
            if regex == True:
                the_pattern = re.compile(p[0])
                res_list = list(filter(the_pattern.search, the_cell_data))
            else:
                res_list = the_cell_data.count(p[0])
                # TODO: this works but is clunky, diff type of object.

            if res_list:  # if there is any matches...
                res.append(True)
            else:
                res.append(False)

        # Determine if row matches, depending on and/or junction
        is_hit = False
        if operator == "and":  # and: all must be True
            if not (False in res):
                is_hit = True

        else:  # default 'or' junction: at least one must be True
            if True in res:
                is_hit = True

        if is_hit == True:

            # Check if the row is alredy in the results, and add if not.
            if not ([r["row"] for r in the_results if r["row"] == row_num]):
                the_row_info = {}
                the_row_info["row"] = row_num
                the_row_info["data"] = row_data
                # add the row to the results.
                the_results.append(the_row_info)

    if len(the_results) > 0:
        # Add heads as first row.
        the_results.insert(0, {"row": 1, "data": the_heads})
        # sort the results by row number.
        the_results = sorted(the_results, key=lambda k: k["row"])

    # Result (if any) will be list of dicts, with head row as first item for further processing if needed.
    # Each dict is of form {'row': <integer>, 'data': [<col1_data>, <col2_data>, etc.]}
    return the_results


def getSheetInfo(sheet):
    # Return data about a spreadsheet.
    service = googleAuth()
    spreadsheet_id = sheet
    request = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, includeGridData=False
    )
    return execute_request(request)


def getSheetTabs(sheet):
    # Return a list of tab names for a given sheet.
    service = googleAuth()
    spreadsheet_id = sheet
    request = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, includeGridData=False
    )
    sheet_data = execute_request(request)
    the_sheets = sheet_data["sheets"]
    the_tabs = []
    for s in the_sheets:
        the_title = s["properties"]["title"]
        the_tabs.append(the_title)

    return the_tabs


def getSheetData(sheet, range, filter_queries=None, filter_regex=True, filter_operator="or"):
    # Return sheet data as list of rows.
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    value_render_option = "FORMATTED_VALUE"
    # https://developers.google.com/sheets/api/reference/rest/v4/DateTimeRenderOption
    date_time_render_option = "SERIAL_NUMBER"
    request = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueRenderOption=value_render_option,
            dateTimeRenderOption=date_time_render_option,
        )
    )
    the_data = execute_request(request)
    if "values" in the_data:
        if filter_queries:
            the_finds = find_matches(
                the_data["values"], queries=filter_queries, regex=filter_regex, operator=filter_operator)
            # Convert find_matches dict output to simple array without heads.
            the_finds.pop(0)
            return [row['data'] for row in the_finds]
        else:
            return the_data["values"]
    else:
        return []


def getSheetDataColumns(sheet, range):
    # Return sheet data in columns instead of rows.
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    value_render_option = "FORMATTED_VALUE"
    # https://developers.google.com/sheets/api/reference/rest/v4/DateTimeRenderOption
    date_time_render_option = "SERIAL_NUMBER"
    major_dimension = "COLUMNS"
    request = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueRenderOption=value_render_option,
            majorDimension=major_dimension,
            dateTimeRenderOption=date_time_render_option,
        )
    )
    the_data = execute_request(request)
    return the_data["values"] if "values" in the_data else []


def getSheetDataSeries(sheet, range):
    # Get data columns as a dict with key and series.
    # Note that series keys must be unique; if column heads are duplicated a UUID will be appended to key in output.
    the_cols = getSheetDataColumns(sheet, range)
    the_series = {}
    for col in the_cols:
        if len(col) > 0:
            key = col.pop(0)
            if key in the_series:
                key_new = str(key) + "_" + str(uuid.uuid1())
                print(
                    "Warning: Duplicate column heading "
                    + str(key)
                    + ". Renaming as "
                    + key_new
                )
                the_series[key_new] = col
            else:
                the_series[key] = col
    return the_series


def getSheetURL(sheet, range):
    # Pull the title of tab from the range
    tab_name = range.split("!")[0]
    sheet_info = getSheetInfo(sheet)["sheets"]
    # Look for sheet matching name and get its ID
    try:
        sheet_id = next(
            i["properties"]["sheetId"]
            for i in sheet_info
            if i["properties"]["title"] == tab_name
        )
        the_url = (
            "https://docs.google.com/spreadsheets/d/"
            + str(sheet)
            + "/edit#gid="
            + str(sheet_id)
        )
    except StopIteration:
        raise sheetFeederError("The tab '" + tab_name +
                               "' could not be found!")
    return the_url


def sheetClear(sheet, range):
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    clear_values_request_body = {
        # TODO: Add desired entries to the request body.
    }
    request = (
        service.spreadsheets()
        .values()
        .clear(
            spreadsheetId=spreadsheet_id, range=range_, body=clear_values_request_body
        )
    )
    return execute_request(request)


def sheetAppend(sheet, range, data):
    # Append rows to end of detecteexecute_request(request)d table.
    # Note: the range is only used to identify a table; values will be appended at the end of table, not at end of range.
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
    value_input_option = "USER_ENTERED"
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption
    insert_data_option = "OVERWRITE"
    value_range_body = {"values": data}
    request = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=value_range_body,
        )
    )
    return execute_request(request)


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
            theResultSet = [aRow[y] for y in returnCols]
            theResults.append(theResultSet)
    return theResults


def sheetImportCSV(sheet, range, a_csv, delim=",", quote="NONE"):
    # CSV can be a file path or URL. A string beginnging with "http"
    # will be treated as a URL and be fetched using urllib3.
    # Otherwise, will look in local file path.
    #  delim (optional): comma by default, can be pipe, colon, etc.
    #  quote (optional): NONE by default. Can be:
    #       ALL, MINIMAL, NONNUMERIC, NONE
    # Note: will clear contents of sheet range first.

    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range

    # Process optional quote handling instruction.
    if quote == "ALL":
        quote_param = csv.QUOTE_ALL
    elif quote == "MINIMAL":
        quote_param = csv.QUOTE_MINIMAL
    elif quote == "NONNUMERIC":
        quote_param = csv.QUOTE_NONNUMERIC
    else:
        quote_param = csv.QUOTE_NONE

    # TODO: Improve ability to pass parameters through to csv dialect options. See https://docs.python.org/3/library/csv.html
    csv.register_dialect("my_dialect", delimiter=delim, quoting=quote_param)

    data = []

    if a_csv.startswith('http'):
        # Read from a URL
        http = urllib3.PoolManager()

        r = http.request('GET', a_csv, preload_content=False)
        r.auto_close = False
        the_csv_data = [l for l in io.TextIOWrapper(r)]
        for row in csv.reader(the_csv_data, "my_dialect"):
            data.append(row)
    else:
        # Read from file
        with open(a_csv) as the_csv_data:
            for row in csv.reader(the_csv_data, "my_dialect"):
                data.append(row)

    sheetClear(sheet, range)

    # https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
    value_input_option = "USER_ENTERED"
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption
    insert_data_option = "OVERWRITE"
    value_range_body = {"values": data}
    request = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=value_range_body,
        )
    )
    return execute_request(request)


def batchGetByDataFilter(sheet, datafilters):
    # TODO: Doesn't work. Make this work!
    service = googleAuth()
    spreadsheet_id = sheet

    batch_get_values_by_data_filter_request_body = {
        "value_render_option": "FORMATTED_VALUE",
        "data_filters": datafilters,
        "date_time_render_option": "SERIAL_NUMBER"
        # TODO: Add desired entries to the request body.
    }

    request = (
        service.spreadsheets()
        .values()
        .batchGetByDataFilter(
            spreadsheetId=spreadsheet_id,
            body=batch_get_values_by_data_filter_request_body,
        )
    )
    return execute_request(request)


def getMatchingRows(sheet, range, queries, regex=True, operator="or"):
    the_data = getSheetData(sheet, range)
    return find_matches(the_data, queries, regex=True, operator="or")


def getMatchingRows0(sheet, range, queries, regex=True, operator="or"):
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
        if operator == "and":  # and: all must be True
            if not (False in res):
                is_hit = True

        else:  # default 'or' junction: at least one must be True
            if True in res:
                is_hit = True

        if is_hit == True:

            # Check if the row is alredy in the results, and add if not.
            if not ([r["row"] for r in the_results if r["row"] == row_num]):
                the_row_info = {}
                the_row_info["row"] = row_num
                the_row_info["data"] = row_data
                # add the row to the results.
                the_results.append(the_row_info)

    if len(the_results) > 0:
        # Add heads as first row.
        the_results.insert(0, {"row": 1, "data": the_heads})
        # sort the results by row number.
        the_results = sorted(the_results, key=lambda k: k["row"])

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

    return build("sheets", "v4", http=creds.authorize(Http()))


if __name__ == "__main__":
    main()
