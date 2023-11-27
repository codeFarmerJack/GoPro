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

def draw_vertical_lines(ax, x_values, label):
    for x_value in x_values:
        ax.axvline(x = x_value, color = 'r', linestyle = '--', label = label)

def on_plot_click(sel):
    if sel.event.name == 'button_press_event':
        global initial_x_value
        initial_x_value = sel.target[0]
        for ax in plt.gcf().get_axes():
            ax.lines = [line for line in ax.lines if 'Vertical Line' not in line.get_label()]
            draw_vertical_lines(ax, [initial_x_value] * 8, 'Vertical Line')
        plt.gcf().canvas.draw()


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
    data_folder_path = r"/Users/jackwong/02_Coding/00_repo/01_GoPro/01_Data"
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
    
# initial_x_value = 5

# Determine the common date range
common_date_range = pd.to_datetime(np.intersect1d(optimizedGopro["date_01"], optimizedRT["date_01"]))

plt.figure(figsize=(15, 10))

# Define the subplot layout
subplot_layout = [
    (optimizedGopro, 'date_01', optimizedGopro[speedGopro], 'speedGopro', 'speedOpt'),
    (optimizedRT, 'date_01', optimizedRT[speedRT], 'speedRT', 'speedOpt'),
    (optimizedGopro, 'date_01', optimizedGopro[accLongGopro], 'accLongGopro', 'accLongOptFilt'),
    (optimizedRT, 'date_01', optimizedRT[accLongRT], 'accLongRT', 'accLongOptFilt'),
    (optimizedGopro, 'date_01', optimizedGopro[accLatGopro], 'accLatGopro', 'accLatOptFilt'),
    (optimizedRT, 'date_01', optimizedRT[accLatRT], 'accLatRT', 'accLatOptFilt'),
    (optimizedGopro, 'date_01', optimizedGopro[jerkGopro], 'jerkGopro', 'jerkOptFilt'),
    (optimizedRT, 'date_01', optimizedRT[jerkRT], 'jerkRT', 'jerkOptFilt')
]

# Iterate through the subplot layout
for i, (df, date_column, data, label, filtered_data) in enumerate(subplot_layout, start=1):
    plt.subplot(4, 2, i)

    # Select the common date range for each subplot
    common_data = data[df[date_column].isin(common_date_range)]
    common_filtered_data = df[filtered_data][df[date_column].isin(common_date_range)]
    
    plt.plot(common_date_range, common_data, label=label)
    plt.plot(common_date_range, common_filtered_data, label=f'{filtered_data}Opt')
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    # Draw vertical lines on each subplot
    # for ax in plt.gcf().get_axes():
    #     draw_vertical_lines(ax, x_values=[initial_x_value] * 8, label='Vertical Line')

plt.tight_layout()
plt.show()
