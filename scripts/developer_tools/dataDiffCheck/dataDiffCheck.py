import os
import collections
from datetime import datetime
import copy

# See README for info

def main():
    LIST_OF_SHEETS = ["AccumulatedAnnualDemand.csv"
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
                      ,"DaysInDayType.csv"
                      ,"DaySplit.csv"
                      ,"DAYTYPE.csv"
                      ,"default_values.csv"
                      ,"DepreciationMethod.csv"
                      ,"DiscountRate.csv"
                      ,"DiscountRateStorage.csv"
                      ,"EMISSION.csv"
                      ,"EmissionActivityRatio.csv"
                      ,"EmissionsPenalty.csv"
                      ,"FixedCost.csv"
                      ,"FUEL.csv"
                      ,"InputActivityRatio.csv"
                      ,"MinStorageCharge.csv"
                      ,"MODE_OF_OPERATION.csv"
                      ,"ModelPeriodEmissionLimit.csv"
                      ,"ModelPeriodExogenousEmission.csv"
                      ,"OperationalLife.csv"
                      ,"OperationalLifeStorage.csv"
                      ,"OutputActivityRatio.csv"
                      ,"REGION.csv"
                      ,"REMinProductionTarget.csv"
                      ,"ReserveMargin.csv"
                      ,"ReserveMarginTagFuel.csv"
                      ,"ReserveMarginTagTechnology.csv"
                      ,"ResidualCapacity.csv"
                      ,"ResidualStorageCapacity.csv"
                      ,"RETagFuel.csv"
                      ,"RETagTechnology.csv"
                      ,"SEASON.csv"
                      ,"SpecifiedAnnualDemand.csv"
                      ,"SpecifiedDemandProfile.csv"
                      ,"STORAGE.csv"
                      ,"StorageLevelStart.csv"
                      ,"StorageMaxChargeRate.csv"
                      ,"StorageMaxDischargeRate.csv"
                      ,"TECHNOLOGY.csv"
                      ,"TechnologyFromStorage.csv"
                      ,"TechnologyToStorage.csv"
                      ,"TIMESLICE.csv"
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

    # Generate new results file
    resultsTxt = open("Sheets Results.txt", "w")

    # Reading from files
    scriptDir = os.path.dirname(__file__)

    # Lists of directories to gather data from
    oldDirList = []
    newDirList = []
    
    for i in range(0, len(LIST_OF_SHEETS)):
        oldDirList.append(os.path.join(scriptDir, "Old Copy/" + LIST_OF_SHEETS[i]))
        newDirList.append(os.path.join(scriptDir, "New Copy/" + LIST_OF_SHEETS[i]))

    # Lists of opened files to gather data from
    oldTxtList = []
    newTxtList = []
    
    for i in range(0, len(LIST_OF_SHEETS)):
        oldTxtList.append(open(oldDirList[i], "r"))
        newTxtList.append(open(newDirList[i], "r"))

    # Lists of lists of lines
    oldListList = []
    newListList = []

    for i in range(0, len(LIST_OF_SHEETS)):
        oldListList.append(oldTxtList[i].readlines())
        newListList.append(newTxtList[i].readlines())

    # Lists of counters of lines
    # (this conversion from lists to counters may not be necessecary any more, but it makes it so
    # that the diff will check differences "unordered" rather than "ordered". This was useful
    # when it was comparing CanadaUSA.txt files, whose contents are the same between model runs but
    # ordered differently)
    oldCounterList = []
    newCounterList = []

    for i in range(0, len(LIST_OF_SHEETS)):
        oldCounterList.append(collections.Counter(oldListList[i]))
        newCounterList.append(collections.Counter(newListList[i]))
    
    printTimestamp(resultsTxt)

    # Compare files
    for i in range(0, len(LIST_OF_SHEETS)):
        resultsTxt.write("\n\n" + LIST_OF_SHEETS[i] + "\n")
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
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    resultsTxt.write("\n\n" + "Timestamp:" + "\n")
    resultsTxt.write(timestamp)

if __name__ == '__main__':
    main()
