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
def dataOpt(rawData, speed, accLong, accLat):
    
    cutoff_freq = 0.07      # Adjust this cutoff frequency as needed

    # Filter the raw data 
    speedOpt = butter_lowpass_filter(rawData[speed], cutoff_freq, SampleRate, order=3)
    accLongOptFilt = butter_lowpass_filter(rawData[accLong], cutoff_freq, SampleRate, order=3)
    accLatOptFilt = butter_lowpass_filter(rawData[accLat], cutoff_freq, SampleRate, order=3)
    # jerkOptFilt = butter_lowpass_filter(rawData[jerk], cutoff_freq, SampleRate, order=3)
    speedOptKPH = speedOpt * 3.6

    # insert to the original DataFrame
    rawData.insert(loc=len(rawData.columns), column = 'speedOpt', value=speedOpt)
    rawData.insert(loc=len(rawData.columns), column = 'accLongOptFilt', value=accLongOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'accLatOptFilt', value=accLatOptFilt)
    # rawData.insert(loc=len(rawData.columns), column = 'jerkOptFilt', value=jerkOptFilt)
    rawData.insert(loc=len(rawData.columns), column = 'speedOptKPH', value=speedOptKPH)
    
    return rawData 

def custom_date_parser(x):
    return pd.to_datetime(x, format = '%H:%M:%S', errors='coerce')

# Function to draw cursor
def draw_cursor(ax, x_values):
    for x in x_values:
        ax.axvline(x = x, color = 'r', linestyle = '--', label = 'cursor')
        
# Callback function for mouse click event
def on_plot_click(event):
    global target_x_value
    if event.inaxes is not None and event.button == 1:
        
        target_x_value = event.xdata

        for ax in plt.gcf().get_axes():
            # Remove the existing cursor with "cursor" label
            existing_lines = [line for line in ax.lines if 'cursor' in line.get_label()]
            for line in existing_lines:
                line.remove()
            # Draw a new cursor at the updated x-value
            draw_cursor(ax, x_values=[target_x_value])
            
        plt.gcf().canvas.draw()

def save_dataframe_to_csv(dataframe, file_path):
    dataframe.to_csv(file_path, index = True)
    
if __name__ == '__main__':

    # data file sample frequency and name
    SampleRate = 10         # Hz
    mergedDataFilename = "GX010188_HERO11 Black-GPS9.csv"
    
    # column names in the csv files, list only the signals that interest us
    ## signals of Gopro
    date = 'dateProcessed'
    speedGopro = 'GPS (2D) [m/s]'
    accLongGopro = 'longAccel'
    accLatGopro = 'latAccel'

    
    # data folder path
    data_folder_path = r"C:\AAD\03_Projects\01_Benchmarking\03_RawData\CW2349_XpengG6"
    os.chdir(data_folder_path)
    # Specify the file path along with the file name
    csv_file_path_1 = r"C:\AAD\03_Projects\01_Benchmarking\03_RawData\CW2349_XpengG6\GX010188_HERO11 Black-GPS9.csv"
    # csv_file_path_2 = r"/Users/jackwong/02_Coding/00_repo/01_GoPro/01_Data/optimizedRT.csv"
    
    gopro = None
    rt = None
    # Read data from csv to DataFrame and rename columns names
    for filename in os.listdir():
        # print(filename)
        if filename == mergedDataFilename:
            gopro = pd.read_csv(filename, delimiter=',', converters={date:custom_date_parser})

    # Process the date column for further analysis
    gopro['dateProcessed'] = gopro['date'].str[-13, -1]

    # Process Gopro with lowpass filter
    optimizedGopro = dataOpt(gopro, speedGopro, accLongGopro, accLatGopro)

    # Save the filtered data to a csv file
    save_dataframe_to_csv(optimizedGopro, csv_file_path_1)
    
    # plot_dynamic_subplot(optimizedRT['date_01'], optimizedRT[accLatRT], optimizedRT['acclLatOptFilt'])
    
    target_x_value = None

    # Determine the common date range
    common_date_range = pd.to_datetime(optimizedGopro[date])

    plt.figure(figsize=(15, 10))


    # Define the subplot layout 
    subplot_layout = [
        (optimizedGopro, date, optimizedGopro[speedGopro], 'speedGopro', 'speedOpt'),
        (optimizedGopro, date, optimizedGopro[accLongGopro], 'accLongGopro', 'accLongOptFilt'),
        (optimizedGopro, date, optimizedGopro[accLatGopro], 'accLatGopro', 'accLatOptFilt')
    ]

    # Connect the mouse click event to the callback function
    plt.gcf().canvas.mpl_connect('button_press_event', on_plot_click)
    # mplcursors.cursor(hover = True).connect('add', on_plot_click)

    # Iterate through the subplot layout
    for i, (df, date_column, data, label, filtered_data) in enumerate(subplot_layout, start=1):
        ax = plt.subplot(4, 2, i)

        # Select the common date range for each subplot
        common_data = data[df[date_column].isin(common_date_range)]
        common_filtered_data = df[filtered_data][df[date_column].isin(common_date_range)]
    
        # Plot data and filtered data
        ax.plot(common_date_range, common_data, label=label)
        ax.plot(common_date_range, common_filtered_data, label=f'{filtered_data}Opt')
    
        draw_cursor(ax, x_values = [common_date_range[0]])
    
        ax.legend(fontsize = 5, loc = 'upper left')

    plt.tight_layout()
    plt.show()

    
