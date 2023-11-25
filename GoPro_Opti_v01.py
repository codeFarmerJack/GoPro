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
    return pd.to_datetime(theDateTime, format='%H:%M:%S', errors='coerce')

def getDF(filename):
    df = pd.read_csv(filename, delimiter=',', parse_dates=['date_01'])
    df["date_01"] = pd.to_datetime(df["date_01"], format='%H:%M:%S', errors='coerce')
    
    df_len = len(df)
    
    for i in range(df_len):
        df.loc[i, 'date_01'] = formatDateTime(df.loc[i, 'date_01'])
    return df

def butter_lowpass_filter(data, cutoff_freq, sample_rate, order=4):
    nyquist = 0.5 * sample_rate     
    normal_cutoff = cutoff_freq / nyquist   
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def dataOpt(rawData):

    global SampleRate
    global VspeedGopro
    global accelerationLongiGopro
    global accelerationLateralGopro
    global jerkGopro
    
    cutoff_freq = 0.07      # Adjust this cutoff frequency as needed

    # Filter the raw data 
    VspeedOpt = butter_lowpass_filter(rawData[VspeedGopro], cutoff_freq, SampleRate, order=3)
    
    # acclLongOptGrad = np.gradient(rawData[VspeedGopro]) * SampleRate
    # print(acclLongOptGrad[:5])
    
    acclLongOptFilt = butter_lowpass_filter(rawData[accelerationLongiGopro], cutoff_freq, SampleRate, order=3)
    
    acclLatOptFilt = butter_lowpass_filter(rawData[accelerationLateralGopro], cutoff_freq, SampleRate, order=3)
    # jerkOptGrad = np.gradient(rawData["acclLongOptFilt"]) * SampleRate
    jerkOptFilt = butter_lowpass_filter(rawData[jerkGopro], cutoff_freq, SampleRate, order=3)
    VspeedOptKPH = VspeedOpt * 3.6


    
    # insert to the original DataFrame
    # rawData.insert(loc=len(rawData.columns), column = 'VspeedOpt', value=VspeedOpt)
    # rawData.insert(loc=len(rawData.columns), column = 'acclLongOptGrad', value=acclLongOptGrad)
    rawData.insert(loc=len(rawData.columns), column = 'acclLongOptFilt', value=acclLongOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'acclLatOptFilt', value=acclLatOptFilt)
    # rawData.insert(loc=len(rawData.columns), column = 'jerkOptGrad', value=jerkOptGrad)
    rawData.insert(loc=len(rawData.columns), column = 'jerkOptFilt', value=jerkOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'VspeedOptKPH', value=VspeedOptKPH)
    
    return rawData 


