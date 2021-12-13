import pandas as pd

def main():
    # PURPOSE: Creates otoole formatted TotalAnnualMaxCapacity.csv
    # INPUT: none
    # OUTPUT: none

    outputDir = '../src/data/TotalAnnualMaxCapacity.csv'  

    dfUsa = getUsaTotalAnnualMaxCapacity()
    dfUsa.to_csv(outputDir, index=False)

def getUsaTotalAnnualMaxCapacity():
    # PURPOSE: Creates TotalAnnualMaxCapacity header data
    # INPUT:   N/A
    # OUTPUT:  dfOut = dataframe to be written to a csv

    dfOut = pd.DataFrame(columns=['REGION','TECHNOLOGY','YEAR','VALUE'])
    return dfOut

if __name__ == "__main__":
    main()