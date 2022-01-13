import pandas as pd
import functions

def main():
    # PURPOSE: Creates otoole formatted RETagTechnology CSVs 
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    regions = functions.openYaml().get('regions')
    subregions = ((functions.openYaml().get('subregions_dictionary')['CAN'])).keys() # Canadian subregions
    years = functions.getYears()

    #Fuels to tag
    fuels = functions.openYaml().get('rnw_fuels')

    ###########################################
    # Compile RE Tags
    ###########################################

    #list to hold all output values
    #columns = region, emission, year, value
    dataOut = []

    #print all values 
    for region in regions:
        for year in years:
            for subregion in subregions:
                for fuel in fuels:
                    techName = 'PWR' + fuel + 'CAN' + subregion + '01'
                    dataOut.append([region, techName, year, 1])
    
    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfUsa = getUsaRETagTechnology()
    dfOut = dfOut.append(dfUsa)
    dfOut.to_csv('../src/data/RETagTechnology.csv', index=False)

def getUsaRETagTechnology():
    # PURPOSE: Creates RETagTechnology file from USA data
    # INPUT:   none
    # OUTPUT:  dfOut = dataframe to be written to a csv

    subregions = (functions.openYaml().get('subregions_dictionary'))['USA'] # American subregions

    fuels = functions.openYaml().get('rnw_fuels')
    years = functions.getYears()

    outData = []

    for year in years:
        for subregion in subregions:
            for fuel in fuels:
                region = 'NAmerica'
                techName = 'PWR' + fuel + 'USA' + subregion + '01'
                outData.append([region, techName, year, 1])

    # create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()