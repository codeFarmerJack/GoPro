'''
Pseudo Code
GoPro raw data processing procedures:
1. Read GPS data and Accelerometer into dataframes separately
2. Convert 'cts' column of both dataframes into timestamps
    Formula: = A2/1000/86400  
    Format: 'mm:ss.000'
3. Align the two dataframes according to the converted 'cts' columns
    - How?
4. Process vehicle speed, longitudinal acceleration, lateral acceleration with low-pass filter
5. Plot the filtered signals
6. Update the bar to faclitate data analysis.
'''

import os
import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoLocator, FuncFormatter

def timestamp_gen(raw_data, raw_time_col):
    raw_data['timestamp'] = raw_data[raw_time_col] / 1000 / 86400
    raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'], unit='D')
    raw_data['timestamp'] = raw_data['timestamp'].dt.strftime('%M:%S.%f')
    raw_data['timestamp'] = raw_data['timestamp'].str[:-5]
    raw_data.set_index('timestamp', inplace=True)
    return raw_data

def save_dataframe_to_csv(dataframe, file_path):
    dataframe.to_csv(file_path, index = True)

def read_file(data_foler, file_name):
    file_path = os.path.join(data_foler, file_name)
    file = pd.read_csv(file_path)
    return file

def butter_lowpass_filter(data, cutoff_freq, sample_rate, order=4):
    nyquist = 0.5 * sample_rate     
    normal_cutoff = cutoff_freq / nyquist   
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def data_filter(rawData, veh_speed, accl_long, accl_lat):
    # rawData: DataFrame containing the data to be filtered
    # veh_speed: column name of the vehichle speed to be filtered 
    # accl_long: column nanme of the longitudinal acceleraiton to be filtered 
    # accl_lat: column name of the lateral acceleration to be filtered 
    
    cutoff_freq = 0.07      # Adjust this cutoff frequency as needed

    # Filter the raw data 
    filtered_spdGopro = butter_lowpass_filter(rawData[veh_speed], cutoff_freq, SampleRate, order=3)
    filtered_accLongGopro = butter_lowpass_filter(rawData[accl_long], cutoff_freq, SampleRate, order=3)
    filtered_accLatGopro = butter_lowpass_filter(rawData[accl_lat], cutoff_freq, SampleRate, order=3)
    filtered_spdGoproKPH = filtered_spdGopro * 3.6

    # insert to the original DataFrame
    rawData.insert(loc=len(rawData.columns), column = 'veh_speed_flt_m/s', value=filtered_spdGopro)
    rawData.insert(loc=len(rawData.columns), column = 'veh_speed_flt_kph', value=filtered_spdGoproKPH)
    rawData.insert(loc=len(rawData.columns), column = 'accel_long_flt', value=filtered_accLongGopro)
    rawData.insert(loc=len(rawData.columns), column = 'accel_lat_flt', value=filtered_accLatGopro)
    
    return rawData 

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


if __name__ == '__main__':

    # Navigate to the folder with GoPro raw data
    raw_data_folder_path = r"/Users/jackwong/02_Coding/00_repo/01_GoPro/RawData"
    os.chdir(raw_data_folder_path)
    
    # Input files
    GoPro_GPS_Data = 'GX020188_HERO11 Black-GPS9.csv'
    GoPro_ACCL_Data = 'GX020188_HERO11 Black-ACCL.csv'
    
    # Output files:
    Combined_File = r'GX020188_HERO11 Black_Combined.csv'
    filtered_combined_data_name = 'GX020188_HERO11 Black-Combined_filtered.csv'
    
    SampleRate = 10         # 10 Hz
    # Columns settings
    raw_time_col = 'cts'
    index_name = 'timestamp'
    veh_speed_col = 'GPS (2D) [m/s]'
    accel_long_col = '2'
    accel_lat_col = '1'
    veh_speed_flt_col = 'veh_speed_flt_m/s'
    veh_speed_flt_kph_col = 'veh_speed_flt_kph'
    accel_long_flt_col = 'accel_long_flt'
    accel_lat_flt_col = 'accel_lat_flt'
    
    # Read data from csv to DataFrame and rename columns names
    raw_data_GPS = read_file(raw_data_folder_path, GoPro_GPS_Data)
    raw_data_ACCL = read_file(raw_data_folder_path, GoPro_ACCL_Data)
    
    # Convert 'cts' column to timestamps
    raw_data_GPS_prep = timestamp_gen(raw_data_GPS, raw_time_col)
    raw_data_ACCL_prep = timestamp_gen(raw_data_ACCL, raw_time_col)
    
    # Extract speed, acceleration and combine them into one dataframe.
    speed_extraction = [veh_speed_col]
    accel_extraction = [accel_long_col, accel_lat_col]
    combined_data_raw = pd.merge(raw_data_GPS_prep[speed_extraction], 
                                 raw_data_ACCL_prep[accel_extraction], 
                                 left_index=True, right_index=True, how='inner')

    combined_data_flt = data_filter(combined_data_raw, veh_speed_col, accel_long_col, accel_lat_col)

    
    save_dataframe_to_csv(combined_data_flt, filtered_combined_data_name)
    
    target_x_value = None    
    
    # Columns to be visualized
    cols_to_visualize = [veh_speed_flt_kph_col, accel_long_flt_col, accel_lat_flt_col]
    
    fig, axes = plt.subplots(nrows=len(cols_to_visualize), ncols=1, figsize=(10, 6), sharex=True)
    
    # Connect the mouse click event to the callback function
    plt.gcf().canvas.mpl_connect('button_press_event', on_plot_click)
    # mplcursors.cursor(hover = True).connect('add', on_plot_click)
    
    for i, col in enumerate(cols_to_visualize):
        combined_data_flt[col].plot(ax=axes[i], label = col)
        axes[i].legend([f'{col}'], loc='upper right')
        
        units_dict = {veh_speed_flt_kph_col: 'kph', accel_long_flt_col:'m/s^2', accel_lat_flt_col:'m/s^2'}
        axes[i].set_ylabel(f'{col} ({units_dict.get(col, "")})')
        axes[i].grid(True, linestyle='--', alpha=0.7)
        
        if col == accel_long_flt_col:
            axes[i].set_ylim(-4.1, 4.1)
            axes[i].set_yticks([-4, -2, 0, 2, 4])
        elif col == accel_lat_flt_col:
            axes[i].set_ylim(-3.1, 3.1)
            axes[i].set_yticks([-3, -2, 0, 2, 3])
    
    axes[-1].set_xlabel('Time (s)')
    
    plt.tight_layout()
    plt.show()

    