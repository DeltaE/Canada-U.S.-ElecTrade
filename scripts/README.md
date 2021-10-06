# Canada-U.S.Model Scripts Folder

## Contents
Included in this folder are the scripts used to pre-process, and a folder for post-processing scripts

## Snakemake 
A [snakemake](https://snakemake.readthedocs.io/en/stable/) workflow has been implemented to eaisly create new datafiles when iterating through scenarios. To generate the datafile, run the command:
1. Navigate to the `scripts/` directory in the command line  
2. Execute the command `snakemake dataFile`  
3. Manually replace the datafile parameter StorageLevelStart as described [here](https://github.com/DeltaE/Canada-U.S.-ElecTrade/tree/main/src)  
The snakemake file also lists the relationships between raw data files in the dataSources folder, the scripts, and the processed files in the src/data folder.

## Config
[config.py] Creates Tech and Fuel sets. Writes our files that are referenced by other scripts  // Find more description

## Merging Canada and USA Data
[MergeCanUsaData.py] appends the USA data onto the bottom of Canada data  // Find more description

## Mode List
[mode_list.csv] // Find more description

## Storage Life
[StorageLife.py] // Find more description

## USA Data
[usaData.py] appends the USA data onto the bottom of Canada data // Find more description

## Pre-Processing Scripts
Below are the pre-processing scripts that are run through the snakemake workflow. Each heading lists the parameter that is generated through the script. 

### Availability Factor
- Script: `AvailabilityFactor.py`  
- Purpose: Creates an otoole formatted CSV holding availability factors for Hydro. If Hydro Availability Factors are used, be sure to remove hydro capacity factor  
- DataFiles: `dataSources/Regionalization.csv`. Capacity and Generation Values are hardcoded into the script  

### Capacity Factor
- Script: `CapacityFactor.py`  
- Purpose: Creates an otoole formatted CSV holding capacity for all technologies. If Hydro Capacity Factors are used, be sure to remove hydro availabilty factor  
- DataFiles: `dataSources/Regionalization.csv`,`dataSources/NREL_Costs.csv`, `dataSources/CapacityFactor`. FC and P2G values are hardcoded in  

### Capacity to Activity Unit
- Script: `CapacityToActivity.py`  
- Purpose: Creates otoole formatted CapacityToActivityUnit CSV. Assumes all usints are in GW and PJ  
- DataFiles: `src/data/REGION.csv`. GW -> PJ conversion factor hardcoded in  

### Capital Costs
- Script: `Costs.py` 
- Purpose: Creates an otool formatted CSV holding capital costs. Capital, fixed, and variable costs are all updated with this script
- DataFiles: `src/data/REGION.csv`, `dataSources/NREL_Costs.csv`, `dataSources/P2G_FC_Costs.xlsx` 

### Capital Cost Storage
- Script: `StorageCosts.py`
- Purpose: Creates an otoole formatted CapitalCostStorage CSV
- DataFiles: `src/data/REGION.csv`. Capital Cost hardcoded in

### Emission Activity Ratio
- Script: `EmissionActivityRatio.py`  
- Purpose: Creates otoole formatted Emission Activity Ratio CSV  
- DataFiles: `src/data/REGION.csv`, `dataSources/EmissionActivityRatioByTechnology.csv` 

### Emissions Penalty
- Script: `EmissionPenalty.py`  
- Purpose: Creates otoole formatted EmissionsPenalty CSV  
- DataFiles: `src/data/REGION.csv`, `dataSources/EmissionPenaltyByYear.csv` 

### Fixed Costs
- Script: `Costs.py` 
- Purpose: Creates an otool formatted CSV holding fixed costs. Capital, fixed, and variable costs are all updated with this script
- DataFiles: `src/data/REGION.csv`, `dataSources/NREL_Costs.csv`, `dataSources/P2G_FC_Costs.xlsx`  

### Input Activity Ratio
- Script: `InOutActivityRatio.py`  
- Purpose: Creates otoole formatted InputActivityRatio **AND** OutputActivityRatio CSVs  
- DataFiles: `src/data/REGION.csv`, `dataSources/InputActivityRatioByTechnology.csv`, `dataSources/OutputActivityRatioByTechnology.csv`

### Operational Life
- Script: `ResidualCapacity.py`
- Purpose: Creates an otoole formatted OperationalLife **AND** ResidualCapacity CSVs  
- DataFiles: `dataSources/Regionalization.csv`, `dataSources/OperationalLifeTechnology.csv`, `dataSources/ResidualCapacitiesByProvince`  

### Operational Life Storage
- Script: `StorageCosts.py`
- Purpose: Creates an otoole formatted OperationalLifeStorage CSV
- DataFiles: `src/data/REGION.csv`. Storage Capital Cost Hardcoded in

### Output Activity Ratio
- Script: `InOutActivityRatio.py`  
- Purpose: Creates otoole formatted InputActivityRatio **AND** OutputActivityRatio CSVs  
- DataFiles: `src/data/REGION.csv`, `dataSources/InputActivityRatioByTechnology.csv`, `dataSources/OutputActivityRatioByTechnology.csv`

### Region
- Script: `Regionalization.py`
- Purpose: Creates otoole formatted REGIONS set file
- DataFiles: `dataSource/Regionalization.csv`

### Reserve Margin
- Script: `ReserveMargin.py`  
- Purpose: Creates an otoole formatted ReserveMargin file  
- DataFiles: `dataSources/Regionalization.csv`, `dataSources/ProvincialAnnualDemand.csv`. NERC Reserve margins are hardcoded in   

### Residual Capacity
- Script: `ResidualCapacity.py`  
- Purpose: Creates an otoole formatted OperationalLife **AND** ResidualCapacity CSVs  
- DataFiles: `dataSources/Regionalization.csv`, `dataSources/OperationalLifeTechnology.csv`, `dataSources/ResidualCapacitiesByProvince`  

### RE Tag Technology
- Script: `RETags.py`  
- Purpose: Creates an otoole formatted RETagTechnology CSVs  
- DataFiles: `src/data/REGION.csv`. Technologies hardcoded in  

### Specified Demand Profile 
- Script: `SpecifiedDemandProfile.py`  
- Purpose: Creates an otoole formatted CSV holding the specified demand profile for the model. Accounts for time zones and daylight saving time    
- DataFiles: `dataSources/Regionalization.csv`, `dataSources/ProvincialHourlyLoads.csv`  

### Specified Annual Demand
- Script: `SpecifiedAnnualDemand.py`  
- Purpose: Creates an otoole formatted CSV holding the specified annual demand for the model
- DataFiles: `dataSources/Regionalization.csv`, `dataSources/ProvincialAnnualDemand.csv`

### Technology From Storage
- Script: `TechToFromStorage.py`  
- Purpose: Creates  otoole formatted CSVs holding TechnologyToStorage and TechnologyFromStorage  
- DataFiles: `src/data/REGION.csv`. Technologies hardcoded in  

### Technology To Storage
- Script: `TechToFromStorage.py`  
- Purpose: Creates  otoole formatted CSV holding TechnologyToStorage
- DataFiles: `src/data/REGION.csv`. Technologies hardcoded in

### Variable Costs
- Script: `Costs.py` 
- Purpose: Creates an otool formatted CSV holding variable costs. Capital, fixed, and variable costs are all updated with this script
- DataFiles: `dataSources/NREL_Costs.csv`, `dataSources/P2G_FC_Costs.xlsx` 
