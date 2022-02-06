"""Creates storage costs."""

import pandas as pd
import functions
from pathlib import Path


def main():
    """Creates storage capex

    All data assumes geography does not effect the capital cost or
    operational life.
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN'].keys()
    storages = functions.get_from_yaml('sto_techs')
    years = functions.get_years()

    # GENERATES DATA

    if not storages:
        df = pd.DataFrame(columns=['REGION', 'STORAGE', 'YEAR', 'VALUE'])
        output_dir = Path(Path(__file__).resolve().parent,
            '../../results/data/CapitalCostStorage.csv')
        df.to_csv(output_dir, index=False)
        return

    #Dictory to hold storage ype and cost in M$/GW
    storage_capex = {'TNK': 11.673152}

    #columns = region, storage, year, value
    data = []

    for year in years:
        for subregion in can_subregions:
            for storage in storages:
                storage_name = 'STO' + storage + 'CAN' + subregion
                cost = storage_capex[storage]
                data.append([continent, storage_name, year, cost])

    df = pd.DataFrame(data, columns=['REGION', 'STORAGE', 'YEAR', 'VALUE'])
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/CapitalCostStorage.csv')
    df.to_csv(output_dir, index=False)


if __name__ == '__main__':
    main()
