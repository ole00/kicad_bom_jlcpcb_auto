import csv

# This script extracts the basic parts from the full list
# of lcsc/jlpcb part library.

# The full list of components (parts.csv) can be downloaded from :
# https://github.com/yaqwsx/jlcparts/actions/workflows/update_components.yaml
# * click on the latest "Update component database" item
# * scroll down to Artifacts section  and download "component_table"
# * unzip the downloaded archive which contins the full lcsc part list as 'parts.csv'


def normaliseCell(cell):
 if (cell.find(',') < 0):
    return cell
 return '"' + cell + '"'

def parse():
  with open("./parts.csv", 'r') as file:
    counter = 0
    csvreader = csv.reader(file)
    for row in csvreader:
      if (row[7][0] == 'b') or (counter == 0) :
        counter = counter + 1
        firstCategory = normaliseCell(row[1])
        secondCategory = normaliseCell(row[2])
        mfrPart = normaliseCell(row[3])
        manufacturer = normaliseCell(row[6])
        description = normaliseCell(row[8])
        datasheet = normaliseCell(row[9])
        price =  normaliseCell(row[11])

        line = row[0] + ',' + firstCategory + ',' + secondCategory + ',' + mfrPart + ',' + row[4] + ',' + row[5] + \
               manufacturer + ',' + row[7] + ',' + description + ',' + datasheet + ',' + row[10] + ',' + price
        print(line)


parse()