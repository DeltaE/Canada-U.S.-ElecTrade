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
    subregions = (functions.openYaml().get('subregions_dictionary')).keys()
    years = functions.getYears()

    #Techs to tag
    techs = functions.openYaml().get('rnw_techs')

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
                for tech in techs:
                    techName = 'PWR' + tech + 'CAN' + subregion + '01'
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

    subregions = functions.getRegionDictionary('USA')

    techs = functions.openYaml().get('rnw_techs')
    years = functions.getYears()

    outData = []

    for year in years:
        for subregion in subregions['USA']:
            for tech in techs:
                region = 'NAmerica'
                techName = 'PWR' + tech + 'USA' + subregion + '01'
                outData.append([region, techName, year, 1])

    # create and return datafram
    dfOut = pd.DataFrame(outData, columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()