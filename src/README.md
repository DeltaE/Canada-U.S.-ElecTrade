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

### Using GLPK
5. Run the model using the command `glpsol -m <modelFile.txt> -d <dataFile.txt>`

### Using CPLEX
5. Create a .lp file using GLPK using the command `glpsol --wlp <outputFile.lp> --check -m <modelFile.txt> -d <dataFile.txt>`
6. Open CPLEX thorugh the command `CPLEX`
7. Read in the .lp file using `read <outputFile.lp>`
8. Solve the model using `optimize`

NOTE: Steps 3 and 4 are required because the modified model file intoduces the StorageMaxCapacity parameter and removes the default StorageLevelStart parameter. Since otoole does not currently support user added parameters, manually addings/removing the parameters is required. 

## Solution Quality 
To check the solution quality, the model is first solved using CPLEX following "How to Run" steps 5 thru 8. Once the model has been optimized, the command `check solution quality` is run. CPLEX will return the following list of numbers: 

Max. unscaled (scaled) bound infeas.        =  
Max. unscaled (scaled) reduced-cost infeas. =  
Max. unscaled (scaled) Ax-b resid.          =  
Max. unscaled (scaled) c-B'pi resid.        =  
Max. unscaled (scaled) |x|                  =  
Max. unscaled (scaled) |slack|              =  
Max. unscaled (scaled) |pi|                 =  
Max. unscaled (scaled) |red-cost|           =  
Condition number of scaled basis            =  

### Condition Number  
We consider acceptable condition numbers on the order of 1e+9 or less. See page 151 of the [CPLEX User’s Manual](https://perso.ensta-paris.fr/~diam/ro/online/cplex/cplex1271_pdfs/usrcplex.pdf)

### Ax-b Residual
We consider acceptable Ax-b residual numbers to be no larder then the feasibility tolerance used to solve the model. See page 272 of the [CPLEX User’s Manual]. By default the [feasability tolerance](http://www-eio.upc.edu/lceio/manuals/cplex-11/html/refparameterscplex/refparameterscplex47.html) is set to 1e-06. 
