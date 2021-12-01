import usa_data_functions

def main():
    # PURPOSE: Creates otoole formatted TotalAnnualMaxCapacity.csv
    # INPUT: none
    # OUTPUT: none

    outputDir = '../src/data/TotalAnnualMaxCapacity.csv'  

    dfUsa = usa_data_functions.getTotalAnnualMaxCapacity()
    dfUsa.to_csv(outputDir, index=False)

if __name__ == "__main__":
    main()