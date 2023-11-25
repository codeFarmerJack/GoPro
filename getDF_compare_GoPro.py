import os
import pandas as pd 
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from pandas.tseries.offsets import Second
from scipy.signal import savgol_filter as sgolay
import matplotlib.pyplot as plt 
from gps_time import GPSTime

def formatDateTime(theDateTime):
    global Datetimeformat   #global variable stating 
    return dt.strptime(theDateTime, Datetimeformat)

def getDF(filename):
    df = pd.read_csv(filename, delimiter=',')
    df_len = len(df)
    # to be optimized, now datetime format in function processGPS and processACCL
    for i in range(df_len):
        df.loc[i, 'date'] = formatDateTime(df.loc[i, 'date'][:21]) + timedelta(hours = 8)
    return df, df_len

def processGPS(gps):
    global Vspeed_orig
    global SampleRate
    
    gps["date"] = pd.to_datetime(gps["date"])
    gps["Vspeed_orig_filt"] = sgolay(gps[Vspeed_orig], 10, 1)               # (function) sgolay: (x, window_length, polyorder)
    accl = sgolay(np.gradient(gps["Vspeed_orig_filt"]) * SampleRate, 10, 1) # (function) sgolay: (x, window_length, polyorder)
    jerk = np.gradient(accl) * SampleRate
    gps["accl"] = accl
    gps["jerk"] = sgolay(jerk, 10, 1)
    gps["Vspeed"] = gps["Vspeed_orig_filt"] * 3.6
    
    return gps

def processACCL(accl):
    
    accl["date"] = pd.to_datetime(accl["date"])
    accl["g_lateral"]       = sgolay(accl["1"], 10, 1)                          # (function) sgolay: (x, window_length, polyorder)
    accl["g_longtitudinal"] = sgolay(accl["2"], 10, 1)                          # (function) sgolay: (x, window_length, polyorder)
    accl["g_z"]             = sgolay(accl["Accelerometer [m/s2]"], 10, 1)       # (function) sgolay: (x, window_length, polyorder)
    
    return accl

def processRT(rt):
    """global variable stating"""
    global SampleRate
    global data_date
    global data_dateRT
    global Vspeed
    global VspeedRT
    global accelerationLongi
    global accelerationLongiRT
    global accelerationLateral
    global accelerationLateralRT
    global jerk
    global jerkRT
    
    rt.loc[:, data_date] = rt[data_dateRT].apply(lambda x: dt.fromtimestamp(x))
    rt[jerkRT] = np.gradient(rt[accelerationLongiRT]) * SampleRate
    rt[jerkRT] = sgolay(rt[jerkRT], 10, 1)      # # (function) sgolay: (x, window_length, polyorder)
    rt.rename(columns = {VspeedRT:Vspeed, accelerationLongiRT:accelerationLongi, accelerationLateralRT:accelerationLateral, jerkRT:jerk}, inplace = True)
    
    return rt

def plotFigure(df):
    l = 4
    plt.figure(figsize = (15, 20))
    
    plt.subplot(l, 1, 1)
    plt.plot(df["date"], df["Vspeed"], label = "speed")
    plt.plot(df["date"], df["VspeedRT"], label = "RT")
    plt.legend(fontsize = 5)
    plt.legend(loc = 'upper left')
    
    plt.subplot(l, 1, 2)
    plt.plot(df["date"], df["accelerationLongi"], label = "accl_GoPro")
    plt.plot(df["date"], df["accelerationLongiRT"], label = "accl_RT")
    plt.legend(fontsize = 5)
    plt.legend(loc = 'upper left')
    
    plt.subplot(l, 1, 3)
    plt.plot(df["date"], df["jerk"], label = "jerk_GoPro")
    plt.plot(df["date"], df["jerkRT"], label = "jerk_RT")
    plt.legend(fontsize = 5)
    plt.legend(loc = 'upper left')
    
    plt.subplot(l, 1, 4)
    plt.plot(df["date"], df["accelerationLateral"], label = "accelerationLateral_GoPro")
    plt.plot(df["date"], df["accelerationLateralRT"], label = "accelerationLateral_RT")
    plt.legend(fontsize = 5)
    plt.legend(loc = 'upper left')
    
    plt.show()
    