def plotFigure(df, col1, col2, col3, col4):

    # col1 corresponds to "speed"
    # col2 corresponds to "accelerationLongi"
    # col3 corresponds to "accelerationLat"
    # col4 corresponds to "jerk"

    l = 4       # number of subplots
    plt.figure(figsize=(15, 20))

    plt.subplot(l, 1, 1)
    plt.plot(df["date_01"], df[col1], label="speed")                                # col 1 = Vspeed
    # Check if columns are present before attempting to plot
    if "VspeedRT" in df.columns:
        plt.plot(df["date_01"], df["VspeedRT"], label="RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')
    
    plt.subplot(l, 1, 2)
    # Check if columns are present before attempting to plot
    if "accelerationLongi" in df.columns and "accelerationLongiRT" in df.columns:
        plt.plot(df["date_01"], df[col2], label="accl_GoPro")                       # col2 = accelerationLongi
        plt.plot(df["date_01"], df["accelerationLongiRT"], label="accl_RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(l, 1, 3)
    # Check if columns are present before attempting to plot
    if "accelerationLateral" in df.columns and "accelerationLateralRT" in df.columns:
        plt.plot(df["date_01"], df[col3], label="accelerationLateral_GoPro")        # col3 = accelerationLateral
        plt.plot(df["date_01"], df["accelerationLateralRT"], label="accelerationLateral_RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(l, 1, 4)   
    # Check if columns are present before attempting to plot
    if "jerk" in df.columns and "jerkRT" in df.columns:
        plt.plot(df["date_01"], df[col4], label="jerk_GoPro")                       # col 4 = jerk
        plt.plot(df["date_01"], df["jerkRT"], label="jerk_RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')


    plt.show()

def custom_date_parser(x):
    return pd.to_datetime(x, format = '%H:%M:%S', errors='coerce')


if __name__ == '__main__':
    # data file sample frequency and name
    SampleRate = 10         # Hz
    modifiedRTFilename = "R_T_processed.csv"
    mergedDataFilename = "merged_data.csv"
    RawDataGopro = 'RawDataGopro.csv'
    RawDataRT = 'RawDataRT.csv'
    # curPath = os.path.abspath(os.curdir)
    counterGPS = 0
    counterACCL = 0
    
    # column names in the csv files
    Datetimeformat = '%H:%M:%S'     # HH:MM:microseconds
    # Vspeed_orig = "GPS (2D) [m/s]"
    # data_date = "date"
    # data_dateRT = "Time (GPS s)"
    VspeedRT = "Speed horizontal (m/s)"
    VspeedGopro = "Vspeed"
    accelerationLongiRT = "Acceleration forward (m/s2)"
    accelerationLongiGopro = "accelerationLongi"
    # accelerationLongiGopro = "accl"
    accelerationLateralRT = "Acceleration lateral (m/s2)"
    accelerationLateralGopro = "accelerationLateral"
    # accelerationLateralGopro = "g_lateral"
    # jerk = "jerk"
    jerkRT = "jerkRT"
    jerkGopro = "jerk"
    
    # data folder path
    data_folder_path = r"C:\AAD\02_Coding\04_python\01_Data"
    os.chdir(data_folder_path)
    
    gopro = None
    rt = None
    # Read data from csv to DataFrame and rename columns names
    for filename in os.listdir():
        # print(filename)
        if filename == RawDataGopro:
            # gopro = getDF(filename)
            gopro = pd.read_csv(filename, delimiter=',', converters={'date_01':custom_date_parser}, 
                                dtype={'accelerationLateral':'float64'})
            gopro["date_01"] = pd.to_datetime(gopro["date_01"], format='%H:%M:%S', errors='coerce')
            # print(gopro["date_01"].head())
            # gopro.rename(columns={VspeedGopro: "Vspeed", accelerationLongiGopro: "accelerationLongi",
            #                    accelerationLateralGopro: "accelerationLateral", jerkGopro: "jerk"}, inplace=True)
            gopro.rename(columns={accelerationLateralGopro:'accelerationLaterGopro'})

        elif filename == RawDataRT:
            # rt = getDF(filename)
            rt = pd.read_csv(filename, delimiter=',', converters={'date_01':custom_date_parser}, 
                             dtype={'Acceleration lateral (m/s2)':'float64'})

            rt["date_01"] = pd.to_datetime(rt["date_01"], format='%H:%M:%S', errors='coerce')
            # print(rt["date_01"].head())
            # rt.rename(columns={VspeedRT: "VspeedRT", accelerationLongiRT: "accelerationLongiRT",
            #                   accelerationLateralRT: "accelerationLateralRT", jerkRT: "jerkRT"}, inplace=True)
            
            # rt.rename(columns={accelerationLateralRT:'accelerationLateralRT'})

            # for i in range(len(rt)):
            #    rt.loc[i, 'date_01'] = GPSTime(week_number=0, time_of_week=rt.loc[i, data_dateRT])
            #    rt.loc[i, 'date_01'] = rt.loc[i, 'date_01'].to_datetime()
            
            # align signals from different files along the time axis
            rt["date_01"] = rt["date_01"] - timedelta(minutes=6) + timedelta(seconds=15)
            # rt["date_01"] = pd.to_datetime(rt["date_01"], format=Datetimeformat)
            
    # Process Gopro with lowpass filter
    optimized = dataOpt(gopro)
    """
    plt.figure(figsize=(15, 20))
    plt.plot(optimized["date_01"], optimized['acclLatOptFilt'], label="acclLatOptFilt") 
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    """
    """plt.figure(figsize=(15, 20))
    plt.plot(optimized["date_01"], optimized['acclLongOptFilt'], label="AccelerationLongOpt") 
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')
    """
    # Base comparison
    if gopro is not None and rt is not None:
        mergedData = pd.merge(gopro, rt, on="date_01")
        # plot the base comparision
        # plotFigure(mergedData, VspeedGopro, accelerationLongiGopro, accelerationLateralGopro, jerkGopro)
        # plt.show()

        # plot the optimized comparision
        mergedDataOpt = pd.merge(optimized, rt, on='date_01')
        print(mergedDataOpt.columns)
        plotFigure(mergedDataOpt, mergedDataOpt['VspeedOpt'], mergedDataOpt['acclLongOptFilt'],mergedDataOpt['acclLatOptFilt'],
                   mergedDataOpt['jerkOptFilt'])
        plt.show()
