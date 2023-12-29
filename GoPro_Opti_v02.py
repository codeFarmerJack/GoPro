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
def dataOpt(rawData, speed, accLong, accLat, fltSpdGopro, fltSpdGoproKPH, fltAccLongGopro, fltAccLatGopro):
    
    cutoff_freq = 0.07      # Adjust this cutoff frequency as needed

    # Filter the raw data 
    filtered_spdGopro = butter_lowpass_filter(rawData[speed], cutoff_freq, SampleRate, order=3)
    filtered_accLongGopro = butter_lowpass_filter(rawData[accLong], cutoff_freq, SampleRate, order=3)
    filtered_accLatGopro = butter_lowpass_filter(rawData[accLat], cutoff_freq, SampleRate, order=3)
    filtered_spdGoproKPH = filtered_spdGopro * 3.6

    # insert to the original DataFrame
    rawData.insert(loc=len(rawData.columns), column = fltSpdGopro, value=filtered_spdGopro)
    rawData.insert(loc=len(rawData.columns), column = fltAccLongGopro, value=filtered_accLongGopro)
    rawData.insert(loc=len(rawData.columns), column = fltAccLatGopro, value=filtered_accLatGopro)
    rawData.insert(loc=len(rawData.columns), column = fltSpdGoproKPH, value=filtered_spdGoproKPH)
    
    return rawData 

def custom_date_parser(x):
    return pd.to_datetime(x, format = '%H:%M:%S.%f', errors='coerce')

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
    
# Function to extract time portion
def extract_time(timestamp_str):
    
    if pd.notna(timestamp_str):
        datetime_object = dt.strptime(timestamp_str[:-1], "%Y-%m-%dT%H:%M:%S.%f")
        time_portion = datetime_object.strftime('%H:%M:%S.%f')[:-3]
        return time_portion
    else:
        return pd.NaT  # Return a NaT (Not a Timestamp) for NaN values
    
if __name__ == '__main__':

    # data file sample frequency and name
    SampleRate = 10         # Hz
    GoProFile = "GX010188_HERO11 Black-GPS9.csv"
    
    
    # column names in the csv files, list only the signals that interest us
    ## raw signals of Gopro
    rawDate = 'date'
    rawSpdGopro = 'GPS (2D) [m/s]'
    rawAccLongGopro = 'longAccel'
    rawAccLatGopro = 'latAccel'
    # truncated columns
    procDate = 'truncated_Date'
    procSpdGopro = 'truncated_rawSpdGopro'
    procAccLongGopro = 'truncated_rawAccLongGopro'
    procAccLatGopro = 'truncated_rawAccLatGopro'
    # low pass filter processed data
    fltSpdGopro = 'filtered_spdGopro'
    fltSpdGoproKPH = 'filtered_spdGoproKPH'
    fltAccLongGopro = 'filtered_accLongGopro'
    fltAccLatGopro = 'filtered_accLatGopro'

    # data folder path
    data_folder_path = r"/Users/jackwong/02_Coding/00_repo/01_GoPro"
    os.chdir(data_folder_path)
    # Specify the file path along with the file name
    csv_file_path_1 = r"/Users/jackwong/02_Coding/00_repo/01_GoPro/GX010188_HERO11 Black-GPS9_preOpt.csv"
    csv_file_path_2 = r"/Users/jackwong/02_Coding/00_repo/01_GoPro/GX010188_HERO11 Black-GPS9_postOpt.csv"
    
    gopro = None
    # Read data from csv to DataFrame and rename columns names
    for filename in os.listdir():
        full_path = os.path.join(data_folder_path, filename)
        if os.path.isfile(full_path):
            print(filename)
            if filename == GoProFile:
                try:
                    gopro = pd.read_csv(filename, delimiter=',')
                    print("Successfully loaded data from CSV.")
                    print(f"Columns in gopro: {gopro.columns}")
                except Exception as e:
                    print(f"Error loading data from CSV: {e}")
                    gopro = None

                min_length = min(gopro[rawDate].count(), gopro[rawAccLongGopro].count())
                gopro[procDate] = gopro[rawDate][:min_length]
                gopro[procSpdGopro] = gopro[rawSpdGopro][:min_length]
                gopro[procAccLongGopro] = gopro[rawAccLongGopro][:min_length]  
                gopro[procAccLatGopro] = gopro[rawAccLongGopro][:min_length]
                
                gopro = gopro.apply(lambda x: x[:min_length])
                
    if gopro is not None:
        # Add a new column 'dateProcessed' with the extracted time portion
        gopro[procDate] = gopro[rawDate].apply(extract_time)
        # Set the 'dateProcessed' column as the date index
        gopro.set_index(procDate, inplace=True)
        gopro = gopro.drop(columns=[rawAccLongGopro, rawAccLatGopro])
        
        save_dataframe_to_csv(gopro, csv_file_path_1)
        # Process Gopro with lowpass filter
        optimizedGopro = dataOpt(gopro, procSpdGopro, procAccLongGopro, procAccLatGopro, fltSpdGopro, fltSpdGoproKPH, fltAccLongGopro, fltAccLatGopro)
        print('data filtered')
        # Save the filtered data to a csv file
        save_dataframe_to_csv(optimizedGopro, csv_file_path_2)
        print('columns of optimizedGopro: ', optimizedGopro.columns)
    
    target_x_value = None

    plt.figure(figsize=(15, 10))

    # Connect the mouse click event to the callback function
    plt.gcf().canvas.mpl_connect('button_press_event', on_plot_click)
    # mplcursors.cursor(hover = True).connect('add', on_plot_click)
    
    # Assuming subplot_layout is your list of tuples
    subplot_layout = [
        (optimizedGopro.index, optimizedGopro[fltSpdGopro], "fltSpdGopro"),
        (optimizedGopro.index, optimizedGopro[fltAccLongGopro], 'fltAccLongGopro'),
        (optimizedGopro.index, optimizedGopro[fltAccLatGopro], 'fltAccLatGopro')
    ]

    for i, (date_column, filtered_data,flt_label) in enumerate(subplot_layout, start=1):
        ax = plt.subplot(3, 1, i)

        # Plot data and filtered data
        ax.plot(date_column, filtered_data, label=flt_label)

        draw_cursor(ax, x_values=[date_column[0]])

        ax.legend(fontsize=5, loc='upper left')

    plt.tight_layout()
    plt.show()
