# Canada-U.S.Model Scripts Folder

## Contents
Included in this folder are the scripts used to pre-process, and a folder for post-processing scripts

## Snakemake 
A [snakemake](https://snakemake.readthedocs.io/en/stable/) workflow has been implemented to eaisly create new datafiles when iterating through scenarios. To generate the datafile, follow the instructions found here: https://github.com/DeltaE/Canada-U.S.-ElecTrade/tree/main/src

The snakemake file also lists the relationships between raw data files in the dataSources folder, the scripts, and the processed files in the src/data folder.

## Config
[config.py] Creates Tech and Fuel sets. Writes our files that are referenced by other scripts  // Find more description

## Mode List
[mode_list.csv] // Find more description
