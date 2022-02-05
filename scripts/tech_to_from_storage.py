"""Create technology to and from stroage values"""

import pandas as pd
import functions


def main():
    """Creates TechnologyToStorage and TechnologyFromStorage values. """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    can_subregions = functions.get_from_yaml('regions_dict')['CAN'].keys()
    storages = functions.get_from_yaml('sto_techs')

    # DATA MAPPUING

    if not storages:
        df_out = pd.DataFrame(columns=[
            'REGION', 'TECHNOLOGY', 'STORAGE', 'MODE_OF_OPERATION', 'VALUE'
        ])
        df_out.to_csv('../src/data/TechnologyToStorage.csv', index=False)
        df_out.to_csv('../src/data/TechnologyFromStorage.csv', index=False)
        return

    #TechnologyToStorage (Technology, Storage)
    tech_to_storage = {'TNK': 'P2G'}

    #TechnologyToStorage (Technology, Storage)
    tech_from_storage = {'TNK': 'FCL'}

    #list to hold all output values
    #columns = region, technology, storage, mode, value
    to_storage_data = []
    from_storage_data = []

    #print all values
    for subregion in can_subregions:
        for storage in storages:
            #Tech to storage
            tech_name = 'PWR' + tech_to_storage[storage] + 'CAN' + subregion + '01'
            storage_name = 'STO' + storage + 'CAN' + subregion
            to_storage_data.append([continent, tech_name, storage_name, 1.0, 1])
            #Tech from storage
            tech_name = 'PWR' + tech_from_storage[storage] + 'CAN' + subregion + '01'
            storage_name = 'STO' + storage + 'CAN' + subregion
            from_storage_data.append([continent, tech_name, storage_name, 1.0, 1])

    # WRITING DATA

    # Tech to storage
    df_out = pd.DataFrame(to_storage_data,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'STORAGE',
                              'MODE_OF_OPERATION', 'VALUE'
                          ])
    df_out.to_csv('../src/data/TechnologyToStorage.csv', index=False)

    # Tech from storage
    df_out = pd.DataFrame(from_storage_data,
                          columns=[
                              'REGION', 'TECHNOLOGY', 'STORAGE',
                              'MODE_OF_OPERATION', 'VALUE'
                          ])
    df_out.to_csv('../src/data/TechnologyFromStorage.csv', index=False)


if __name__ == '__main__':
    main()
