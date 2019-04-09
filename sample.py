import GoogleSheetAPITools as gs
import secrets
from pprint import pprint


# The ID and range of a sample spreadsheet.
test_sheet = secrets.default_sheet
test_range = secrets.default_range


def main():

#    print(gs.sheetLookup(test_sheet,test_range,"b",1,0))

    # Clear contents of sheet
    gs.sheetClear(test_sheet,test_range)

    # Query rows that match two regex queries (AND junction)
    x = gs.getMatchingRows(the_sheet, the_range, [['linked_records_record_id', 'resource'],['linked_records_record_title', 'Marvin']], regex=True, operator='and')

    pprint(x)

    # Write data to sheet
    gs.sheetAppend(the_sheet,the_target,the_data)

    # Get list tab names from sheet
    the_tabs = gs.getSheetTabs(test_sheet)

    # Get data from 2nd tab
    the_data = gs.getSheetData(test_sheet, str(the_tabs[1] + '!A:Z'))



if __name__ == '__main__':
    main()
