# sheetFeeder
_(Formerly googlesheet_tools, GoogleSheetAPITools)_

Basic Python functions for operations on a Google Sheet. See https://developers.google.com/sheets/api/quickstart/python for more setup details. See API documentation: https://developers.google.com/sheets/api/reference/rest.
This module has been heavily used in Columbia University Libraries' archival data migrations and other activites; a case study involving its use can be found in https://journal.code4lib.org/articles/14871.

## Requirements

* Python 3.4 or higher.
* A Google Apps account.
* Python packages:
  * `requests`
  * `google-api-python-client`
  * `oauth2client`
  * `httplib2`

## Setup

This library is bundled as an [installable package from pypi.org](https://pypi.org/project/sheetFeeder/).

1. Installation

    There are several ways to use `sheetFeeder`, depending how you want to manage dependencies like authentication credentials. Three options are described here: system installation, installation in a virtual environment, and stand-alone module use. For testing and portability, the virtual-environment option is most recommended.

    #### A. System installation

    To install into your default Python 3 environment, use the version of pip assocated with that environment (usually `pip3`).

    ```
    pip3 install sheetFeeder
    ```

    NOTE: You may need to prepend `sudo` to the above to install at the system level. If you do not have `su` permissions to install Python packages, you may do better to use a virtual environment (see below).

    You will need to note the location where the package is installed for step 2 below. It will be something like:

    ```
    /usr/local/lib/python3.7/site-packages/sheetFeeder
    ```

    #### B. Virtual environment installation

    The command `venv` is used to create a virtual Python environment. See https://docs.python.org/3/library/venv.html. (Commands below are for a bash shell in Linux or Mac OS; your use of venv may vary,see the venv documentation linked above.)

    * Use `venv` to create a new virtual Python 3 environment in a convenient location with an appropriate name such as "sfvenv":

        ```
        python3 -m venv sfvenv
        ```

    * Activate the virtual environment to which dependencies will be added:

        ```
        source sfvenv/bin/activate
        ```

        (To deactivate the environment use the command `deactivate`.)

    * Install `sheetFeeder` using pip:

        ```
        pip install sheetFeeder
        ```

        This will install into the activated virtual environment and only be available while the environment is active. Note the location where the library was installed for step 2 below. It will be something like:

        ```
        sfvenv/lib/python3.6/site-packages/sheetFeeder/
        ```

    #### C. Stand-alone installation

    If you prefer not to install the module as a package but rather wish to use it as a standalone Python module, you will need to install a few dependencies yourself, either in a virtual environment or in your default Python 3 environment. In this case, download `sheetFeeder.py` to your working directory and import it from your scripts in the same directory.

    Dependencies to install into environment:

    * `pip install requests`
    * `pip install --upgrade google-api-python-client`
    * `pip install oauth2client`

    In this scenario, you will place the `credentials.json` file from step 2 below in the same working directory as `sheetFeeder.py`.


2. Obtain API credentials. To begin using the Google Sheets API you need to obtain credentials specific to your Google account and make them available to `sheetFeeder`. 

    - Go to https://developers.google.com/sheets/api/quickstart/python. Make sure you are signed in as the Google identity you want to enable API access for. 
    - Click "Enable the Google Sheets API" button. Download the API credentials as `credentials.json`.
    - Place `credentials.json` in the `sheetFeeder` package location as identified in step 1 above (will be different depending on which type of installation you opted for).

3. Authenticate and authorize access to your Google account's API (Quickstart).
    - Download and run [sample.py](https://github.com/dwhodges2/sheetFeeder/blob/master/sample.py) in your working directory.
    - The first time you use the API you will be asked to select the Google identity to use (if more than one are detected) and to verify access. Note that you may see a warning that the application is not verified by Google. You can go to the "advanced" option and proceed with the "Quickstart" authentication process from there.
    - Click through to grant read/write permission to your Google Sheets account. If successful you will see a message saying "The authentication flow has completed."
    - If successful, a `token.json` file should be created in the same folder as the `credentials.json` file (see step 1 above for location), and a brief readout of sample table data will appear. Once the credentials and token are in place, you be able to access sheets via the API without additional steps; you can verify this by running `sample.py` again—you should get the read-out without the authentication steps. 

### Reusing and revoking API credentials

Note that your API credentials (`credentials.json` and `token.json`) can be reused in other environments where `sheetFeeder` is installed without repeating steps 2–3 above. You may copy them to the appropriate location per step 1 above. To disallow API access and reset to the initial state, simply delete the files. You may also manage API access via the [Google API console](https://console.developers.google.com/).


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
  * Optional query to filter results, see syntax of `matchingRows()` below.
  * Example: `my_sheet.getData()`
  * Result: [['head1', 'head2'],['a', 'b'],['one', 'two']]
  * Example with filter: `my_sheet.getData(filter_queries=[['head2', 'b']])`
  * Result: [['a', 'b']]

* `getDataColumns()`
  * Return the contents of dataSheet rotated as columns, in a list of lists.
  * Example: `my_sheet.getDataColumns()`
  * Result: [['head1', 'a', 'one'],['head2', 'b','two']]
* `getDataSeries()`
  * Return the contents of dataSheet as a dict with each column a series. Assumes that the first row is heads.
  * Example: `my_sheet.getDataSeries()`
  * Result: {'head1: ['a', 'c'], 'head2': ['b', 'd']}
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
  * Import a CSV file into a designated sheet range, overwriting what is there. Can be either local or remote. If string begins with "http" it will be treated as a URL and requested via urllib3. Otherwise it will treat it as a local file path. Delimeter is comma by default, but can be any character, e.g., pipe ('|').
  * Example: `my_sheet.importCSV(my_file_path,delim='|')`
  * Result: Import contents of pipe-delimited text file into dataSheet.

### Additional subclasses

* `.id`: Returns id part of dataSheet 
* `.range`: Returns range part of dataSheet 
* `.initInfo`: Returns dictionary of metadata about sheet (all tabs, not just the one defined in 2nd arg of dataSheet).
* `.initTabs`: Returns a list of names of tabs in spreadsheet.
* `.url`: Returns public url of sheet of form https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={tab_id}


## Using sheetFeeder with Pandas

You can easily use sheetFeeder in [Pandas](https://pandas.pydata.org/) projects. Data retrieved from Google Sheets is easily translated into Pandas dataframes. Pandas outputs can be posted to Google Sheets as well. The file `pandas_examples.py` demonstrates some use cases. The default output from sheetFeeder is a 2-dimensional list array. So, assuming the first row contains the heads, you only need to pop that row into the `columns` parameter when creating a DataFrame object.

  ```python
  def datasheet_to_dataframe(_sheet_id, _sheet_range):
    the_data = dataSheet(_sheet_id, _sheet_range).getData()
    heads = the_data.pop(0)  # assumes the first row is column heads.
    return pd.DataFrame(the_data, columns=heads)

  df = datasheet_to_dataframe(sheet_id, sheet_range)
  ```

Using the sample table in the example, the `df` object will look like:


  ```
      Col A Col B Col C Col D
  0     1     2     3     4
  1     5     6     7     8
  ```

The reverse process converts a Pandas dataframe back into a 2-dimensional array for use in sheetFeeder:

  ```python
  def dataframe_to_datasheet(_df):
    heads = list(_df.columns.values)
    ds = _df.values.tolist()
    ds.insert(0, heads)
    return ds

  dataframe_to_datasheet(df)

  >>> [['Col A', 'Col B', 'Col C', 'Col D'], ['1', '2', '3', '4'], ['5', '6', '7', '8']]
  ```

The `getDataSeries()` method also gets data as series such that they can be fed into a Pandas dataframe easily:

  ```python
  ds = dataSheet(sheet_id, sheet_range)
  ds_series = ds.getDataSeries()
  ds_series

  >>> {'Col A': ['1', '5'], 'Col B': ['2', '6'], 'Col C': ['3', '7'], 'Col D': ['4', '8']}

  pd.DataFrame(ds_series)

  >>> 
    Col A Col B Col C Col D
  0     1     2     3     4
  1     5     6     7     8
  ```

Run the included `pandas_examples.py` to demonstrate the transformations to and from Pandas.

## Error handling and recovery

Occasionally the API returns an HTTP error of one kind or another (`googleapiclient.errors.HttpError`) and refuses a request. Assuming credentials are in order, this is likely an intermittent problem on the server side, and can be addressed by recovering and retrying the request after a short interval. Several defaults are defined as global variables in `sheetFeeder.py` to apply to all API calls:

* `retry_default = True`
* `interval_default = 0.5`
* `max_tries_default = 5`

A backoff function will double the retry interval with each try until the max number is reached. If the request still cannot be executed, an exception is raised of the class `sheetFeederError`. The optimal interval between retries is subject to speculation.


## Notes

This is a work in progress. Comments/suggestions very welcome. 

