# coding: utf-8

import os
import urllib
from zipfile import ZipFile
import csv
import pickle

BASE_DIR = os.path.dirname(__file__)
FILE_PICKLE = os.path.join(BASE_DIR, "data/names.pickle")
FILE_ZIP = os.path.join(BASE_DIR, "data/names.zip")


def getNameList():
    if not os.path.exists(FILE_PICKLE):
        print("names.pickle does not exist, generating")
        if not os.path.exists(FILE_ZIP):
            print("names.zip does not exist, downloading from github")
            downloadNames()
        else:
            print("names.zip exists, not downloading")

        print("Extracting names from names.zip")
        namesDict = extractNamesDict()

        maleNames = list()
        femaleNames = list()

        print("Sorting Names")
        for name in namesDict:
            counts = namesDict[name]
            tuple = (name, counts[0], counts[1])
            if counts[0] > counts[1]:
                maleNames.append(tuple)
            elif counts[1] > counts[0]:
                femaleNames.append(tuple)

        names = (maleNames, femaleNames)

        print("Saving names.pickle")
        fw = open(FILE_PICKLE, "wb")
        pickle.dump(names, fw, -1)
        fw.close()
        print("Saved names.pickle")
    else:
        print("names.pickle exists, loading data")
        f = open(FILE_PICKLE, "rb")
        names = pickle.load(f)
        print("names.pickle loaded")

    print(
        "%d male names loaded, %d female names loaded" % (len(names[0]), len(names[1]))
    )

    return names


def downloadNames():
    os.system("wget https://github.com/downloads/sholiday/genderPredictor/names.zip")
    return
    u = urllib.urlopen(
        "https://github.com/downloads/sholiday/genderPredictor/names.zip"
    )
    localFile = open(FILE_ZIP, "w")
    localFile.write(u.read())
    localFile.close()


def extractNamesDict():
    zf = ZipFile(FILE_ZIP, "r")
    filenames = zf.namelist()

    names = dict()
    genderMap = {"M": 0, "F": 1}

    for filename in filenames:
        file = zf.open(filename, "r")
        lines = (line.decode("ascii") for line in file)
        rows = csv.reader(lines)

        for row in rows:
            name = row[0].upper()
            gender = genderMap[row[1]]
            count = int(row[2])

            if name not in names:
                names[name] = [0, 0]
            names[name][gender] = names[name][gender] + count

        file.close()
        print("\tImported %s" % filename)
    return names


if __name__ == "__main__":
    getNameList()
