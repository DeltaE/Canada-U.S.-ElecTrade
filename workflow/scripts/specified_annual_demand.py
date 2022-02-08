"""Creates specified annual demand data."""

import pandas as pd
import functions
from pathlib import Path


def main():
    """Generates specified annual demand data. """

    # GET DATA

    df_usa = get_usa_specified_annual_demand()
    df_can = get_can_specified_annual_demand()

    # WRITE DATA

    df = pd.DataFrame(df_can, columns=['REGION', 'FUEL', 'YEAR', 'VALUE'])
    df = df.append(df_usa)
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/SpecifiedAnnualDemand.csv')
    df.to_csv(output_dir, index=False)


def get_can_specified_annual_demand():
    """Creates Canadian specified annual demand data.

    Returns:
        demand: List of lists describing Canadaian demand data.
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN']
    years = functions.get_years()

    # CALCULATIONS

    #Read in csv containing data
    source_file = Path(Path(__file__).resolve().parent,
        '../../resources/ProvincialAnnualDemand.csv')
    df = pd.read_csv(source_file, index_col=0)

    #Master list to output
    #Region, fuel, year, value
    demand = []

    # pylint: disable=unused-variable
    for subregion, provinces in can_subregions.items():
        df_provinces = df[can_subregions[subregion]]
        sum_demand = df_provinces.loc[:, :].sum(axis=1)
        for year in years:
            fuel_name = 'ELC' + 'CAN' + subregion + '02'
            value = sum_demand[year]
            value = round(value, 3)
            demand.append([continent, fuel_name, year, value])

    return demand


def get_usa_specified_annual_demand():
    """Creates USA specified annual demand data.

    Returns:
        df_out: Dataframe describing USA demand data
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')

    # GET DATA

    df = pd.read_excel(Path(Path(__file__).resolve().parent,
        '../../resources/USA_Data.xlsx'),
        sheet_name='SpecifiedAnnualDemand(r,f,y)')

    # MAP DATA

    #remove anything from years 2015 - 2018
    df = df.loc[df['YEAR'] > 2018]
    df.reset_index()

    out_data = []
    for i in range(len(df)):
        fuel = 'ELC' + 'USA' + df['REGION'].iloc[i] + '02'
        year = df['YEAR'].iloc[i]
        value = df['DEMAND'].iloc[i]
        value = round(value, 3)
        out_data.append([continent, fuel, year, value])

    #create and return datafram
    df_out = pd.DataFrame(out_data,
                          columns=['REGION', 'FUEL', 'YEAR', 'VALUE'])
    return df_out

if __name__ == '__main__':
    main()
