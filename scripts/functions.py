#####################################
## This file is for functions common between multiple files
#####################################

def getLoadValues():
    # PURPOSE: Takes hourly load value excel sheet and converts it into a master df
    # INPUT: none
    # OUTPUT: Dataframe with the columns: Province, Month, Day, Hour, Load Value 
    #Dictionary to hold timezone shifting values 
    timeZone = {
        'BC':0,
        'AB':1,
        'SAS':2,
        'MAN':2,
        'ONT':3,
        'QC':3,
        'NB':4,
        'NL':4,
        'NS':4,
        'PEI':4}

    #Read in all provinces
    sourceFile = '../dataSources/ProvincialHourlyLoads.xlsx'
    sheets = pd.read_excel(sourceFile, sheet_name=None)

    #Will store output information with the columns...
    #Province, month, hour, load [MW]
    data = []

    #Loop over sheets and store in a master list 
    for province, sheet in sheets.items():
        dateList = sheet['Date'].tolist()
        hourList = sheet['HOUR (LOCAL)'].tolist()
        loadList = sheet['LOAD [MW]'].tolist()

        #loop over list and break out month, day, hour from date
        for i in range(len(dateList)):
            dateFull = dateList[i]
            date = datetime.datetime.strptime(dateFull, '%Y-%m-%d')

            #Shift time values to match BC time (ie. Shift 3pm Alberta time back one hour, so all timeslices represent the asme time)
            hourAdjusted = int(hourList[i]) - timeZone[province]
            if hourAdjusted < 1:
                hourAdjusted = hourAdjusted + 24

            #Save data
            data.append([province, date.month, date.day, hourAdjusted, loadList[i]])

    #process daylight savings time values 
    data = daylightSavings(data)

    #dataframe to output 
    dfOut = pd.DataFrame(data,columns = ['PROVINCE','MONTH','DAY','HOUR','VALUE'])
    return dfOut
