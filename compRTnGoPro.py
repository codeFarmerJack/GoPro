# Peudo Code
# 1. Read raw data of RT and GoPro into the data frame 
# 2. Filter the raw data of RT and GoPro 
# 3. Compare veh_spd, accel_long and accel_lat of RT and GoPro after filtering 
# 4. Compare veh_spd, accel_long and accel_lat of RT before filtering and 
#    filtered veh_spd, accel_long and accel_lat of GoPro
import os 
import pandas as pd
import numpy as np 
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

def read_file(data_folder, file_name):
    file_path = os.path.join(data_folder, file_name)
    file = pd.read_csv(file_path)
    return file

def butter_lowpass_filter(data, cutoff_freq, sample_rate, order=4):
    nyquist = 0.5 * sample_rate     
    normal_cutoff = cutoff_freq / nyquist   
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def data_filter(rawData, veh_speed, accel_long, accel_lat, sample_rate, cutoff_freq, atten_order):
    # rawData: DataFrame containing the data to be filtered
    # veh_speed: column name of the vehicle speed to be filtered 
    # accel_long: column name of the longitudinal acceleration to be filtered 
    # accel_lat: column name of the lateral acceleration to be filtered 
        
    # Filter the raw data 
    filtered_spdGopro = butter_lowpass_filter(rawData[veh_speed], cutoff_freq, sample_rate, atten_order)
    filtered_accLongGopro = butter_lowpass_filter(rawData[accel_long], cutoff_freq, sample_rate, atten_order)
    filtered_accLatGopro = butter_lowpass_filter(rawData[accel_lat], cutoff_freq, sample_rate, atten_order)

    # insert to the original DataFrame
    rawData.insert(loc=len(rawData.columns), column = f'{veh_speed}_flt', value=filtered_spdGopro)
    rawData.insert(loc=len(rawData.columns), column = f'{accel_long}_flt', value=filtered_accLongGopro)
    rawData.insert(loc=len(rawData.columns), column = f'{accel_lat}_flt', value=filtered_accLatGopro)
    
    return rawData 

def save_dataframe_to_csv(dataframe, file_path):
    dataframe.to_csv(file_path, index = True)
    
def adjust_offset(original_series, offset):
    adjusted_series = original_series + offset
    return adjusted_series

def invert_signal(signal, invert = False):
    if invert:
        inverted_signal = [-value for value in signal]
        return inverted_signal
    else:
        return signal

if __name__ == '__main__':
    
    # Folder that contains raw data
    raw_data_folder = r'/Users/jackwong/02_Coding/00_repo/01_GoPro/01_Data'
    
    # Input files 
    file_name = r'GoPronRTRawData.csv'
    filtered_file_name = r'GoPronRTRawData_Filetered.csv'
    
    sample_rate = 10    # Hz
    cutoff_freq = 0.15
    atten_order = 4
    
    # Acceleration offset 
    accel_long_offset = 0.3
    accel_lat_offset = 0.2
    
    # Specify if the sign of the signal is inverted
    invert_flag_long = True
    invert_flag_lat = False
    
    
    # column names - raw data
    index = 'Index'
    veh_spd_RT = 'vehSpd_RT'
    veh_spd_GoPro = 'vehSpd_GoPro'
    accel_long_RT = 'accLong_RT'
    accel_long_GoPro = 'accLong_GoPro'
    accel_lat_RT = 'accLat_RT'
    accel_lat_GoPro = 'accLat_GoPro'
    
    # column names - filtered data
    veh_spd_RT_flt = 'vehSpd_RT_flt'
    veh_spd_GoPro_flt = 'vehSpd_GoPro_flt'
    accel_long_RT_flt = 'accLong_RT_flt'
    accel_long_GoPro_flt = 'accLong_GoPro_flt'
    accel_lat_RT_flt = 'accLat_RT_flt'
    accel_lat_GoPro_flt = 'accLat_GoPro_flt'
    accel_long_GoPro_off = 'accLong_GoPro_off'
    accel_long_GoPro_inv = 'accLong_GoPro_inv'
    accel_lat_GoPro_off = 'accLat_GoPro_off'
    accel_lat_GoPro_inv = 'accLat_GoPro_inv'
     
    raw_data = read_file(raw_data_folder, file_name)
    raw_data_tr = raw_data[0:13980]
    print(raw_data_tr)
    
    # Low pass filter RT
    
    data_flt = data_filter(raw_data_tr, veh_spd_RT, accel_long_RT, accel_lat_RT, sample_rate, cutoff_freq, atten_order)
    # Low pass filter GoPro
    data_flt = data_filter(raw_data_tr, veh_spd_GoPro, accel_long_GoPro, accel_lat_GoPro, sample_rate, cutoff_freq, atten_order)
    
    # Adjust offset
    data_flt[accel_long_GoPro_off] = adjust_offset(data_flt[accel_long_GoPro_flt], accel_long_offset)
    data_flt[accel_lat_GoPro_off] = adjust_offset(data_flt[accel_lat_GoPro_flt], accel_lat_offset)
    
    # Invert acceleration signals
    data_flt[accel_long_GoPro_inv] = invert_signal(data_flt[accel_long_GoPro_off], invert_flag_long)
    data_flt[accel_lat_GoPro_inv] = invert_signal(data_flt[accel_lat_GoPro_off], invert_flag_lat)
    
    # Define the subplot layout
    subplot_layout = [
        (data_flt[veh_spd_GoPro_flt], data_flt[veh_spd_RT], 'veh_spd_GoPro_flt', 'veh_spd_RT_raw'),
        (data_flt[accel_long_GoPro_inv], data_flt[accel_long_RT], 'accel_long_GoPro_flt', 'accel_long_RT_raw'),
        (data_flt[accel_lat_GoPro_inv], data_flt[accel_lat_RT], 'accel_lat_GoPro_flt', 'accel_lat_RT_raw'),
        (data_flt[veh_spd_GoPro_flt], data_flt[veh_spd_RT_flt], 'veh_spd_GoPro_flt', 'veh_spd_RT_flt'),
        (data_flt[accel_long_GoPro_inv], data_flt[accel_long_RT_flt], 'accel_long_GoPro_flt', 'accel_long_RT_flt'),
        (data_flt[accel_lat_GoPro_inv], data_flt[accel_lat_RT_flt], 'accel_lat_GoPro_flt', 'accel_lat_RT_flt'),
    ]
    
    timestamp = data_flt[index]
    
    # Iterate through the subplot layout
    for i, (y_1, y_2, label_1, label_2) in enumerate(subplot_layout, start=1):
        ax = plt.subplot(3, 2, i)
        
        ax.plot(timestamp, y_2, label=label_2)
        ax.plot(timestamp, y_1, label=label_1)
        
        ax.legend(fontsize=8, loc='upper right')
        # Set the y range 
        if label_1 == 'accel_long_GoPro_flt':
            ax.set_ylim(-4.5, 4.5)
        elif label_1 == 'accel_lat_GoPro_flt':
            ax.set_ylim(-3.5, 3.5)
               
    plt.tight_layout()
    plt.show()
