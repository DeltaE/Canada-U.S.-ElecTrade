# Canada-U.S.Model Scripts Folder

## Contents
Inlcuded in this folder are the scripts used to pre-process and post-process data 

## Pre-Processing Scripts

`AvailabilityFactor.py`  
Creates an otoole formatted CSV holding availability factors for Hydro. If Hydro Availability Factors are used, be sure to remove hydro capacity factor 

`CapacityFactor.py`  
Creates an otoole formatted CSV holding capacity factors for Solar, Wind, Hydro and Gas. If Hydro Capacity Factors are used, be sure to remove hydro availabilty factor

`SpecifiedDemandProfile.py`  
Creates an otoole formatted CSV holding the specified demand profile for the model. Accounts for time zones and daylight saving time

`SpecifiedAnnualDemand.py`  
Creates an otoole formatted CSV holding the specified annual demand for the model

`Costs.py`  
Creates an otool formatted CSV holding capital costs, fixed costs, OR variable costs. The script does NOT update all three files during one run. There is a user parameter inside the script to change what file to update. 

`ResidualCapacity.py`
Creates otoole formatted OperationalLife and ResidualCapacity CSVs

## Post-Processing Scripts

`W_ProductionAndDemandNOTrade_24_extended.py`