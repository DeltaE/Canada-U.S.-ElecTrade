"""Compares two CanadaUSA.txt files for differences. """

import os
import sys
import collections
from datetime import datetime
import copy

# See README for info

# CONSTANTS

_LIST_OF_SHEETS = ['AccumulatedAnnualDemand.csv'
                      ,'AnnualEmissionLimit.csv'
                      ,'AnnualExogenousEmission.csv'
                      ,'AvailabilityFactor.csv'
                      ,'CapacityFactor.csv'
                      ,'CapacityOfOneTechnologyUnit.csv'
                      ,'CapacityToActivityUnit.csv'
                      ,'CapitalCost.csv'
                      ,'CapitalCostStorage.csv'
                      ,'Conversionld.csv'
                      ,'Conversionlh.csv'
                      ,'Conversionls.csv'
                      ,'DAILYTIMEBRACKET.csv'
                      ,'DAYTYPE.csv'
                      ,'DaySplit.csv'
                      ,'DaysInDayType.csv'
                      ,'DepreciationMethod.csv'
                      ,'DiscountRate.csv'
                      ,'EMISSION.csv'
                      ,'EmissionActivityRatio.csv'
                      ,'EmissionsPenalty.csv'
                      ,'FUEL.csv'
                      ,'FixedCost.csv'
                      ,'InputActivityRatio.csv'
                      ,'MODE_OF_OPERATION.csv'
                      ,'MinStorageCharge.csv'
                      ,'ModelPeriodEmissionLimit.csv'
                      ,'ModelPeriodExogenousEmission.csv'
                      ,'OperationalLife.csv'
                      ,'OperationalLifeStorage.csv'
                      ,'OutputActivityRatio.csv'
                      ,'REGION.csv'
                      ,'REMinProductionTarget.csv'
                      ,'RETagFuel.csv'
                      ,'RETagTechnology.csv'
                      ,'ReserveMargin.csv'
                      ,'ReserveMarginTagFuel.csv'
                      ,'ReserveMarginTagTechnology.csv'
                      ,'ResidualCapacity.csv'
                      ,'ResidualStorageCapacity.csv'
                      ,'SEASON.csv'
                      ,'STORAGE.csv'
                      ,'SpecifiedAnnualDemand.csv'
                      ,'SpecifiedDemandProfile.csv'
                      ,'StorageLevelStart.csv'
                      ,'StorageMaxChargeRate.csv'
                      ,'StorageMaxDischargeRate.csv'
                      ,'TECHNOLOGY.csv'
                      ,'TIMESLICE.csv'
                      ,'TechnologyFromStorage.csv'
                      ,'TechnologyToStorage.csv'
                      ,'TotalAnnualMaxCapacity.csv'
                      ,'TotalAnnualMaxCapacityInvestment.csv'
                      ,'TotalAnnualMinCapacity.csv'
                      ,'TotalAnnualMinCapacityInvestment.csv'
                      ,'TotalTechnologyAnnualActivityLowerLimit.csv'
                      ,'TotalTechnologyAnnualActivityUpperLimit.csv'
                      ,'TotalTechnologyModelPeriodActivityLowerLimit.csv'
                      ,'TotalTechnologyModelPeriodActivityUpperLimit.csv'
                      ,'TradeRoute.csv'
                      ,'VariableCost.csv'
                      ,'YEAR.csv'
                      ,'YearSplit.csv']

def main():
    """Compares two CanadaUSA.txt files for differences.

    Compares two CanadaUSA.txt files to make sure that they have the same
    unordered contents within each section. Outputs exact changes between
    the files, if there are any, to Results.txt. More info in associated README.
    """

    # Enumerate arguments to get paths to old and new files
    arguments = []
    for argument in enumerate(sys.argv):
        arguments.append(argument)

    # Generate results file
    results_txt = open('Results.txt', 'w')

    # Reading from files
    script_dir = os.path.dirname(__file__)
    old_dir = os.path.join(script_dir, arguments[1][1])
    new_dir = os.path.join(script_dir, arguments[2][1])

    old_txt = open(old_dir, 'r')
    new_txt = open(new_dir, 'r')

    # Lists of lists of lines
    old_list_list = []
    new_list_list = []

    old_list_list = populate_list_list(old_list_list, old_txt)
    new_list_list = populate_list_list(new_list_list, new_txt)

    # Lists of counters of lines

    # This conversion from lists to counters allows for the diff to check sublist contents
    # "unordered" rather than "ordered". This is important because the order of lines
    # within each CanadaUSA.txt sublist are non-deterministic -- they change each time the
    # scripts are run.
    old_counter_list = []
    new_counter_list = []

    for i in range(0, len(_LIST_OF_SHEETS)):
        old_counter_list.append(collections.Counter(old_list_list[i]))
        new_counter_list.append(collections.Counter(new_list_list[i]))

    print_timestamp(results_txt)

    # Compare files
    for i in range(0, len(_LIST_OF_SHEETS)):
        results_txt.write('\n\n' + _LIST_OF_SHEETS[i] + '\n')
        if old_counter_list[i] == new_counter_list[i]:
            results_txt.write('Both files are the same.')
        else: # oldCounterList[i] != newCounterList[i]
            results_txt.write('The two files are different.')

            # These copies are to avoid calling already modified counters
            old_counter_copy = copy.deepcopy(old_counter_list[i])
            new_counter_copy = copy.deepcopy(new_counter_list[i])

            old_counter_list[i].subtract(new_counter_copy) # Deletions
            deleted_elements = list(old_counter_list[i].elements())

            new_counter_list[i].subtract(old_counter_copy) # Additions
            added_elements = list(new_counter_list[i].elements())

            results_txt.write('\n\n' + 'Deleted Elements:' + '\n')
            for j in range(0, len(deleted_elements)):
                results_txt.write(deleted_elements[j])

            results_txt.write('\n' + 'Added Elements:"' + '\n')
            for j in range(0, len(added_elements)):
                results_txt.write(added_elements[j])

    results_txt.close()
    old_txt.close()
    new_txt.close()

def print_timestamp(resultsTxt):
    """Prints a timestamp.

    Prints the current time in the format MM/DD/YYYY, HH:MM:SS, so that users
    can be sure that something actually happened.

    Args:
        resultsTxt: A reference to the output file.
    """

    timestamp = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
    resultsTxt.write('\n\n' + 'Timestamp:' + '\n')
    resultsTxt.write(timestamp)

def populate_list_list(list_list, txt):
    """Creates a list of list of lines.

    Creates a list of items that are each associated with a specific CSV output
    file, each of item of which is a list containing all relevant lines for that
    CSV output. To reiterate, this function reads lines into a list of list of
    lines in the Format [[...],[...],[...]...], where each of the inner lists
    correspondes to a particular set of output data.

    Args:
        list_list: The list of lists, to be populated.
        txt: The location of the directory being read from, that contains CanadaUSA.txt.

    Returns:
        list_list: The finalized list of list of lines.
    """

    current_sheet_id = 0
    list_list.append([])
    for line in txt:
        if line == ';\n':
            current_sheet_id = current_sheet_id + 1
            list_list.append([])
        else:
            list_list[current_sheet_id].append(line)

    return list_list

if __name__ == '__main__':
    main()
