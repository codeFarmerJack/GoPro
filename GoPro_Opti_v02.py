import os
import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

def butter_lowpass_filter(data, cutoff_freq, sample_rate, order=4):
    nyquist = 0.5 * sample_rate     
    normal_cutoff = cutoff_freq / nyquist   
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

# dataOpt is designed to remove noises through butter-worth-filter
#   rawData: the signal that contains noises
#   speed: polluted speed
#   accLon: polluted longitudinal speed 
#   accLat: polluted lateral speed
#   jerk: polluted jerk
def dataOpt(rawData, speed, accLong, accLat, jerk):
    
    cutoff_freq = 0.07      # Adjust this cutoff frequency as needed

    # Filter the raw data 
    VspeedOpt = butter_lowpass_filter(rawData[speed], cutoff_freq, SampleRate, order=3)
    acclLongOptFilt = butter_lowpass_filter(rawData[accLong], cutoff_freq, SampleRate, order=3)
    acclLatOptFilt = butter_lowpass_filter(rawData[accLat], cutoff_freq, SampleRate, order=3)
    jerkOptFilt = butter_lowpass_filter(rawData[jerk], cutoff_freq, SampleRate, order=3)
    VspeedOptKPH = VspeedOpt * 3.6

    # insert to the original DataFrame
    rawData.insert(loc=len(rawData.columns), column = 'VspeedOpt', value=VspeedOpt)
    rawData.insert(loc=len(rawData.columns), column = 'acclLongOptFilt', value=acclLongOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'acclLatOptFilt', value=acclLatOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'jerkOptFilt', value=jerkOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'VspeedOptKPH', value=VspeedOptKPH)
    
    return rawData 

def custom_date_parser(x):
    return pd.to_datetime(x, format = '%H:%M:%S', errors='coerce')

def plot_dynamic_subplot(x, *y_data):
    num_plots = len(y_data)

    fig, axes = plt.subplots(num_plots, 1, figsize = (15, 2 * num_plots))

    if num_plots == 1:
        axes = [axes]   # Ensure axes is a list even for a single plot

    for i, (y_value, y_name) in enumerate(y_data):
        axes[i].plot(x, y_value, label = y_name)
        axes[i].set_xlabel('X-axis')
        axes[i].set_ylabel(f'Y-axis {y_name}')
        axes[i].legend()
    
    # Adjust layout to prevent clipping of titles
    plt.tight_layout()

    plt.show()

if __name__ == '__main__':

    # data file sample frequency and name
    SampleRate = 10         # Hz
    modifiedRTFilename = "R_T_processed.csv"
    mergedDataFilename = "merged_data.csv"
    
    # column names in the csv files, list only the signals that interest us
    ## signals of Gopro
    speedGopro = 'Vspeed'
    accLongGopro = 'accelerationLongi'
    accLatGopro = 'accelerationLateral'
    jerkGopro = 'jerk'

    ## signals of Ground Truth
    speedRT = 'Speed horizontal (m/s)'
    accLongRT = 'Acceleration forward (m/s2)'
    accLatRT = "Acceleration lateral (m/s2)"
    jerkRT = "jerkRT"
    
    # data folder path
    data_folder_path = r"C:\AAD\02_Coding\04_python\01_Data"
    os.chdir(data_folder_path)
    
    gopro = None
    rt = None
    # Read data from csv to DataFrame and rename columns names
    for filename in os.listdir():
        # print(filename)
        if filename == mergedDataFilename:
            gopro = pd.read_csv(filename, delimiter=',', converters={'date_01':custom_date_parser})
        elif filename == modifiedRTFilename:
            rt = pd.read_csv(filename, delimiter=',', converters={'date_01':custom_date_parser})
            # align signals from different files along the time axis
            rt["date_01"] = rt["date_01"] - timedelta(minutes=6) + timedelta(seconds=15)
            
    # Process Gopro with lowpass filter
    optimizedGopro = dataOpt(gopro, speedGopro, accLongGopro, accLatGopro, jerkGopro)
    optimizedRT = dataOpt(rt, speedRT, accLongRT, accLatRT, jerkRT)

    plot_dynamic_subplot(optimizedRT['date_01'], optimizedRT[accLatRT], optimizedRT['acclLatOptFilt'])


    """plt.figure(1)
    plt.figure(figsize=(15, 20))

    plt.subplot(3,1,1)
    plt.plot(optimizedGopro["date_01"], optimizedGopro[accLatGopro], label="acclLateral")
    plt.plot(optimizedGopro["date_01"], optimizedGopro['acclLatOptFilt'], label="acclLatOptFilt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(3,1,2)
    plt.plot(rt["date_01"], rt[accLatRT], label="accelerationLateralRT")
    plt.plot(optimizedRT["date_01"], optimizedRT['acclLatOptFilt'], label="acclLatOptFiltRT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(3,1,3)
    plt.plot(optimizedGopro["date_01"], optimizedGopro['acclLatOptFilt'], label="acclLatOptFilt")
    plt.plot(optimizedRT["date_01"], optimizedRT['acclLatOptFilt'], label="acclLatOptFiltRT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.show()"""
    
    # Base comparison
    if gopro is not None and rt is not None:
        mergedData = pd.merge(gopro, rt, on="date_01", how='inner')
        # plot the base comparision
        
        # plotFigure(mergedData, VspeedGopro, accelerationLongiGopro, accelerationLateralGopro, jerkGopro)
        # plt.show()

        # plot the optimized comparision
        # mergedDataOpt = pd.merge(optimized, rt, on='date_01', how='inner')
        # print(mergedDataOpt.columns)
        # plotFigure(mergedDataOpt, mergedDataOpt['VspeedOpt'], mergedDataOpt['acclLongOptFilt'],mergedDataOpt['acclLatOptFilt'],
        #            mergedDataOpt['jerkOptFilt'])
        # plt.show()
    