import csv

with open('Workbook1.csv', 'rb') as csvfile:
    rr = csv.reader(csvfile, delimiter=',')
    for row in rr:
        print row[0]
