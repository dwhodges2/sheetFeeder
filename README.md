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
  * `google-api-client`
  * `oauth2client`
  * `httplib2`

## Setup

NEW: Now available as an [installable package from pypi.org](https://pypi.org/project/sheetFeeder/)!

### Installing as a package


1. Create a scratch folder for setup in a convenient location:

  ```bash
  mkdir sheetFeeder_setup
  cd sheetFeeder_setup
  ```

  Download the `sample.py` file from the `sheetFeeder` GitHub and put it in this folder.

2. Set up a virtual environment:

  NOTE: As `sheetFeeder` stores user-specific files for authentication, it is highly recommended to create a virtual Python environment for your project and install `sheetFeeder` and other dependencies into it. See https://docs.python.org/3/library/venv.html.

  Create a new virtual environment in a convenient location with an appropriate name (here called "sfvenv" in the working directory—it can be at any location as long as you note the path for steps below):

  ```bash
  python3 -m venv sfvenv
  ```

  Activate the virtual environment to which dependencies will be added:

  ```bash
  source sfvenv/bin/activate
  ```

3. Install the `sheetFeeder` package into the virtual environment using `pip`:

  ```bash
  pip install sheetFeeder
  ```

  NOTE: This installs several external dependency packages, versions of which you may need to manage in relation to the needs of your project:  

 - `requests`
 - `google-api-python-client`
 - `oauth2client`

  If you get an error saying "invalid command 'bdist_wheel'" you may need to install `wheel` (`pip install wheel`) and repeat.

  Your virtual environment may need additional packages installed of course, depending on your project.

4. Obtain API credentials. To begin using the Google Sheets API you need to obtain credentials specific to your Google account and make them available to `sheetFeeder`. 

- Go to https://developers.google.com/sheets/api/quickstart/python. Make sure you are signed in as the Google identity you want to enable API access for. 
- Click "Enable the Google Sheets API" button. Download the API credentials as `credentials.json`.

5. Place `credentials.json` in the `sheetFeeder` package folder within your virtual environment. The path may vary but it will be something like:

  ```
  sfvenv/lib/python3.6/site-packages/sheetFeeder/
  ```

6. Authenticate and authorize access to your Google account's API (Quickstart).
- Run `sample.py` (`python sample.py`).
- The first time you use the API you will be asked to select the Google identity to use (if more than one are active) and to verify access. Note that you may see a warning that the application is not verified by Google. You can go to the "advanced" option and proceed with the "Quickstart" authentication process from there.
- Click through to grant read/write permission to your Google Sheets account. If successful you will see a message saying "The authentication flow has completed."

7. If successful, a `token.json` file will be created in the same folder as the credentials, and a brief readout of table data will appear. Once the credentials and token are in place, you be able to access sheets via the API without additional steps. You can verify this by running `sample.py` again (you should just get the read-out, without the authentication steps). 

(Note that `credentials.json` and `token.json` can be reused in other virtual environments that have `sheetFeeder` installed without repeating steps 4–7 above.)

### Using as a stand-alone module

If you prefer not to install the module as a package but rather wish to use it as a standalone Python module, you will need to install a few dependencies yourself, either in a virtual environment or in your default Python 3 environment. In this case, download `sheetFeeder.py` to your working directory and import it from your scripts in the same directory.

Dependencies to install into environment:

* `pip install requests`
* `pip install --upgrade google-api-python-client`
* `pip install oauth2client`

To establish connectivity to the API, repeat steps 4 and 6 above. The files `credentials.json` and `token.json` then should reside in the same folder as `sheetFeeder.py`. They can be copied to other projects and will continue to work.

```bash
├── credentials.json
├── sample.py
├── sheetFeeder.py
└── token.json
├── your_script.py
```

### Redoing authorization

If you need to use a different Google account or re-establish fresh credentials, delete the `credentials.json` and `token.json` files above and repeat the steps to create them anew.


## Using sheetFeeder

### The dataSheet() class

The core class is `dataSheet(id,range)`. Define a dataSheet to operate on using the id string of a Google Sheet (the long string between "https://docs.google.com/spreadsheets/d/" and "/edit#gid=0" or the like), and a range including a tab name. Example:

```python
from sheetFeeder import dataSheet

my_sheet = dataSheet('1YzM1diaFchenQnchemgogyU2menGxv5Gme','Sheet1!A:Z')
```

This enables several methods on the dataSheet class, as outlined below.



### Methods

* `clear()`
  * Empty the contents of range, as defined by dataSheet.
  * Example: `my_sheet.clear()`: 
* `getData()`
  * Return the contents of dataSheet in a list of lists.
  * Example: `my_sheet.getData()`
  * Result: [['head1', 'head2'],['a', 'b'],['one', 'two']]
* `getDataColumns()`
  * Return the contents of dataSheet rotated as columns, in a list of lists.
  * Example: `my_sheet.getDataColumns()`
  * Result: [['head1', 'a', 'one'],['head2', 'b','two']]
* `appendData(data)`
  * Append rows of data to sheet.  Note: the range is only used to identify a table; values will be appended as rows at the end of table, not at end of range.
  * Example: `my_sheet.appendData([[5,"e", 'xx'],[6,"f"],[7,"g"]])`
  * Result: add some rows.
* `lookup(search_str,col_search,col_result)`
  * Provide string to match, the column to match in, and col(s) to return. The col_result can either be an integer or a list of integers, e.g., col_search=0, col_result=[1,2], which will return an array of results. Will return multiple matches in a list.
  * Example: `my_sheet.lookup('Smith',2,[3,4])`
  * Result: Return values of columns 3 and 4 for any row where column 2 equals "Smith".
* `matchingRows(queries,regex=True,operator='or')`
  * Return a list of rows for which at least one queried column matches regex query. Assumes the first row contains heads. Queries are pairs of column heads and matching strings, e.g., [['ID','123'],['Author','Yeats']]. They are regex by default and can be joined by either 'and' or 'or' logic.
  * Example: `my_sheet.matchingRows([['ID', '123'], ['Title', '.*Humph.*']])`
  * Result: Return all rows where ID = 123 *or* Title matches the regex expression `.*Humph.*`. 
  * Example: `my_sheet.matchingRows([['ID', '123'], ['Title', '.*Humph.*']], operator='and')`
  * Result: Return all rows where ID = 123 *and* Title matches the regex expression `.*Humph.*`. 
* `importCSV(csv,delim=',',quote='NONE')`
  * Import a CSV file into a designated sheet range, overwriting what is there. Delimeter is comma by default, but can be any character, e.g., pipe ('|').
  * Example: `my_sheet.importCSV(my_file,delim='|')`
  * Result: Import contents of pipe-delimited text file into dataSheet.

### Additional subclasses

* `.id`: Returns id part of dataSheet 
* `.range`: Returns range part of dataSheet 
* `.initInfo`: Returns dictionary of metadata about sheet (all tabs, not just the one defined in 2nd arg of dataSheet).
* `.initTabs`: Returns a list of names of tabs in spreadsheet.
* `.url`: Returns public url of sheet of form https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={tab_id}


## Notes

This is a work in progress. Comments/suggestions as well as forking very welcome. 

