# Requires pytest. Checks basic connectivity and read functions from sample data sheet.
# If in virtual environment, use 'python -m pytest'.

from sheetFeeder import dataSheet

sheet_id = '19zHqOJt9XUGfrfzAXzOcr4uARgCGbyYiOtoaOCAMP7s'
sheet_range = 'Sheet1!A:Z'
test_sheet = dataSheet(sheet_id, sheet_range)


def test_read_sheet_rows():
    the_data = test_sheet.getData()
    assert len(the_data) == 3, "Count of rows should be 3"


def test_read_sheet_columns():
    the_data = test_sheet.getDataColumns()
    assert len(the_data) == 4, "Count of cols should be 4"


def test_query_data():
    query_results = test_sheet.matchingRows(
        [['Col A', '5'], ['Col D', '8']], operator='and')
    assert query_results[1]['row'] == 3, "Should match 3rd row."

# TODO: Add more tests!
