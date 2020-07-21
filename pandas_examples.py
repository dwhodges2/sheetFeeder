from sheetFeeder import dataSheet
import pandas as pd
import uuid

# This code shows how to translate to and from the Popular Pandas dataframe object type. You can use sheetFeeder to easily import your data from a Google Sheet into Pandas and/or write out your processed data back to Google Sheets. Installation of Pandas is required.

sheet_id = '19zHqOJt9XUGfrfzAXzOcr4uARgCGbyYiOtoaOCAMP7s'
sheet_range = 'Sheet1!A:Z'


# Functions to translate sheetFeeder dataSheet to/from Pandas dataframes
def datasheet_to_dataframe(_sheet_id, _sheet_range):
    # Read sheet data into a Pandas dataframe object.
    the_data = dataSheet(_sheet_id, _sheet_range).getData()
    heads = the_data.pop(0)  # assumes the first row is column heads.
    return pd.DataFrame(the_data, columns=heads)


def dataframe_to_datasheet(_df):
    heads = list(_df.columns.values)
    ds = _df.values.tolist()
    ds.insert(0, heads)
    return ds


# Data from sheetFeeder dataSheet
print("dataSheet data array:")
ds = dataSheet(sheet_id, sheet_range).getData()
print(ds)

print("")

# ds to df example
df = datasheet_to_dataframe(sheet_id, sheet_range)
print("Converted to dataframe:")
print(df)

print("")

# df back to ds
ds = dataframe_to_datasheet(df)
print("Converted back to dataSheet array:")
print(ds)

print("")

# Get sheetFeeder data as series, and convert to Pandas df
ds = dataSheet(sheet_id, sheet_range)
ds_series = ds.getDataSeries()
print("Data as series:")

print("")

print(ds_series)
df = pd.DataFrame(ds_series)
print("Series converted to dataframe:")
print(df)
