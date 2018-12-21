# googlesheet_tools

Basic Python functions for operations on a Google Sheet. See https://developers.google.com/sheets/api/quickstart/python for inital setup.
This uses a secrets.py file to hold a sheet ID and default range, but these can be set as vars elsewhere of course.

Sample commands:

* getSheetData(sheet,range) : return the contents from the specified range
* sheetAppend(sheet,range,[[5,"e", 'xx'],[6,"f"],[7,"g"]] ) : add some rows to end of table
* sheetLookup(sheet,range,"b",1,0) : return column 0 for any row that matches string in column 1
* sheetLookup(sheet,range,"b",0,[1,2]) : return columns 1 and 2 for any row that matches string in column 1
* sheetLookup(sheet,range,'4492444',2,3)[0][0] : look for match of string in col 2, return 1st matching result from col 3
