import os
import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from gps_time import GPSTime

def formatDateTime(theDateTime):
    global Datetimeformat   # global variable stating 
    return dt.strptime(theDateTime, Datetimeformat)

def getDF(filename):
    df = pd.read_csv(filename, delimiter=',')
    df_len = len(df)
    
    for i in range(df_len):
        df.loc[i, 'date'] = formatDateTime(df.loc[i, 'date'][:21]) + timedelta(hours=8)
    
    return df, df_len

def butterworth_filter(data, sample_rate, cutoff_freq, filter_type='low', order=4):
    nyquist_freq = 0.5 * sample_rate
    normalized_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff, btype=filter_type, analog=False)
    return filtfilt(b, a, data)

def processGPS(gps):
    global Vspeed_orig
    global SampleRate
    
    gps["date"] = pd.to_datetime(gps["date"])
    
    # Replace sgolay filter with Butterworth filter
    cutoff_freq = 0.5  # Adjust this cutoff frequency as needed
    gps["Vspeed_orig_filt"] = butterworth_filter(gps[Vspeed_orig], SampleRate, cutoff_freq, filter_type='low')

    accl = butterworth_filter(np.gradient(gps["Vspeed_orig_filt"]) * SampleRate, SampleRate, cutoff_freq, filter_type='low')
    jerk = np.gradient(accl) * SampleRate
    
    gps["accl"] = accl
    gps["jerk"] = butterworth_filter(jerk, SampleRate, cutoff_freq, filter_type='low')
    gps["Vspeed"] = gps["Vspeed_orig_filt"] * 3.6
    
    return gps

def processACCL(accl):
    accl["date"] = pd.to_datetime(accl["date"])
    accl["g_lateral"] = butterworth_filter(accl["1"], 10, 0.5, filter_type='low')
    accl["g_longtitudinal"] = butterworth_filter(accl["2"], 10, 0.5, filter_type='low')
    accl["g_z"] = butterworth_filter(accl["Accelerometer [m/s2]"], 10, 0.5, filter_type='low')
    
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
    
    print("processRT function is called!")
    
    rt.loc[:, data_date] = rt[data_dateRT].apply(lambda x: dt.fromtimestamp(x))
    rt[jerkRT] = np.gradient(rt[accelerationLongiRT]) * SampleRate
    rt[jerkRT] = butterworth_filter(rt[jerkRT], SampleRate, 0.5, filter_type='low')
    rt.rename(columns={VspeedRT: Vspeed, accelerationLongiRT: accelerationLongi, 
                       accelerationLateralRT: accelerationLateral, jerkRT: jerk}, inplace=True)
    
    return rt

def plotFigure(df):
    l = 4
    print("Inside plotFigure function")

    plt.figure(figsize=(15, 20))
    
    print("Before subplot 1")
    plt.subplot(l, 1, 1)
    print("After subplot 1")
    plt.plot(df["date"], df["Vspeed"], label="speed")
    
    # Check if columns are present before attempting to plot
    if "VspeedRT" in df.columns:
        plt.plot(df["date"], df["VspeedRT"], label="RT")
    
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')
    
    print("Before subplot 2")
    plt.subplot(l, 1, 2)
    print("After subplot 2")
    
    # Add print statements to inspect data
    print("Printing data for accelerationLongi subplot:")
    print(df[["date", "accelerationLongi", "accelerationLongiRT"]].head())
    
    # Check if columns are present before attempting to plot
    if "accelerationLongi" in df.columns and "accelerationLongiRT" in df.columns:
        plt.plot(df["date"], df["accelerationLongi"], label="accl_GoPro")
        plt.plot(df["date"], df["accelerationLongiRT"], label="accl_RT")
    
    print("Before subplot 3")
    plt.subplot(l, 1, 3)
    print("After subplot 3")
    
    # Check if columns are present before attempting to plot
    if "jerk" in df.columns and "jerkRT" in df.columns:
        plt.plot(df["date"], df["jerk"], label="jerk_GoPro")
        plt.plot(df["date"], df["jerkRT"], label="jerk_RT")
    
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')
    
    print("Before subplot 4")
    plt.subplot(l, 1, 4)
    print("After subplot 4")
    
    # Check if columns are present before attempting to plot
    if "accelerationLateral" in df.columns and "accelerationLateralRT" in df.columns:
        plt.plot(df["date"], df["accelerationLateral"], label="accelerationLateral_GoPro")
        plt.plot(df["date"], df["accelerationLateralRT"], label="accelerationLateral_RT")
    
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')
    
    print("Before show")
    plt.show()
    print("After show")

# Rest of the code remains unchanged


"""
# under construction
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
"""

if __name__ == '__main__':
    print("Step1: Script execution started!!")
    SampleRate = 10  # Hz
    Datetimeformat = '%Y-%m-%dT%H:%M:%S.%f'
    Vspeed_orig = "GPS (2D) [m/s]"
    modifiedRTFilename = "R_T_processed.csv"
    mergedDataFilename = "merged_data.csv"
    # curPath = os.path.abspath(os.curdir)
    counterGPS = 0
    counterACCL = 0
    
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
    
    data_folder_path = "/Users/jackwong/02_Coding/00_repo/01_GoPro/01_Data"
    os.chdir(data_folder_path)
    
    gopro = None
    
    for filename in os.listdir():
        # print(filename)
        if filename == mergedDataFilename:
            gopro = pd.read_csv(filename, delimiter=',', parse_dates=['date'])
        elif filename == modifiedRTFilename:
            rt = pd.read_csv(filename, delimiter=',', parse_dates=['date'])
            rt.rename(columns={VspeedRT: "VspeedRT", accelerationLongiRT: "accelerationLongiRT",
                               accelerationLateralRT: "acccelerationLateralRT", jerkRT: "jerkRT"}, inplace=True)
            for i in range(len(rt)):
                rt.loc[i, 'date'] = GPSTime(week_number=0, time_of_week=rt.loc[i, data_dateRT])
                rt.loc[i, 'date'] = rt.loc[i, 'date'].to_datetime()
            rt["date"] = rt["date"] + timedelta(hours=8) - timedelta(seconds=18)
            rt["date"] = pd.to_datetime(rt["date"])
            
    print("Step2: Execution After the for loop")
    if gopro is not None:
        print("Columns in gopro DataFrame:")
        print(gopro.columns)
        
        mergedData = pd.merge(gopro, rt, on="date")
        
        print("Columns in mergedData DataFrame:")
        print(mergedData.columns)
        
        plotFigure(mergedData)
        plt.show()