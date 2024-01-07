# Pseudo Code
# GoPro raw data processing procedures:
# 1. Read GPS data and Accelerometer into dataframes separately
# 2. Convert 'cts' column of both dataframes into timestamps
#     Formula: = A2/1000/86400  
#     Format: 'mm:ss.000'
# 3. Align the two dataframes according to the converted 'cts' columns
# 4. Process vehicle speed, longitudinal acceleration, lateral acceleration with low-pass filter
# 5. Plot the filtered signals
# 6. Update the bar to faclitate data analysis.

import os
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

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
    # The filter order determines how steeply the filter attenuates frequencies beyond the cutoff
    #   The higher filter order results in a steeper roll-off beyond the cutoff frequency but may
    #   introduce more phase distortion.
    #   A lower filter order provides a gentler roll-off but may not attenuate high frequencies 
    #   as effectively.
    # related link: https://www.elprocus.com/butterworth-filter-formula-and-calculations/
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
        # Increasing the cutoff frequency allows more higher-frequency components of the signal to 
        #   pass through the filter, resulting in less filtering
        # Decreasing the cutoff frequency filters out more high-frequency components, smoothing the
        #   signal more aggressively
    # Filter the raw data 
    filtered_spdGopro = butter_lowpass_filter(rawData[veh_speed], cutoff_freq, sample_rate, order=3)
    filtered_accLongGopro = butter_lowpass_filter(rawData[accl_long], cutoff_freq, sample_rate, order=3)
    filtered_accLatGopro = butter_lowpass_filter(rawData[accl_lat], cutoff_freq, sample_rate, order=3)
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

# Format x-axis tick labels as 'mm::ss'
def format_time_ticks(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f'{minutes:02d}:{seconds:02d}'

def cnt_btwn_and_abv_thd(y_values, threshold_1, threshold_2, cooldown_duration = 10):
    above_threshold_1_count = 0
    above_threshold_2_count = 0
    btwn_threshold_count = 0
    max_above_threshold_1 = float('-inf')
    state = 'below'     # Initial state
    cooldown_counter = 0
    
    # Calculate the absolute of y_values
    y_values_abs = abs(y_values)
    
    for value in y_values_abs:
        if state == 'below' and value > threshold_1 and cooldown_counter == 0:
            state = 'above'
            above_threshold_1_count += 1
            cooldown_counter = cooldown_duration    # Set cooldown counter to prevent immediate count
            #print('value: ', value)
            #print('above_threshold_1_count: ', above_threshold_1_count)
        elif state == 'above' and value < threshold_1:
            state = 'below'
            if max_above_threshold_1 >= threshold_2 and cooldown_counter == 0:
                above_threshold_2_count += 1
                max_above_threshold_1 = 0   # reset the max_above_threshold_1 every time it is counted
                cooldown_counter = cooldown_duration
            #print('value: ', value)
            #print('max_above_threshold_1: ', max_above_threshold_1)
            #print('above_threshold_2_count: ', above_threshold_2_count)
        elif state == 'above' and value > max_above_threshold_1:
            max_above_threshold_1 = value
        
        # Update cooldown_counter 
        cooldown_counter = max(0, cooldown_counter - 1)
        
    # Check the last state
    if state == 'above' and max_above_threshold_1 > threshold_2:
        above_threshold_2_count += 1
        
    btwn_threshold_count = above_threshold_1_count - above_threshold_2_count
    
    return btwn_threshold_count, above_threshold_2_count

if __name__ == '__main__':

    # Navigate to the folder with GoPro raw data
    raw_data_folder_path = r"/Users/jackwong/02_Coding/00_repo/01_GoPro/RawData"
    os.chdir(raw_data_folder_path)
    
    common_file_name = r'GX020188_HERO11'
    # Input files
    GoPro_GPS_Data = f'{common_file_name} Black-GPS9.csv'
    GoPro_ACCL_Data = f'{common_file_name} Black-ACCL.csv'
    
    # Output files:
    Combined_File = f'{common_file_name} Black_Combined.csv'
    filtered_combined_data_name = f'{common_file_name} Black-Combined_filtered.csv'
    
    sample_rate = 10         # 10 Hz
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
    
    # Count the nubmer of times abs(accel_long) lies between (2, 4), and above 4
    accel_long_thd_1 = 2    # Unit: m/s^2
    accel_long_thd_2 = 4    # Unit: m/s^2 
    accel_long_btwn_count, accel_long_above_count = cnt_btwn_and_abv_thd(combined_data_flt[accel_long_flt_col], accel_long_thd_1, accel_long_thd_2)

    # Count the nubmer of times abs(accel_long) lies between (2, 3), and above 3
    accel_lat_thd_1 = 2     # Unit: m/s^2
    accel_lat_thd_2 = 3     # Unit: m/s^2
    accel_lat_btwn_count, accel_lat_above_count = cnt_btwn_and_abv_thd(combined_data_flt[accel_lat_flt_col], accel_lat_thd_1, accel_lat_thd_2)
    
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
        
        units_dict = {veh_speed_flt_kph_col: 'kph', accel_long_flt_col:'m/s²', accel_lat_flt_col:'m/s²'}
        axes[i].set_ylabel(f'{col} ({units_dict.get(col, "")})')
        axes[i].grid(True, linestyle='--', alpha=0.7)
        
        if col == accel_long_flt_col:
            axes[i].set_ylim(-4.1, 4.1)
            axes[i].set_yticks([-4, -2, 0, 2, 4])
        elif col == accel_lat_flt_col:
            axes[i].set_ylim(-3.1, 3.1)
            axes[i].set_yticks([-3, -2, -1, 0, 1, 2, 3])
    
    axes[-1].set_xlabel('Time (mm:ss)')
    
    # Define dynamic legends for subplot 2 and subplot 3
    text_legend_2 = axes[1].text(0.78, 0.12, '', transform=axes[1].transAxes, fontsize=8, verticalalignment='center', horizontalalignment='left')
    text_legend_3 = axes[2].text(0.78, 0.12, '', transform=axes[2].transAxes, fontsize=8, verticalalignment='center', horizontalalignment='left')
    
    
    # Update dynamic legends
    text_legend_2.set_text(f'Accel_Long: '
                           f'\n{accel_long_btwn_count} times between {accel_long_thd_1}m/s² and {accel_long_thd_2}m/s²' 
                           f'\n{accel_long_above_count} times above {accel_long_thd_2}m/s²')
    text_legend_3.set_text(f'Accel_Lat: '
                           f'\n{accel_lat_btwn_count} times between {accel_lat_thd_1}m/s² and {accel_lat_thd_2}m/s²' 
                           f'\n{accel_lat_above_count} times above {accel_lat_thd_2}m/s²')

    # Add title to the figure
    plt.suptitle(common_file_name)

    plt.tight_layout()
    
    plt.show()

    