def plotFigure_Twin(df):
    """global variable stating"""
    global data_date
    global Vspeed
    global accelerationLongi
    global accelerationLateral
    global jerk
    
    l = 3
    plt.figure(figsize = (15, 20))
    
    plt.subplot(l, 1, 1)
    plt.plot(df[data_date], df[Vspeed], label = "speed")
    plt.legend(fontsize = 15)
    plt.xlabel('Time')
    plt.ylabel('Vspeed', color = 'b')
    plt.tick_params(axis = 'y', labelcolor = 'b')
    plt.legend(loc = 'upper left')
    ax2 = plt.twinx()
    ax2.plot(df[data_date], df[accelerationLongi], 'r', label = 'accelerationLongi')
    plt.axhline(y = 0, c = 'r', ls = "--")
    plt.axhline(y = 2, c = 'r', ls = "--")
    plt.axhline(y = -2, c = 'r', ls = "--")
    plt.axhline(y = 4, c = 'r', ls = "--")
    plt.axhline(y = -4, c = 'r', ls = "--")
    ax2.set_ylabel('accl_longi.', color = 'r')
    plt.tick_params(axis = 'y', labelcolor = 'r')
    plt.legend(loc = 'upper right')
    
    plt.subplot(l, 1, 2)
    plt.plot(df[data_date], df[Vspeed], label = "speed")
    plt.legend(fontsize = 15)
    plt.xlabel('Time')
    plt.ylabel('Vspeed', color = 'b')
    plt.tick_params(axis = 'y', labelcolor = 'b')
    plt.legend(loc = 'upper left')
    ax2 = plt.twinx()
    ax2.plot(df[data_date], df[jerk], 'r', label = 'jerk')
    plt.axhline(y = 0, c = 'r', ls = "--")
    plt.axhline(y = 2, c = 'r', ls = "--")
    plt.axhline(y = -2, c = 'r', ls = "--")
    ax2.set_ylabel('jerk', color = 'r')
    plt.tick_params(axis = 'y', labelcolor = 'r')
    plt.legend(loc = 'upper right')
    
    plt.subplot(l, 1, 3)
    plt.plot(df[data_date], df[Vspeed], label = "speed")
    plt.legend(fontsize = 15)
    plt.xlabel('Time')
    plt.ylabel('Vspeed', color = 'b')
    plt.tick_params(axis = 'y', labelcolor = 'b')
    plt.legend(loc = 'upper left')
    ax2 = plt.twinx()
    ax2.plot(df[data_date], df[accelerationLateral], 'r', label = 'accelerationLateral')
    plt.axhline(y = 0, c = 'r', ls = "--")
    plt.axhline(y = 2, c = 'r', ls = "--")
    plt.axhline(y = -2, c = 'r', ls = "--")
    plt.axhline(y = 3, c = 'r', ls = "--")
    plt.axhline(y = -3, c = 'r', ls = "--")
    ax2.set_ylabel('accl_lateral', color = 'r')
    plt.tick_params(axis = 'y', labelcolor = 'r')
    plt.legend(loc = 'upper right')
    
    plt.savefig("plot.png")
    plt.show()
    
#under construction
    """ 
    def mainGoPro(filename):
    counter = 0
    
    df, df_len = getDF(filename)
    df = processGPS(df)
    counter += 1
    temp = df
    if counter > 1:
        pd.concat([df1, df1], ignore_index = True)
        mergedGPS.sort_value("date", ascending = True)
    """
        
#under construction
def getStatistic(df):
    num = 0
    for i in range(len(df)):
        if 2 < abs(df.loc[i, 'g_lateral']) < 3:
            try:
                if 2 < df.loc[i - 1, 'g_lateral'] < 3:
                    pass
                # else
            except:
                pass    # first data no peak
            
if __name__ == '__main__':
    
    SampleRate = 10 #Hz
    Datetimeformat = '%Y-%m-%dT%H:%M:%S.%f'
    Vspeed_orig = "GPS (2D) [m/s]"
    modifiedRTFilename = "R_T_processed.csv"
    mergedDataFilename = "merged_data.csv"
    # mergedGPSFilename = "merged_data_GPS.csv"
    # mergedACCLFilename = "merged_data_ACCL.csv"
    curPath = os.path.abspath(os.curdir)
    counterGPS = 0
    counterACCL = 0
    """----------------------------cloumns definition---------------------------"""
    data_date = "date"
    data_dateRT = "Time (GPS s)"
    Vspeed = "Vspeed"
    VspeedRT = "Speed horizontal (m/s)"
    VspeedGopro = "Vspeed"
    accelerationLongi = "accelerationLongi"
    accelerationLongiRT = "Acceleration forward (m/s^2)"
    accelerationLongiGopro = "accl"
    accelerationLateral = "accelerationLateral"
    accelerationLateralRT = "Acceleration Lateral (m/s^2)"
    accelerationLateralGopro = "g_lateral"
    jerk = "jerk"
    jerkRT = "jerk"
    jerkGopro = "jerk"
    """----------------------------columns definition--------------------------"""
    data_folder_path = "/Users/jackwong/02_Coding/00_repo/01_GoPro/01_Data"
    # Change the current working directory to the specified path
    os.chdir(data_folder_path)
    
    for filename in os.listdir(curPath):
        if filename == mergedDataFilename:
            gopro = pd.read_csv(filename, delimiter = ',', parse_dates = ['date'])
        elif filename == modifiedRTFilename:
            rt = pd.read_csv(filename, delimiter = ',', parse_dates = ['date'])
            rt.rename(columns = {VspeedRT:"VspeedRT", accelerationLongiRT:"accelerationLongiRT", accelerationLateralRT:"acccelerationLateralRT", jerkRT:"jerkRT"}, inplace = True)
            # rt["VspeedRT"] = rt["Vspeed"] * 3.6
            # rt["date"] = rt["date"] + timedelta(days = 365 * 10 + 7)
            # rt["date"] = rt["date"] - timedelta(seconds = 17)
            for i in range(len(rt)):
                rt.loc[i, 'date'] = GPSTime(week_number = 0, time_of_week = rt.loc[i, data_dateRT])
                rt.loc[i, 'date'] = rt.loc[i, 'date'].to_datetime()
                # print(rt.loc[i, 'date'])
            rt["date"] = rt["date"] + timedelta(hours = 8) - timedelta(seconds = 18) 
            rt["date"] = pd.to_datetime(rt["date"])
            # print(rt["date"])
        mergedData = pd.merge(gopro, rt, on = "date")
        plotFigure(mergedData)
        plt.show()
               
            
            