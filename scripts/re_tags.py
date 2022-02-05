"""Creates renewable energy tags"""

import pandas as pd
import functions


def main():
    """Creates renewable energy tags.

    Reads in the configuration file and parses the PWR technologies to create
    a list of renewable energy technologies based on the fuel type
    """

    # PARAMETERS

    region = functions.get_from_yaml('continent')
    subregions = functions.get_from_yaml('regions_dict')
    years = functions.get_years()
    fuels = functions.get_from_yaml('rnw_fuels')

    # PROCESSINGS

    #columns = region, emission, year, value
    data_out = []

    #print all values
    for year in years:
        for country in subregions.keys():
            for subregion in subregions[country].keys():
                for fuel in fuels:
                    tech_name = 'PWR' + fuel + country + subregion + '01'
                    data_out.append([region, tech_name, year, 1])

    #write to a csv
    df_out = pd.DataFrame(data_out,
                          columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    df_out.to_csv('../src/data/RETagTechnology.csv', index=False)


if __name__ == '__main__':
    main()
