from sheetFeeder import dataSheet

# Change vars below to match the UID and range of a Google sheet to read.
# The Google account from which the API credentials are obtained
# must have edit priviledges to the test sheet.

sheet_id = '19zHqOJt9XUGfrfzAXzOcr4uARgCGbyYiOtoaOCAMP7s'
sheet_range = 'Sheet1!A:Z'

my_sheet = dataSheet(sheet_id,sheet_range)

x = my_sheet.getData()

print(x)

print(' ')
print('Go to ' + my_sheet.url + ' to see the data!')

