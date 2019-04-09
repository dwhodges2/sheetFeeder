from googleapiclient import discovery
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
import json
import re


# If modifying these scopes, delete the file token.json.
# SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'


def main():

    # Test code here.

    quit()


def getSheetInfo(sheet):
    # Return data about a spreadsheet.
    service = googleAuth()
    spreadsheet_id = sheet
    request = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False)
    response = request.execute()
    return response


def getSheetTabs(sheet):
    # Return a list of tab names for a given sheet.
    service = googleAuth()
    spreadsheet_id = sheet
    request = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False)
    sheet_data = request.execute()
    the_sheets=sheet_data['sheets']
    the_tabs = []
    for s in the_sheets:
        the_title = s['properties']['title']
        the_tabs.append(the_title)

    return the_tabs


def getSheetData(sheet,range):

    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    value_render_option = 'FORMATTED_VALUE'
    # https://developers.google.com/sheets/api/reference/rest/v4/DateTimeRenderOption
    date_time_render_option = 'SERIAL_NUMBER' 
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
    the_data = request.execute()
    response = the_data["values"]
    return response


def sheetClear(sheet,range):
    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    clear_values_request_body = {
    # TODO: Add desired entries to the request body.
    }
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_, body=clear_values_request_body)
    response = request.execute()
    return response




def sheetAppend(sheet,range,data):
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
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    #pprint(response)



def sheetLookup(sheet,range,search_str,col_search,col_result):
    # Provide sheet, range to search, string to match, the column to match in, and col(s) to return. The col_result can either be an integer or a list of integers, e.g., col_search=0, col_result=[1,2], which will return an array of results. Will return multiple matches in a list.
    # theData = getSheetData(sheet,range).get("values")
    theData = getSheetData(sheet,range)
    theResults = []
    returnCols = []
    if isinstance(col_result,list):
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


def batchGetByDataFilter(sheet,datafilters):
    # TODO: Doesn't work. Make this work!
    service = googleAuth()
    spreadsheet_id = sheet

    batch_get_values_by_data_filter_request_body = {
    'value_render_option': 'FORMATTED_VALUE', 
    'data_filters': datafilters, 
    'date_time_render_option': 'SERIAL_NUMBER'  
    # TODO: Add desired entries to the request body.
    }

    request = service.spreadsheets().values().batchGetByDataFilter(spreadsheetId=spreadsheet_id, body=batch_get_values_by_data_filter_request_body)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    return response


def getMatchingRows(sheet,range,queries, regex=True, operator='or'):
    # Return a list of rows for which at least one queried column matches regex query. Assumes the first row contains heads.

    the_data = getSheetData(sheet,range)
    # use first row as heads
    the_heads = the_data[0]

    the_results = []

    # generate combined query/target pairs to evaluate in rows.
    # Will look like [ [ query_str1, [col_a,col_b] ], [ query_str2, [col_c,col_d] ] ]
    the_query_pairs = []
    for q in queries:
    # Get list of column indexes for which the head matches query (should usually be just one or none).
        the_col_indexes = [ind for ind, txt in enumerate(the_heads) if txt == q[0]]
        the_query_pairs.append([q[1], the_col_indexes])

    # Process each row testing against all query pairs; result is a list of booleans.
    for row_num, row_data in enumerate(the_data):

        # Adjust list to match row numbers in sheet, starting with 1
        row_num = row_num + 1

        res = []
        for p in the_query_pairs:
            the_col_data = [row_data[c] for c in p[1]]
            if regex==True:
                the_pattern = re.compile(p[0])
                res_list = list(filter(the_pattern.search, the_col_data))
            else:
                res_list = the_col_data.count(p[0])
                # TODO: this works but is clunky, diff type of object. 

            if res_list: # if there is any matches...
                res.append(True)
            else:
                res.append(False)

        # Determine if row matches, depending on and/or junction
        is_hit = False
        if operator == 'and': # and: all must be True
            if not(False in res):
                is_hit = True

        else: # default 'or' junction: at least one must be True
            if True in res:
                is_hit = True

        if is_hit == True:

            # Check if the row is alredy in the results, and add if not.
            if not( [r["row"] for r in the_results if r["row"] == row_num]):
                the_row_info = {}
                the_row_info["row"] = row_num
                the_row_info["data"] = row_data
                # add the row to the results.
                the_results.append(the_row_info)

    if len(the_results) > 0:
        # Add heads as first row.
        the_results.insert(0, {'row':1, 'data': the_heads})
        # sort the results by row number.
        the_results = sorted(the_results, key=lambda k: k['row'])

    # Result (if any) will be list of dicts, with head row as first item for further processing if needed.
    # Each dict is of form {'row': <integer>, 'data': [<col1_data>, <col2_data>, etc.]}
    return the_results




def googleAuth():
    # General function to authenticate
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)

    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service


if __name__ == '__main__':
    main()
