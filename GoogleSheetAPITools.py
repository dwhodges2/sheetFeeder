from __future__ import print_function
from googleapiclient import discovery
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
import json


# If modifying these scopes, delete the file token.json.
# SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'



def main():
    
    quit()



def getSheetData(sheet,range):

    service = googleAuth()
    spreadsheet_id = sheet
    range_ = range
    # https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
    value_render_option = 'FORMATTED_VALUE'
    # https://developers.google.com/sheets/api/reference/rest/v4/DateTimeRenderOption
    date_time_render_option = 'SERIAL_NUMBER' 
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
    response = request.execute()
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
    theData = getSheetData(sheet,range).get("values")
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
