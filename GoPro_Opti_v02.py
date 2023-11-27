import os
import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import mplcursors

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
    speedOpt = butter_lowpass_filter(rawData[speed], cutoff_freq, SampleRate, order=3)
    accLongOptFilt = butter_lowpass_filter(rawData[accLong], cutoff_freq, SampleRate, order=3)
    accLatOptFilt = butter_lowpass_filter(rawData[accLat], cutoff_freq, SampleRate, order=3)
    jerkOptFilt = butter_lowpass_filter(rawData[jerk], cutoff_freq, SampleRate, order=3)
    speedOptKPH = speedOpt * 3.6

    # insert to the original DataFrame
    rawData.insert(loc=len(rawData.columns), column = 'speedOpt', value=speedOpt)
    rawData.insert(loc=len(rawData.columns), column = 'accLongOptFilt', value=accLongOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'accLatOptFilt', value=accLatOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'jerkOptFilt', value=jerkOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'speedOptKPH', value=speedOptKPH)
    
    return rawData 

def custom_date_parser(x):
    return pd.to_datetime(x, format = '%H:%M:%S', errors='coerce')

"""
def plot_dynamic_subplot(x, *y_data):
    if len(y_data) % 2 != 0:
        raise ValueError('Number of y_data arguments should be even.')
    
    num_plots = len(y_data) // 2

    fig, axes = plt.subplots(num_plots, 1, sharex = True, figsize = (15, 2 * num_plots))

    if num_plots == 1:
        axes = [axes]   # Ensure axes is a list even for a single plot

    # Plot data on each subplot
    for i in range(0, len(y_data), 2):
        if i % 2 == 0:

        

    # Set common X-axis label
    # axes[-1].set_xlabel('X-axis')
    
    for i, y_value in enumerate(y_data):
        axes[i].plot(x, y_value)
        axes[i].set_xlabel('X-axis')
        axes[i].set_ylabel(f'Y-axis {i + 1}')
        axes[i].legend()
    
    
    # Adjust layout to prevent clipping of titles
    plt.tight_layout()

    # Add labels to data points 
    mplcursors.cursor(axes).connect('add', 
                                    lambda sel: sel.annotation.set_text(f'X: ({sel.target[0]:.2f}, Y: {sel.target[1]:.2f})'),
                                    )
    plt.show()
"""

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

    # plot_dynamic_subplot(optimizedRT['date_01'], optimizedRT[accLatRT], optimizedRT['acclLatOptFilt'])
    

    plt.figure(figsize=(15, 20))

    plt.subplot(4,2,1)
    plt.plot(optimizedGopro["date_01"], optimizedGopro[speedGopro], label="speedGopro")
    plt.plot(optimizedGopro["date_01"], optimizedGopro['speedOpt'], label="speedOpt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(4,2,3)
    plt.plot(optimizedGopro["date_01"], optimizedGopro[accLongGopro], label="accLongGopro")
    plt.plot(optimizedGopro["date_01"], optimizedGopro['accLongOptFilt'], label="accLongOptFilt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(4,2,5)
    plt.plot(optimizedGopro["date_01"], optimizedGopro[accLatGopro], label="accLatGopro")
    plt.plot(optimizedGopro["date_01"], optimizedGopro['accLatOptFilt'], label="accLatOptFilt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(4,2,7)
    plt.plot(optimizedGopro["date_01"], optimizedGopro[jerkGopro], label="jerkGopro")
    plt.plot(optimizedGopro["date_01"], optimizedGopro['jerkOptFilt'], label="jerkOptFilt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(4,2,2)
    plt.plot(optimizedRT["date_01"], optimizedRT[speedRT], label="speedRT")
    plt.plot(optimizedRT["date_01"], optimizedRT['speedOpt'], label="speedOpt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(4,2,4)
    plt.plot(optimizedRT["date_01"], optimizedRT[accLongRT], label="accLongRT")
    plt.plot(optimizedRT["date_01"], optimizedRT['accLongOptFilt'], label="accLongOptFilt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(4,2,6)
    plt.plot(optimizedRT["date_01"], optimizedRT[accLatRT], label="accLatRT")
    plt.plot(optimizedRT["date_01"], optimizedRT['accLatOptFilt'], label="accLatOptFiltRT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.subplot(4,2,8)
    plt.plot(optimizedRT["date_01"], optimizedRT[jerkRT], label="jerkRT")
    plt.plot(optimizedRT["date_01"], optimizedRT['jerkOptFilt'], label="jerkOptFilt")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')


    plt.tight_layout()
    # Add labels to data points 
    """mplcursors.cursor(axes).connect('add', 
                                    lambda sel: sel.annotation.set_text(f'X: ({sel.target[0]:.2f}, Y: {sel.target[1]:.2f})'),
                                    )"""
    
    plt.show()
