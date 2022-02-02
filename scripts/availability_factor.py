"""Creates availability factor data."""


import pandas as pd
import functions
import constants as const


def main():
    """Creates hydro facility availability factors.

    Generates Canadian availability factors for hydro power plants based on
    2017 capacity and generation levels. These values are copied over for the
    entire time horizon. USA hydro availability factors are generated from the
    existing USA dataset's capacity factors.

    """

    # PARAMETERS

    region = functions.openYaml().get('regions')
    subregions = (functions.openYaml().get('subregions_dictionary'))['CAN']
    years = functions.getYears()

    # CALCULATIONS

    # Availability factor for each Canadian province
    af = {}
    for subregion in subregions:
        generation = 0  #TWh
        capacity = 0  #TW
        #calcualte totals for subregion
        for province in subregions[subregion]:
            capacity = capacity + const.RESIDUAL_HYDRO_CAPACITY[province]
            generation = generation + const.HYDRO_GENERATION[province]
        #save total availability factor
        af[subregion] = (generation * (1000 / 8760)) / capacity

    #columns = region, technology, year, value
    out_df = []

    #Populate output lsit
    for year in years:
        print(f'Hydro {year}')
        for subregion in subregions:
            tech_name = 'PWR' + 'HYD' + 'CAN' + subregion + '01'
            af_value = round(af[subregion], 3)
            out_df.append([region, tech_name, year, af_value])

    df = pd.DataFrame(out_df,
                      columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    df_usa = functions.getUsaCapacityOrAvailabilityFactor(False)
    df = df.append(df_usa)

    df.to_csv('../src/data/AvailabilityFactor.csv', index=False)


if __name__ == '__main__':
    main()
