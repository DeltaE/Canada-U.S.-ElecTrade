import pandas as pd
import functions

####################################################
## ASSUMES ALL PROVINCES USE THE SAME COST VALUES ##
####################################################

def main():
    # PURPOSE: Creates an otoole formatted CapitalCostStorage CSV AND OperationalLifeStorage CSV
    # INPUT: none
    # OUTPUT: none

    # Parameters to print over
    continent = functions.getFromYaml('continent')
    canSubregions = functions.getFromYaml('regions_dict')['CAN'].keys() # Canadian subregions
    storages = functions.getFromYaml('sto_techs')
    years = functions.getYears()
    
    if not storages: # sto_techs is an empty list, so the program always steps in here
        df = pd.DataFrame(columns=['REGION','STORAGE','YEAR','VALUE'])
        df.to_csv('../src/data/CapitalCostStorage.csv', index=False)
        return

    #Dictory to hold storage ype and cost in M$/GW
    storageCosts = {'TNK':11.673152}

    ##############################
    ## Populate data
    ##############################

    #columns = region, storage, year, value
    data = []

    for year in years:
        for subregion in canSubregions:
            for storage in storages:
                stoName = 'STO' + storage + 'CAN' + subregion
                cost = storageCosts[storage]
                data.append([continent,stoName,year,cost])

    df = pd.DataFrame(data, columns=['REGION','STORAGE','YEAR','VALUE'])
    df.to_csv('../src/data/CapitalCostStorage.csv', index=False)
    



if __name__ == "__main__":
    main()