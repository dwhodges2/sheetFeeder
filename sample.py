import GoogleSheetAPITools as gs
import secrets

# The ID and range of a sample spreadsheet.
test_sheet = secrets.default_sheet
test_range = 'Test!A:Z'


def main():

#    print(gs.sheetLookup(test_sheet,test_range,"b",1,0))

    c = gs.sheetClear(test_sheet,test_range)



if __name__ == '__main__':
    main()
