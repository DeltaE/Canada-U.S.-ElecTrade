"""Creates emission penalty data."""

import pandas as pd
import functions


def main():
    """Generates global emission penalty data.

    Creates otoole formatted emission penalty data for both countries in units
    of M$/MT. Since emission penalty is defined over region, the value is
    defined at a global level, rather then a provicial, subregional, or
    regional level.
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    years = functions.get_years()

    # PROCESSING

    #read in raw emission activity values
    df_raw = pd.read_csv('../dataSources/EmissionPenaltyByYear.csv',
                         index_col=0)

    #list to hold all output values
    #columns = region, emission, year, value
    data_out = []

    for year in years:
        penalty = df_raw.loc[year, 'PENALTY (M$/Mtonne)']
        data_out.append([continent, 'CO2', year, penalty])

    #write to a csv
    df_out = pd.DataFrame(data_out,
                          columns=['REGION', 'EMISSION', 'YEAR', 'VALUE'])
    df_out.to_csv('../src/data/EmissionsPenalty.csv', index=False)


if __name__ == '__main__':
    main()
