# sheetFeeder
_(Formerly googlesheet_tools, GoogleSheetAPITools)_

Basic Python functions for operations on a Google Sheet. See https://developers.google.com/sheets/api/quickstart/python for more setup details. See API documentation: https://developers.google.com/sheets/api/reference/rest.
This module has been heavily used in Columbia University Libraries' archival data migrations and other activites; a case study involving its use can be found in https://journal.code4lib.org/articles/14871.

## Requirements

* Python 3.4 or higher.
* A Google Apps account.
* Generated `token.json` and `credentials.json` files in project folder (see quickstart instructions below).
* Python packages:
  * `requests`
  * `googleapiclient`
  * `oauth2client`
  * `httplib2`

## Setup

### Python dependencies

It is recommended to create a virtual Python environment (optional but recommended), to isolate project dependencies. See https://docs.python.org/3/library/venv.html.

```
python3 -m venv sfvenv
```

Activate the virtual environment to which dependencies will be added:

```
source sfvenv/bin/activate
```

(To deactivate later use command `deactivate`.)

Dependencies to install into environment:

* `pip install requests`
* `pip install --upgrade google-api-python-client`
* `pip install oauth2client`
* `pip install lxml==4.3.4`

(Note, can use current or other version of `lxml`; 4.3.4 is used for compatibility with Python 3.4.)

### Enable Google Sheets API 

* Go to https://developers.google.com/sheets/api/quickstart/python. Make sure you are signed in as the Google identity you want to enable API access for. 
* Click "Enable the Google Sheets API" button. Download the API credentials as `credentials.json` and put it in the same folder with sheetFeeder.
* Authenticate and grant access.
  * Run `quickstart.py`.
  * The first time you use the API you will be asked to select the Google identity to use (if more than one) and to verify access. Note that you may see a warning that the application is not verified by Google and could pose a security risk. You can go to the "advanced" option and proceed with the QuickStart authentication process from there.
  * Click through to grant read/write permission to your Google Sheets account. If successful you will see a message saying "The authentication flow has completed."

You should now have a file called `token.json` created in your directory. If you want to redo authentication, delete the file and run the script again. Any instance of sheetFeeder will need appropriate `credentials.json` and `token.json` files adjacent.


## Using sheetFeeder

### Classes and Methods

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

#### Additional Subclasses

* `.id`: Returns id part of dataSheet 
* `.range`: Returns range part of dataSheet 
* `.initInfo`: Returns dictionary of metadata about sheet (all tabs, not just the one defined in 2nd arg of dataSheet).
* `.initTabs`: Returns a list of names of tabs in spreadsheet.
* `.url`: Returns public url of sheet of form https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={tab_id}


### Sample Commands

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

This is a work in progress. Comments/suggestions as well as forking very welcome. 

TODO: Compile into package and register with PyPi for easier installation! 