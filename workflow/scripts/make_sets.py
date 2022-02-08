"""Generates set files"""

import pandas as pd
import functions
from pathlib import Path


def main():
    """Generates all otoole formatted set files.
    """

    # PARAMETERS

    continent = functions.get_from_yaml('continent')
    emissions = functions.get_from_yaml('emissions')
    techs_master = functions.get_from_yaml('techs_master')
    rnw_fuels = functions.get_from_yaml('rnw_fuels')
    mine_fuels = functions.get_from_yaml('mine_fuels')
    sto_techs = functions.get_from_yaml('sto_techs')
    subregions = functions.get_from_yaml('regions_dict')
    years = functions.get_years()

    # WRITING SETS

    # Years set
    df_out = pd.DataFrame(years, columns=['VALUE'])
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/YEAR.csv')
    df_out.to_csv(output_dir, index=False)

    #Regions set
    df_out = pd.DataFrame([continent], columns=['VALUE'])
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/REGION.csv')
    df_out.to_csv(output_dir, index=False)

    # Emissions set
    df_out = pd.DataFrame(emissions, columns=['VALUE'])
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/EMISSION.csv')
    df_out.to_csv(output_dir, index=False)

    # Technology set
    df_out = functions.create_tech_df(subregions, techs_master,
                                           mine_fuels, rnw_fuels,
                                           'Trade.csv')
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/TECHNOLOGY.csv')
    df_out.to_csv(output_dir, index=False)

    # Fuel set
    df_out = functions.create_fuel_df(subregions, rnw_fuels, mine_fuels)
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/FUEL.csv')
    df_out.to_csv(output_dir, index=False)

    # Storage set
    storage_list = get_storages(subregions, sto_techs)
    df_out = pd.DataFrame(storage_list, columns=['VALUE'])
    output_dir = Path(Path(__file__).resolve().parent,
        '../../results/data/STORAGE.csv')
    df_out.to_csv(output_dir, index=False)

# EXTRA FUNCTIONS

def get_storages(regions, storages):
    """Creates storage names.

    Reads in storage parameters from configuration file and generates
    formatted list of storage name.

    Args:
        regions: Dictionary holding Country and regions
            ({CAN:{WS:[...], ...} USA:[NY:[...],...]})
        storages: names of storage technologies

    Returns:
        out_list: List of all storage names
    """

    # list to hold technologies
    out_list = []

    if not storages:
        return storages

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions['CAN']:
            for storage in storages:
                storage_name = 'STO' + storage + region + subregion
                out_list.append(storage_name)

    # Return list of hydrogen fuels
    return out_list

# pylint: disable=pointless-string-statement
'''
def getHY2fuels(regions):
    # PURPOSE: Creates Hydrogen Fuel names
    # INPUT:   regions =  Dictionary holding region as the key and subregion as the values in a list
    # OUTPUT:  outList =  List of all the ELC Fuels

    # list to hold technologies
    outList = []

    # Loop to create all technology names
    for region, subregions in regions.items():
        for subregion in subregions:
            fuelName = 'HY2' + region + subregion + '01'
            outList.append(fuelName)
    
    # Return list of hydrogen fuels
    return outList
'''

if __name__ == '__main__':
    main()
