#coding=utf-8

#  use python3 !

import os
import locale
import sys
import csv

os.environ["PYTHONIOENCODING"] = "utf-8"

VERSION = "1.0"

symOhm = "Ω"
resistorList = []
capacitorList = []

class Component:
    def __init__(self, ref, package, value, altvalue1, altvalue2, partNumber, comment):
        self.ref = ref
        self.package = package
        self.value = value
        self.altvalue1 = altvalue1
        self.altvalue2 = altvalue2
        self.partNumber = partNumber
        self.comment = comment
        self.key = 0
        if (self.ref == "R"):
            self.key = (int(package, 10) * 10000000000) + getKeyValueResistor(altvalue2)
        else:
            if (self.ref == "C"):
                self.key = (int(package, 10) * 10000000000) + getKeyValueCapacitor(altvalue2)
            

    def toXmlString(self):
        return "<comp ref=\"" + self.ref + "\" package=\"" + self.package + "\" value=\"" + self.value + \
         "\" altvalue1=\"" + self.altvalue1 + "\" altvalue2=\""  + self.altvalue2 + "\" pn=\"" + self.partNumber + "\" /> <!-- " + self.comment + " -->"
    def toString(self):
        return "ref=" + self.ref + " package=" + self.package + " value=" + self.value + \
         " altvalue1=" + self.altvalue1 + " altvalue2="  + self.altvalue2 + " partNumber=" + self.partNumber + " key=" + str(self.key)


def getAltValueResistor(value):
    # milli Ohms (100m)
    indexM = value.find('m');
    if (indexM > 0):
        value = "0." + value[0: indexM]
        return value


    index = value.find('.');
    if (index < 0):
        return value

    indexK = value.find('k');
    if (indexK > 0):
        value = value.replace("k", " ").replace(".", "k").rstrip()
        return value
    # Mega Ohms
    indexM = value.find('M');
    if (indexM > 0):
        value = value.replace("M", " ").replace(".", "M").rstrip()
  
    return value.replace(".", "R")

def getKeyValueResistor(value):
    indexR = value.find('R')
    if (indexR > 0):
        numVal = int(value[0: indexR], 10) * 10
        l = len(value)
        if (indexR < l - 1):
            numVal += int(value[indexR + 1 : l])
        return numVal
        
    indexM = value.find('m')
    if (indexM > 0):
        return int(value[0:1], 10)

    #dots are in milli unit only
    indexDot = value.find('.')
    if (indexDot > 0):
        return int(value[indexDot + 1 : indexDot + 2], 10)
    
    return int(value) * 10

def getNumericValueResistor(value):
    numVal = 0
    indexK = value.find('k')
    if (indexK > 0):
        numVal = int(value[0: indexK], 10) * 1000
        l = len(value)
        if (indexK < l - 1):
            numVal += int(value[indexK + 1 : indexK + 2]) * 100
        indexK = indexK + 1
        if (indexK < l - 1):
            numVal += int(value[indexK + 1 : indexK + 2]) * 10
        
        return str(numVal)
        
    indexM = value.find('M')
    if (indexM > 0):
        numVal = int(value[0: indexM], 10) * 1000000
        l = len(value)
        if (indexM < l - 1):
            numVal += int(value[indexM + 1 : l]) * 100000
        return str(numVal)

    return value


def createResistor(comment, package, partNumber):
    ohmIndex = comment.find(symOhm)
    if (ohmIndex < 0):
        print("invalid resistor part:" + partNumber, file=sys.stderr)
        return
    valueStartIndex = ohmIndex
    while (valueStartIndex > 0) and (comment[valueStartIndex] != ' '):
        valueStartIndex = valueStartIndex - 1
    value = comment[valueStartIndex + 1 : ohmIndex].rstrip()
    
    altvalue1 = getAltValueResistor(value)
    altvalue2 = getNumericValueResistor(altvalue1)
    c = Component("R", package, value, altvalue1, altvalue2, partNumber, comment)
    resistorList.append(c)


# Process Resistors
def parseResistors():
    print("Processing resistors", file=sys.stderr);
    with open("./basic_parts.csv", 'r') as file:
        counter = 0
        csvreader = csv.reader(file)
        for row in csvreader:
            #ensure the part is basic
            if row[6][0] == 'b' :
                category = row[1]
                subCategory = row[2]
                # Surface mount Resistors
                if (category == "Resistors") and (subCategory.find("urface") >= 0):
                    comment = row[7]
                    package = row[4]
                    partNumber = row[0]
                    #print("line=" + partNumber)

                    createResistor(comment, package, partNumber)
                    counter = counter + 1
                    #if (counter > 150):
                    #    return

