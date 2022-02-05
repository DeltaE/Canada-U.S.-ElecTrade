"""Creates storage operational life values"""

import pandas as pd
import functions


def main():
    """Creates operational life storage values.

    Assumes all values are the same regardless of geography.
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    subregions = functions.get_from_yaml('regions_dict')['CAN'].keys()
    storages = functions.get_from_yaml('sto_techs')

    # MAPPING DATA

    if not storages:
        df = pd.DataFrame(columns=['REGION', 'STORAGE', 'VALUE'])
        df.to_csv('../src/data/OperationalLifeStorage.csv', index=False)
        return

    #Dictory to hold storage ype and op life in years
    storage_op_life = {'TNK': 30}

    #List to hold all output data
    #columns = region, storage, value
    data = []

    for subregion in subregions:
        for storage in storages:
            storage_name = 'STO' + storage + 'CAN' + subregion
            life = storage_op_life[storage]
            data.append([continent, storage_name, life])

    df = pd.DataFrame(data, columns=['REGION', 'STORAGE', 'VALUE'])
    df.to_csv('../src/data/OperationalLifeStorage.csv', index=False)


if __name__ == '__main__':
    main()
