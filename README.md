# sheetFeeder
_(Formerly googlesheet_tools, GoogleSheetAPITools)_

Basic Python functions for operations on a Google Sheet. See https://developers.google.com/sheets/api/quickstart/python for inital setup.

## Requirements

* Python 3.
* A Google Apps account.
* Generated token.json and credentials.json files in project folder (see quickstart guide above).
* Python packages installed in environment:
  * googleapiclient (pip install --upgrade google-api-python-client)
  * oauth2client (pip install oauth2client)
  * httplib2 (pip install httplib2)


## Classes and Methods

The core class is dataSheet(id,range). Define a dataSheet to operate on using the id string of a Google Sheet (the long string between "https://docs.google.com/spreadsheets/d/" and "/edit#gid=0" or the like), and a range including a tab name. Example:

```python
from sheetFeeder import dataSheet

my_sheet = dataSheet('1YzM1diaFchenQnchemgogyU2menGxv5Gme','Sheet1!A:Z')
```

This enables several methods on the dataSheet class:

* `.clear()`: Clears content of range.
* `.getData()`: Returns data in form of a list of rows.
* `.getDataColumns()`: Returns data in form of a list of columns.
* `.appendData(some_data)`: Appends rows of data to sheet.  Note: the range is only used to identify a table; values will be appended as rows at the end of table, not at end of range.
* `.lookup(search_str,col_search,col_result)`: Provide string to match, the column to match in, and col(s) to return. The col_result can either be an integer or a list of integers, e.g., col_search=0, col_result=[1,2], which will return an array of results. Will return multiple matches in a list.
* `.importCSV(csv_path,delim=)`: Import a CSV file into a designated sheet range, overwriting what is there. Delimeter is comma by default, but can be any character, e.g., pipe ('|').
* `.matchingRows(self,queries,regex=True,operator='or')`: Return a list of rows for which at least one queried column matches regex query. Assumes the first row contains heads. Queries are pairs of column heads and matching strings, e.g., [['ID','123'],['Author','Yeats']]. They are regex by default and can be joined by either 'and' or 'or' logic.

### Additional Subclasses

* `.id`: Returns id part of dataSheet 
* `.range`: Returns range part of dataSheet 
* `.initInfo`: Returns dictionary of metadata about sheet (all tabs, not just the one defined in 2nd arg of dataSheet).
* `.initTabs`: Returns a list of names of tabs in spreadsheet.
* `.url`: Returns public url of sheet of form https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={tab_id}


## Sample Commands

* `my_sheet.getData()`
  * Result: [['head1', 'head2'],['a', 'b'],['one','two']]
* `my_sheet.appendData[[5,"e", 'xx'],[6,"f"],[7,"g"]]`
  * Result: add some rows.
* `my_sheet.lookup('Smith',2,[3,4])`
  * Result: Return values of columns 3 and 4 for any row where column 2 equals "Smith".
* `my_sheet.matchingRows([['ID', '123'], ['Title', '.*Humph.*']])`
  * Result: Return all rows where ID = 123 *or* Title matches the regex expression `.*Humph.*`. 
* `my_sheet.matchingRows([['ID', '123'], ['Title', '.*Humph.*']], operator='and')`
  * Result: Return all rows where ID = 123 *and* Title matches the regex expression `.*Humph.*`. 
* `my_sheet.clear()`: Empty the contents of dataSheet.
* `my_sheet.importCSV(my_file,delim='|')`: Import contents of pipe-delimited text file into dataSheet.



## Notes

This is a work in progress. 