"""Creates availability factor data."""


import pandas as pd
import functions
from pathlib import Path

# MODULE CONSTANTS

# Residual Hydro Capacity (GW) per province in 2017
# https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startYear=2017&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20170101
_RESIDUAL_HYDRO_CAPACITY = {
    'BC': 15.407,
    'AB': 1.218,
    'SK': 0.867,
    'MB': 5.461,
    'ON': 9.122,
    'QC': 40.438,
    'NB': 0.968,
    'NL': 6.762,
    'NS': 0.370,
    'PE': 0.000
}

# Hydro generation (TWh) per province in 2017
# https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501&pickMembers%5B0%5D=1.1&pickMembers%5B1%5D=2.1&cubeTimeFrame.startMonth=01&cubeTimeFrame.startYear=2017&cubeTimeFrame.endMonth=12&cubeTimeFrame.endYear=2017&referencePeriods=20170101%2C20171201
_HYDRO_GENERATION = {
    'BC': 66.510,
    'AB': 2.050,
    'SK': 3.862,
    'MB': 35.991,
    'ON': 39.492,
    'QC': 202.001,
    'NB': 2.583,
    'NL': 36.715,
    'NS': 0.849,
    'PE': 0.000
}


def main():
    """Creates hydro facility availability factors.

    Generates Canadian availability factors for hydro power plants based on
    2017 capacity and generation levels. These values are copied over for the
    entire time horizon. USA hydro availability factors are generated from the
    existing USA dataset's capacity factors.
    """

    # PARAMETERS

    region = functions.get_from_yaml('continent')
    subregions = functions.get_from_yaml('regions_dict')['CAN']
    years = functions.get_years()

    # CALCULATIONS

    # Availability factor for each Canadian province
    af = {}
    for subregion in subregions:
        generation = 0  #TWh
        capacity = 0  #TW
        #calcualte totals for subregion
        for province in subregions[subregion]:
            capacity = capacity + _RESIDUAL_HYDRO_CAPACITY[province]
            generation = generation + _HYDRO_GENERATION[province]
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
    df_usa = functions.get_usa_capacity_availability_factor(False)
    df = df.append(df_usa)

    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/AvailabilityFactor.csv')
    df.to_csv(output_dir, index=False)


if __name__ == '__main__':
    main()
