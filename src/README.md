# Folder Contents

## 1. OSeMOSYS Model file 
The OSeMOSYS model, `osemosys_fast.txt`, is a modified version of the original [OSeMOSYS_fast](https://github.com/OSeMOSYS/OSeMOSYS_GNU_MathProg/tree/master/src#installation) code. Specific modifications are outlined in the [wiki](https://github.com/DeltaE/Canada-U.S.-ElecTrade/wiki). 

## 2. Data File 
The data file, `CanadaUSA.txt` holds all data read in during the solving process. 

## 3. data folder 
Contains CSV files that hold all parameter data in seperate files 

## 4. datapackage.json file 
Used by [otoole](https://github.com/OSeMOSYS/otoole) to create the datafile from the folder of CSVs

# Running the Model
To run the model, you will first need to install the [GUN Linear Programming Kit](https://www.gnu.org/software/glpk/). Installation instructions can be found on the [OSeMOSYS repository](https://github.com/OSeMOSYS/OSeMOSYS_GNU_MathProg/tree/master/src#installation). Ensure you follow the optional steps to install [otoole]()https://github.com/OSeMOSYS/otoole and the CBC open-source solver. 

## Dependencies 
### Python Packages 


### Computer Requirements
The base model requires extensive computer resources. 
- 64GB RAM 
- 9hr Run Time using CPLEX 

## How to Run 
1. Navigate to the `/scripts` folder in the command line 
2. Run the command `snakemake <input_argument>` from the command line, replacing `<input_argument>` with  
a.  `dataFile` to generate the file holding all data in .txt format  
b.  `lpFile` to generate the file to input into the solver  
c.  `solveCBC` to generate the input datafiles and solve the model using CPLEX  
d. `solveCPLEX` to generate the input datafiles and solve the model using CPLEX

### Solution Quality 
If using CPLEX to solve the model, the following table will print out at the end of the solve. This table presents the quality and stability of the solution. We consider acceptable condition numbers to be on the order of 1e+9 or less, as described on page 151 of the [CPLEX User’s Manual](https://perso.ensta-paris.fr/~diam/ro/online/cplex/cplex1271_pdfs/usrcplex.pdf). We also consider acceptable Ax-b residual numbers to be no larder then the [feasability tolerance](http://www-eio.upc.edu/lceio/manuals/cplex-11/html/refparameterscplex/refparameterscplex47.html) used to solve the model. By default the feasibility tolerance is set to 1e-06 as described on page 272 of the [CPLEX User’s Manual](https://perso.ensta-paris.fr/~diam/ro/online/cplex/cplex1271_pdfs/usrcplex.pdf). 

Max. unscaled (scaled) bound infeas.        =  
Max. unscaled (scaled) reduced-cost infeas. =  
Max. unscaled (scaled) Ax-b resid.          =  
Max. unscaled (scaled) c-B'pi resid.        =  
Max. unscaled (scaled) |x|                  =  
Max. unscaled (scaled) |slack|              =  
Max. unscaled (scaled) |pi|                 =  
Max. unscaled (scaled) |red-cost|           =  
Condition number of scaled basis            =  

## Viewing Results 
The results will be saved to a `.sol` in a `results/` folder under the root directory. If running through CBC, a folder of CSVs will also be created.

### CPLEX Results
Working with the native solution file from CPLEX is difficult. We opt to use a OSeMOSYS Community user created script to convert the CPLEX result file into one that is the same format as CBC. 

### Jupyter Notebooks 
Visualization scripts can be found in `scripts/postPocessing/`. Scripts will read in the `.sol` file 