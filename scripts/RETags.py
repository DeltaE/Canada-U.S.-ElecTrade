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
    continent = functions.getFromYaml('continent')
    subregions = functions.getFromYaml('subregions_dictionary')
    years = functions.getYears()

    #Fuels to tag
    fuels = functions.getFromYaml('rnw_fuels')

    ###########################################
    # Compile RE Tags
    ###########################################

    #list to hold all output values
    #columns = region, emission, year, value
    dataOut = []

    #print all values 
    for year in years:
        for region in subregions.keys():
            for subregion in subregions[region].keys():
                for fuel in fuels:
                    techName = 'PWR' + fuel + region + subregion + '01'
                    dataOut.append([continent, techName, year, 1])
    
    #write to a csv
    dfOut = pd.DataFrame(dataOut,columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    dfOut.to_csv('../src/data/RETagTechnology.csv', index=False)

if __name__ == "__main__":
    main()