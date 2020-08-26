import datetime as dt

## Define a conversion function for the native timestamps in the csv file
def dateparse (time_in_secs):    
    return dt.datetime.fromtimestamp(float(time_in_secs))