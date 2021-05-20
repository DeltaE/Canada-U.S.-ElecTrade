# Canada-U.S.Model Scripts Folder

## Contents
Inlcuded in this folder are the scripts used to pre-process and post-process data 

## Pre-Processing Scripts

### Availability Factor
- Script: `AvailabilityFactor.py`  
- Purpose: Creates an otoole formatted CSV holding availability factors for Hydro. If Hydro Availability Factors are used, be sure to remove hydro capacity factor  
- DataFiles: None. Capacity and Generation Values are hardcoded into the script  

### Capacity Factor
- Script: `CapacityFactor.py`  
- Purpose: Creates an otoole formatted CSV holding capacity for all technologies. If Hydro Capacity Factors are used, be sure to remove hydro availabilty factor  
- DataFiles: `dataSources/NREL_Costs.csv`, `dataSources/CapacityFactor`. FC and P2G values are hardcoded in  

### Specified Demand Profile 
- Script: `SpecifiedDemandProfile.py`  
- Purpose: Creates an otoole formatted CSV holding the specified demand profile for the model. Accounts for time zones and daylight saving time    
- DataFiles: `dataSources/ProvincialHourlyLoads.csv`  

### Specified Annual Demand
- Script: `SpecifiedAnnualDemand.py`  
- Purpose: Creates an otoole formatted CSV holding the specified annual demand for the model
- DataFiles: `dataSources/ProvincialAnnualDemand.csv`

### Capital Costs
- Script: `Costs.py` 
- Purpose: Creates an otool formatted CSV holding capital costs. A user parameter changes if you print capital, fixed, or variable costs  
- DataFiles: `dataSources/NREL_Costs.csv`, `dataSources/P2G_FC_Costs.xlsx` 

### Fixed Costs
- Script: `Costs.py` 
- Purpose: Creates an otool formatted CSV holding fixed costs. A user parameter changes if you print capital, fixed, or variable costs  
- DataFiles: `dataSources/NREL_Costs.csv`, `dataSources/P2G_FC_Costs.xlsx`  

### Variable Costs
- Script: `Costs.py` 
- Purpose: Creates an otool formatted CSV holding variable costs. A user parameter changes if you print capital, fixed, or variable costs  
- DataFiles: `dataSources/NREL_Costs.csv`, `dataSources/P2G_FC_Costs.xlsx` 

### Residual Capacity
- Script: `ResidualCapacity.py`
- Purpose: Creates an otoole formatted OperationalLife **AND** ResidualCapacity CSVs  
- DataFiles: `dataSources/OperationalLifeTechnology.csv`, `dataSources/ResidualCapacitiesByProvince`  

### Input Activity Ratio
- Script: `InOutActivityRatio.py`  
- Purpose: Creates otoole formatted InputActivityRatio **AND** OutputActivityRatio CSVs  
- DataFiles: `dataSources/InputActivityRatioByTechnology.csv`, `dataSources/OutputActivityRatioByTechnology.csv`

### Output Activity Ratio
- Script: `InOutActivityRatio.py`  
- Purpose: Creates otoole formatted InputActivityRatio **AND** OutputActivityRatio CSVs  
- DataFiles: `dataSources/InputActivityRatioByTechnology.csv`, `dataSources/OutputActivityRatioByTechnology.csv`

### Capacity to Activity Unit
- Script: `CapacityToActivity.py`  
- Purpose: Creates otoole formatted CapacityToActivityUnit CSV. Assumes all usints are in GW and PJ  
- DataFiles: None. GW -> PJ conversion factor hardcoded in  

### Emission Activity Ratio
- Script: `EmissionActivityRatio.py`  
- Purpose: Creates otoole formatted Emission Activity Ratio CSV  
- DataFiles: `dataSources/EmissionActivityRatioByTechnology.csv`  

### Reserve Margin
- Script: `ReserveMargin.py`
- Purpose: Creates an otoole formatted ReserveMargin file
- DataFiles: None. Reserve margins are hardcoded in 

### Capital Cost Storage
- Script: `StorageCosts.py`
- Purpose: Creates an otoole formatted CapitalCostStorage CSV
- DataFiles: None. Capital Cost hardcoded in

### Operational Life Storage
- Script: `StorageCosts.py`
- Purpose: Creates an otoole formatted OperationalLifeStorage CSV
- DataFiles: None. Storage Capital Cost Hardcoded in

## Post-Processing Scripts

`W_ProductionAndDemandNOTrade_24_extended.py`