from sheetFeeder import dataSheet
import pandas as pd
# import numpy as np


# This code shows how to translate to and from the Popular Pandas dataframe object type. You can use sheetFeeder to easily import your data from a Google Sheet into Pandas and/or write out your processed data back to Google Sheets. Installation of Pandas is required.


def main():

    # Test sheet with sample data
    sheet_id = '19zHqOJt9XUGfrfzAXzOcr4uARgCGbyYiOtoaOCAMP7s'
    sheet_range = 'Sheet1!A:Z'

    # Data from sheetFeeder dataSheet
    print("1. dataSheet data array:")
    ds = dataSheet(sheet_id, sheet_range).getData()
    print(ds)

    print("")

    # ds to df example
    df = datasheet_to_dataframe(sheet_id, sheet_range)
    print("2. Converted to DataFrame:")
    print(df)
    print("")
    print("DataFrame shape:")
    print(df.shape)
    print("")
    print("Data types:")
    print(df.dtypes)
    print("")
    print("Column averages:")
    print(df.mean())

    df['mean'] = df.mean(numeric_only=True, axis=1)
    print(df)
    df.assign(mean_a=df.a.mean(), mean_b=df.b.mean())

    # ds = dataframe_to_datasheet(df)
    # # print(ds)
    # dataSheet(sheet_id, sheet_range).appendData(ds)
    quit()

    print("")

    # df back to ds
    ds = dataframe_to_datasheet(df)
    print("3. Converted back to dataSheet array:")
    print(ds)

    print("")

    # Get sheetFeeder data as series, and convert to Pandas df
    ds = dataSheet(sheet_id, sheet_range)
    ds_series = ds.getDataSeries()
    print("4. Data as series:")
    print(ds_series)
    print("")

    df = pd.DataFrame(ds_series)
    print("5. Series converted to dataframe:")
    print(df)


# Functions to translate sheetFeeder dataSheet to/from Pandas dataframes
def datasheet_to_dataframe(_sheet_id, _sheet_range):
    # Read sheet data into a Pandas dataframe object.
    the_data = dataSheet(_sheet_id, _sheet_range).getData()
    the_data = numberize_data(the_data)
    heads = the_data.pop(0)  # assumes the first row is column heads.
    return pd.DataFrame(the_data, columns=heads)


def dataframe_to_datasheet(_df):
    heads = list(_df.columns.values)
    ds = _df.values.tolist()
    ds.insert(0, heads)
    return ds


def cast_to_number(string):
    try:
        result = int(string)
    except ValueError:
        try:
            result = float(string)
        except ValueError:
            result = string
    return result


def numberize_data(array):
    # input is a list of lists;
    # output casts any number-like strings as either integers or floats
    result = []
    for row in array:
        result.append([cast_to_number(r) for r in row])
    return result


if __name__ == "__main__":
    main()
