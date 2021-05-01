# Canada-U.S.Model Source Folder

## Contents
Inlcuded in this folder are the four items listed below. For more information on OSeMOSYS, see their [GitHub page](https://github.com/OSeMOSYS)

### 1. OSeMOSYS Model file 
The OSeMOSYS model used is the [Alternative Storage Code](https://github.com/OSeMOSYS/OSeMOSYS_GNU_MathProg/releases/tag/AlternateStorageCode_v0.1) version created by T. Niet. 

### 2. Data File 
The data file is generated thorugh [otoole](https://github.com/OSeMOSYS/otoole) using the CSVs in the data folder 

### 3. datapackage.json file 
Used by otoole to create the datafile from the CSVs

### 4. data folder 
Contains all data in CSV fomat to be written to a datafile using [otoole](https://github.com/OSeMOSYS/otoole)

## How to Run 
1. Update the paramter data in the /data folder 
2. Run the otoole command: `otoole convert datapackage datafile datapackage.json <dataFileName.txt>`
3. In the dataFile, remove the parameter `StorageLevelStart`
4. In the dataFile, add the parameter `param default 999999999 : StorageMaxCapacity := ;`
5. Run the model using the command `glpsol -m <modelFile.txt> -d <dataFile.txt>`

NOTE: Steps 3 and 4 are required because the modified model file intoduces the StorageMaxCapacity parameter and removes the default StorageLevelStart parameter. Since otoole does not currently support user added parameters, manually addings/removing the parameters is required. 