"""Creates renewable energy tags"""

import pandas as pd
import functions
from pathlib import Path


def main():
    """Creates renewable energy tags.

    Reads in the configuration file and parses the PWR technologies to create
    a list of renewable energy technologies based on the fuel type
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    subregions = functions.get_from_yaml('regions_dict')
    fuels = functions.get_from_yaml('rnw_fuels')
    years = functions.get_years()

    # PROCESSINGS

    #columns = region, emission, year, value
    data_out = []

    #print all values
    for year in years:
        for region in subregions.keys():
            for subregion in subregions[region].keys():
                for fuel in fuels:
                    tech_name = 'PWR' + fuel + region + subregion + '01'
                    data_out.append([continent, tech_name, year, 1])

    #write to a csv
    df_out = pd.DataFrame(data_out,
                          columns=['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE'])
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/RETagTechnology.csv')
    df_out.to_csv(output_dir, index=False)


if __name__ == '__main__':
    main()
