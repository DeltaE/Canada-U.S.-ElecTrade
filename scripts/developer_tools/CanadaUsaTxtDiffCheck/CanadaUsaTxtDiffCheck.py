import os
import collections
from datetime import datetime
import copy

# See README for info

def main():
    # Change these names if the files you are comparing have different names
    NAME_OF_OLD_FILE = "CanadaUSA.txt"
    NAME_OF_NEW_FILE = "CanadaUSA.txt"

    # Generate results file
    resultsTxt = open("Results.txt", "w")

    # Reading from files
    scriptDir = os.path.dirname(__file__)
    oldDir = os.path.join(scriptDir, "Old Copy/" + NAME_OF_OLD_FILE)
    newDir = os.path.join(scriptDir, "New Copy/" + NAME_OF_NEW_FILE)

    oldTxt = open(oldDir, "r")
    newTxt = open(newDir, "r")

    oldList = oldTxt.readlines()
    newList = newTxt.readlines()

    oldCounter = collections.Counter(oldList)
    newCounter = collections.Counter(newList)

    # Compare files
    if oldCounter == newCounter:
        resultsTxt.write("Both files are the same.")
        printTimestamp(resultsTxt)
    else: # oldCounter != newCounter
        resultsTxt.write("The two files are different.")
        printTimestamp(resultsTxt)

        oldCounterCopy = copy.deepcopy(oldCounter) # The copies are to avoid calling already modified counters
        newCounterCopy = copy.deepcopy(newCounter)

        oldCounter.subtract(newCounterCopy) # Deletions
        deletedElements = list(oldCounter.elements())

        newCounter.subtract(oldCounterCopy) # Additions
        addedElements = list(newCounter.elements())

        resultsTxt.write("\n\n" + "Deleted Elements:" + "\n")
        for i in range(0, len(deletedElements)):
            resultsTxt.write(deletedElements[i])
        
        resultsTxt.write("\n" + "Added Elements:" + "\n")
        for i in range(0, len(addedElements)):
            resultsTxt.write(addedElements[i])

def printTimestamp(resultsTxt):
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    resultsTxt.write("\n\n" + "Timestamp:" + "\n")
    resultsTxt.write(timestamp)

if __name__ == '__main__':
    main()