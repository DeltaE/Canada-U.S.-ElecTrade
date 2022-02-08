# pylint: skip-file

"""Add description. """

import os
import sys
import collections
from datetime import datetime
import copy

# See README for info

# CONSTANTS

_LIST_OF_SHEETS = ["AccumulatedAnnualDemand.csv"
                      ,"AnnualEmissionLimit.csv"
                      ,"AnnualExogenousEmission.csv"
                      ,"AvailabilityFactor.csv"
                      ,"CapacityFactor.csv"
                      ,"CapacityOfOneTechnologyUnit.csv"
                      ,"CapacityToActivityUnit.csv"
                      ,"CapitalCost.csv"
                      ,"CapitalCostStorage.csv"
                      ,"Conversionld.csv"
                      ,"Conversionlh.csv"
                      ,"Conversionls.csv"
                      ,"DAILYTIMEBRACKET.csv"
                      ,"DAYTYPE.csv"
                      ,"DaySplit.csv"
                      ,"DaysInDayType.csv"
                      ,"DepreciationMethod.csv"
                      ,"DiscountRate.csv"
                      ,"EMISSION.csv"
                      ,"EmissionActivityRatio.csv"
                      ,"EmissionsPenalty.csv"
                      ,"FUEL.csv"
                      ,"FixedCost.csv"
                      ,"InputActivityRatio.csv"
                      ,"MODE_OF_OPERATION.csv"
                      ,"MinStorageCharge.csv"
                      ,"ModelPeriodEmissionLimit.csv"
                      ,"ModelPeriodExogenousEmission.csv"
                      ,"OperationalLife.csv"
                      ,"OperationalLifeStorage.csv"
                      ,"OutputActivityRatio.csv"
                      ,"REGION.csv"
                      ,"REMinProductionTarget.csv"
                      ,"RETagFuel.csv"
                      ,"RETagTechnology.csv"
                      ,"ReserveMargin.csv"
                      ,"ReserveMarginTagFuel.csv"
                      ,"ReserveMarginTagTechnology.csv"
                      ,"ResidualCapacity.csv"
                      ,"ResidualStorageCapacity.csv"
                      ,"SEASON.csv"
                      ,"STORAGE.csv"
                      ,"SpecifiedAnnualDemand.csv"
                      ,"SpecifiedDemandProfile.csv"
                      ,"StorageLevelStart.csv"
                      ,"StorageMaxChargeRate.csv"
                      ,"StorageMaxDischargeRate.csv"
                      ,"TECHNOLOGY.csv"
                      ,"TIMESLICE.csv"
                      ,"TechnologyFromStorage.csv"
                      ,"TechnologyToStorage.csv"
                      ,"TotalAnnualMaxCapacity.csv"
                      ,"TotalAnnualMaxCapacityInvestment.csv"
                      ,"TotalAnnualMinCapacity.csv"
                      ,"TotalAnnualMinCapacityInvestment.csv"
                      ,"TotalTechnologyAnnualActivityLowerLimit.csv"
                      ,"TotalTechnologyAnnualActivityUpperLimit.csv"
                      ,"TotalTechnologyModelPeriodActivityLowerLimit.csv"
                      ,"TotalTechnologyModelPeriodActivityUpperLimit.csv"
                      ,"TradeRoute.csv"
                      ,"VariableCost.csv"
                      ,"YEAR.csv"
                      ,"YearSplit.csv"]

def main():
    """Add description."""
    # Enumerate arguments to get paths to old and new files
    arguments = []
    for argument in enumerate(sys.argv):
        arguments.append(argument)

    # Generate results file
    resultsTxt = open("Results.txt", "w")

    # Reading from files
    scriptDir = os.path.dirname(__file__)
    oldDir = os.path.join(scriptDir, arguments[1][1])
    newDir = os.path.join(scriptDir, arguments[2][1])

    oldTxt = open(oldDir, "r")
    newTxt = open(newDir, "r")

    # Lists of lists of lines
    oldListList = []
    newListList = []

    oldListList = populateListList(oldListList, oldTxt)
    newListList = populateListList(newListList, newTxt)

    # Lists of counters of lines
    # (this conversion from lists to counters may not be necessecary any more, but it makes it so
    # that the diff will check differences "unordered" rather than "ordered". This was useful
    # when it was comparing CanadaUSA.txt files, whose contents are the same between model runs but
    # ordered differently)
    oldCounterList = []
    newCounterList = []

    for i in range(0, len(_LIST_OF_SHEETS)):
        oldCounterList.append(collections.Counter(oldListList[i]))
        newCounterList.append(collections.Counter(newListList[i]))

    printTimestamp(resultsTxt)

    # Compare files
    for i in range(0, len(_LIST_OF_SHEETS)):
        resultsTxt.write("\n\n" + _LIST_OF_SHEETS[i] + "\n")
        if oldCounterList[i] == newCounterList[i]:
            resultsTxt.write("Both files are the same.")
        else: # oldCounterList[i] != newCounterList[i]
            resultsTxt.write("The two files are different.")

            oldCounterCopy = copy.deepcopy(oldCounterList[i]) # The copies are to avoid calling already modified counters
            newCounterCopy = copy.deepcopy(newCounterList[i])

            oldCounterList[i].subtract(newCounterCopy) # Deletions
            deletedElements = list(oldCounterList[i].elements())

            newCounterList[i].subtract(oldCounterCopy) # Additions
            addedElements = list(newCounterList[i].elements())

            resultsTxt.write("\n\n" + "Deleted Elements:" + "\n")
            for i in range(0, len(deletedElements)):
                resultsTxt.write(deletedElements[i])
            
            resultsTxt.write("\n" + "Added Elements:" + "\n")
            for i in range(0, len(addedElements)):
                resultsTxt.write(addedElements[i])

def printTimestamp(resultsTxt):
    """Add description.
    
    Args:
        resultsTxt: add description
    """
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    resultsTxt.write("\n\n" + "Timestamp:" + "\n")
    resultsTxt.write(timestamp)

def populateListList(listList, txt):
    """Add description.
    
    Args:
        listList: add description
        txt: add description
    """

    # Reads lines by CSV into a list of list of lines.
    # In Format [[...],[...],[...]...] where each of the inner
    # lists correspondes to a particular CSV, in order
    current_sheet_id = 0
    listList.append([])
    for line in txt:
        if line == ';\n':
            current_sheet_id = current_sheet_id + 1
            listList.append([])
        else:
            listList[current_sheet_id].append(line)

    return listList

if __name__ == '__main__':
    main()
