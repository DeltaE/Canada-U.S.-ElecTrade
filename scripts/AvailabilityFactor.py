import pandas as pd
import functions

def main():
    # PURPOSE: Creates an otoole formatted CSV holding availability factors for Hydro. If Hydro Availability Factors are used, be sure to remove hydro capacity factor  
    # INPUT: none
    # OUTPUT: none

    ###########################################
    # Model Parameters
    ###########################################

    # Parameters to print over
    seasons = functions.openYaml().get('seasons')
    years = functions.openYaml().get('years')
    regions = functions.openYaml().get('regions')
    subregions = functions.openYaml().get('subregions_dictionary')

    ###########################################
    # Availability Factor Calculations
    ###########################################

    #calculate capacity factor for each province 
    af = {}
    for subregion in subregions:
        generation = 0 #TWh
        capacity = 0 #TW
        #calcualte totals for subregion 
        for province in subregions[subregion]:
            capacity = capacity + functions.RESIDUAL_HYDRO_CAPACITY[province]
            generation = generation + functions.HYDRO_GENERATION[province]
        
        #save total capacity factor
        af[subregion] = (generation*(1000/8760))/capacity
    
    #list to save data to 
    #columns = region, technology, year, value
    outData = []

    #Populate output lsit 
    for year in years:
        print(f'Hydro {year}')
        for region in regions:
            for subregion in subregions:
                techName = 'PWR' + 'HYD' + 'CAN' + subregion + '01'
                value = round(af[subregion],3)
                outData.append([region, techName, year, value])

    ###########################################
    # Writing Availability Factor to File 
    ###########################################

    df = pd.DataFrame(outData, columns = ['REGION','TECHNOLOGY','YEAR','VALUE'])
    df.to_csv('../src/data/Canada/AvailabilityFactor.csv', index=False)

if __name__ == "__main__":
    main()
