from sheetFeeder import dataSheet


my_sheet = dataSheet('1YzM1diaFchenQnchemgogyU2menGxv5Gme','Sheet1!A:Z')

x = my_sheet.getData()

print(x)

print('Go to ' + my_sheet.url + ' to see the data!')