# get alternative capacitor value
# here we convert higher units:
#  *  to lower units, like 1nF to 1000pF or 4.7uF to 4700nF
#     if the value is in single digits (lesst han 10)
#  *  to higher units, like  100nF to 0.1uF o 470pF to 0.47uF
#     if the values are in 2 or more digits
def getAltValueCapacitor(value):

    # handle nF
    index = value.find('nF');
    if (index > 0):
        fv = float(value[0:index])
        if (fv < 10):
            return str(int(fv * 1000)) + "pF"
        else:
            fv /= 1000
            return str(fv) + "uF"

    # handle pF - they go only up if the value is in 2 digits
    index = value.find('pF');
    if (index > 0):
        fv = float(value[0:index])
        if (fv > 10):
            fv /= 1000
            return str(fv) + "nF"

    # handle uF - they go only down if the value is in single digits
    index = value.find('uF');
    if (index > 0):
        fv = float(value[0:index])
        if (fv < 10):
            return str(int(fv * 1000)) + "nF"

    return value

# get capacitor value in pF
def getNumericValueCapacitor(value):

    # handle nF
    index = value.find('nF');
    if (index > 0):
        fv = float(value[0:index])
        return str(int(fv * 1000)) + "pF"

    # handle uF
    index = value.find('uF');
    if (index > 0):
        fv = float(value[0:index])
        return str(int(fv * 1000000)) + "pF"

    return value

# convert to integer, in pF * 10
def getKeyValueCapacitor(value):
    index = value.find('pF');
    if (index > 0):
        fv = float(value[0:index])
        return int(fv * 10)
    return 0


def createCapacitor(comment, package, partNumber):
    faradIndex = comment.find("uF")
    if (faradIndex < 0):
        faradIndex = comment.find("nF")
    if (faradIndex < 0):
        faradIndex = comment.find("pF")
    if (faradIndex < 0):
        print("invalid capacitor part:" + partNumber)
        return
    valueStartIndex = faradIndex
    while (valueStartIndex > 0) and (comment[valueStartIndex] != ' '):
        valueStartIndex = valueStartIndex - 1
    value = comment[valueStartIndex + 1 : faradIndex+2].rstrip()
    
    altvalue1 = getAltValueCapacitor(value)
    altvalue2 = getNumericValueCapacitor(value)
    c = Component("C", package, value, altvalue1, altvalue2, partNumber, comment)
    capacitorList.append(c)

# Process Capacitors
def parseCapacitors():
    print("Processing capacitors", file=sys.stderr);
    with open("./basic_parts.csv", 'r') as file:
        counter = 0
        csvreader = csv.reader(file)
        for row in csvreader:
            #ensure the part is basic
            if row[6][0] == 'b' :
                category = row[1]
                subCategory = row[2]
                # Surface mount Capacitors : MLCC
                if (category == "Capacitors") and (subCategory.find("MLCC") >= 0):
                    comment = row[7]
                    package = row[4]
                    partNumber = row[0]
                    #print("line=" + partNumber)

                    createCapacitor(comment, package, partNumber)
                    counter = counter + 1
                    #if (counter > 150):
                    #    return


def printComponents(componentList):
    counter = 0;
    package = ""
    for part in componentList:
        if (package != part.package) and (counter > 0):
            print("");
        counter = counter + 1
        package = part.package
        print("\t" + part.toXmlString())
    print("");


def exportXml():
    print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
    print("");
    print("<!--- Generated by export_default_cpomonents.py3  version " + VERSION + " -->");
    print("<!--- Use with Kicad BOM exporter -->");
    
    print("");
    print("<lcsc>");
    print("\t<!-- enable / disable component search from this database -->");
    print("\t<search enable=\"true\" />");
    print("");

    print("\t<!-- Resistors ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->");
    printComponents(resistorList)

    print("\t<!-- Capacitors ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->");
    printComponents(capacitorList)

    print("</lcsc>");


def main():
    parseResistors()
    parseCapacitors()

    # Sort components
    resistorList.sort(key=lambda Component: Component.key)
    capacitorList.sort(key=lambda Component: Component.key)

    exportXml()
    
main()

