import os
import json
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

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

def data_filter(rawData, veh_speed, accl_long, accl_lat, sample_rate, cutoff_freq, atten_order):
    # rawData: DataFrame containing the data to be filtered
    # veh_speed: column name of the vehichle speed to be filtered 
    # accl_long: column nanme of the longitudinal acceleraiton to be filtered 
    # accl_lat: column name of the lateral acceleration to be filtered 
    
        
    # Filter the raw data 
    filtered_spdGopro = butter_lowpass_filter(rawData[veh_speed], cutoff_freq, sample_rate, atten_order)
    filtered_accLongGopro = butter_lowpass_filter(rawData[accl_long], cutoff_freq, sample_rate, atten_order)
    filtered_accLatGopro = butter_lowpass_filter(rawData[accl_lat], cutoff_freq, sample_rate, atten_order)
    filtered_spdGoproKPH = filtered_spdGopro * 3.6

    # insert to the original DataFrame
    rawData.insert(loc=len(rawData.columns), column = 'veh_speed_flt_m/s', value=filtered_spdGopro)
    rawData.insert(loc=len(rawData.columns), column = 'veh_speed_flt_kph', value=filtered_spdGoproKPH)
    rawData.insert(loc=len(rawData.columns), column = 'accel_long_flt', value=filtered_accLongGopro)
    rawData.insert(loc=len(rawData.columns), column = 'accel_lat_flt', value=filtered_accLatGopro)
    
    return rawData 

def get_y_value(ax, x_value):
    line = ax.lines[0]
    x_data = line.get_xdata()
    y_data = line.get_ydata()
    
    # Find the index of the closest x-value in data
    idx = (abs(x_data - x_value)).argmin()
    
    return y_data[idx]

def update_bottom_right_text(ax, x_value, y_value):
    # Assuming the last axis is the bottom right one
    bottom_right_ax = ax
    # Remove the existing text with "bottom_right_text" label
    existing_texts = [text for text in bottom_right_ax.texts if 'bottom_right_text' in text.get_label()]
    
    for text in existing_texts:
        text.remove()
        
    # Add new text with x and y values
    bottom_right_ax.text(0.95, 0.05, f'X: {x_value:.2f}, Y:{y_value: .2f}',
                         transform=bottom_right_ax.transAxes, color='red', fontsize=8,
                         verticalalignment='bottom', horizontalalignment='right',
                         label = 'bottom_right_text')

# Function to draw cursor
def draw_cursor(ax, x_values):
    
    ax.axvline(x = x_values, color = 'r', linestyle = '--', label = 'cursor')
        
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
                
             # Remove the existing bottom right text with "bottom_right_text" label
            existing_texts = [text for text in ax.texts if 'bottom_right_text' in text.get_label()]
            for text in existing_texts:
                text.remove()
                
            # Draw a new cursor at the updated x-value
            draw_cursor(ax, x_values=target_x_value)
            y_values = get_y_value(ax, target_x_value)
            update_bottom_right_text(ax, target_x_value, y_values)
            
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
            
        elif state == 'above' and value > max_above_threshold_1:
            max_above_threshold_1 = value
        
        # Update cooldown_counter 
        cooldown_counter = max(0, cooldown_counter - 1)
        
    # Check the last state
    if state == 'above' and max_above_threshold_1 > threshold_2:
        above_threshold_2_count += 1
        
    btwn_threshold_count = above_threshold_1_count - above_threshold_2_count
    
    return btwn_threshold_count, above_threshold_2_count

def adjust_offset(original_series, offset):
    adjusted_series = original_series + offset
    return adjusted_series

def invert_signal(signal, invert = False):
    if invert:
        inverted_signal = [-value for value in signal]
        return inverted_signal
    else:
        return signal
    
def load_settings(json_file_path, current_settings):
    try:
        with open(json_file_path, 'r') as json_file:
            loaded_settings = json.load(json_file)
        return loaded_settings
    except FileNotFoundError:
        # If the file doesn't exist, save the current settings to a new JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(current_settings, json_file, indent=4)
        return current_settings
    
def interval_filter(array, min_inverval=600):
    filtered_array = []
    
    for i in range(len(array)-1):
        current_element = array[i]
        next_element = array[i+1]
        if next_element - current_element >= min_inverval:
            filtered_array.append(current_element)
    # Include the last element 
    filtered_array.append(array[-1])
    return filtered_array
