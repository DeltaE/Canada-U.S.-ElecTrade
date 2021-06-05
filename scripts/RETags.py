import pandas as pd

def main():
    # PURPOSE: Creates otoole formatted RETagTechnology
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Regions to print over
    df = pd.read_csv('../src/data/REGION.csv')
    regions = df['VALUE'].tolist()

    # Subregions to print over
    df = pd.read_excel('../dataSources/Regionalization.xlsx', sheet_name='CAN')
    subregions = df['REGION'].tolist()
    subregions = list(set(subregions)) # removes duplicates

    #Years to Print over
    dfYears = pd.read_csv('../src/data/YEAR.csv')
    years = dfYears['VALUE'].tolist()

    #Techs to tag
    techs = ['HYD','WND','BIO','SPV']

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
    dfOut.to_csv('../src/data/RETagTechnology.csv', index=False)

if __name__ == "__main__":
    main()