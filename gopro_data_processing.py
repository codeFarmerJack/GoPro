
import pandas as pd
from scipy.signal import butter, filtfilt


class DataProcessing:
    
    
    @staticmethod
    def timestamp_gen(raw_data, raw_time_col):
        raw_data['timestamp'] = raw_data[raw_time_col] / 1000 / 86400
        raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'], unit='D')
        raw_data['timestamp'] = raw_data['timestamp'].dt.strftime('%M:%S.%f')
        raw_data['timestamp'] = raw_data['timestamp'].str[:-5]
        raw_data.set_index('timestamp', inplace=True)
        return raw_data

    @staticmethod
    def butter_lowpass_filter(data, cutoff_freq, sample_rate, order=4):
        nyquist = 0.5 * sample_rate     
        normal_cutoff = cutoff_freq / nyquist   
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)
    
    def data_filter(self, raw_data, veh_speed, accel_long, accel_lat, sample_rate, cutoff_freq, order):
        # rawData: DataFrame containing the data to be filtered
        # veh_speed: column name of the vehichle speed to be filtered 
        # accl_long: column nanme of the longitudinal acceleraiton to be filtered 
        # accl_lat: column name of the lateral acceleration to be filtered 
        
            
        # Filter the raw data 
        filtered_spdGopro = self.butter_lowpass_filter(raw_data[veh_speed], cutoff_freq, sample_rate, order)
        filtered_accLongGopro = self.butter_lowpass_filter(raw_data[accel_long], cutoff_freq, sample_rate, order)
        filtered_accLatGopro = self.butter_lowpass_filter(raw_data[accel_lat], cutoff_freq, sample_rate, order)
        filtered_spdGoproKPH = filtered_spdGopro * 3.6

        # insert to the original DataFrame
        raw_data.insert(loc=len(raw_data.columns), column = 'veh_speed_flt_m/s', value=filtered_spdGopro)
        raw_data.insert(loc=len(raw_data.columns), column = 'veh_speed_flt_kph', value=filtered_spdGoproKPH)
        raw_data.insert(loc=len(raw_data.columns), column = 'accel_long_flt', value=filtered_accLongGopro)
        raw_data.insert(loc=len(raw_data.columns), column = 'accel_lat_flt', value=filtered_accLatGopro)
        
        return raw_data 
    
    @staticmethod
    def cnt_btwn_and_abv_thd(y_values, thd_1, thd_2, cooldown_duration=10):
        above_thd_1_count = 0
        above_thd_2_count = 0
        btwn_thd_count = 0
        max_above_thd_1 = float('-inf')
        state = 'below'     # Initial state
        cooldown_counter = 0
        
        # Calculate the absolute of y_values
        y_values_abs = abs(y_values)
        
        for value in y_values_abs:
            if state == 'below' and value > thd_1 and cooldown_counter == 0:
                state = 'above'
                above_thd_1_count += 1
                cooldown_counter = cooldown_duration    # Set cooldown counter to prevent immediate count
                #print('value: ', value)
                #print('above_thd_1_count: ', above_thd_1_count)
            elif state == 'above' and value < thd_1:
                state = 'below'
                if max_above_thd_1 >= thd_2 and cooldown_counter == 0:
                    above_thd_2_count += 1
                    max_above_thd_1 = 0   # reset the max_above_thd_1 every time it is counted
                    cooldown_counter = cooldown_duration
            elif state == 'above' and value > max_above_thd_1:
                max_above_thd_1 = value
            
            # Update cooldown_counter 
            cooldown_counter = max(0, cooldown_counter - 1)
            
        # Check the last state
        if state == 'above' and max_above_thd_1 > thd_2:
            above_thd_2_count += 1
            
        btwn_thd_count = above_thd_1_count - above_thd_2_count
        
        return btwn_thd_count, above_thd_2_count
    
    def adjust_offset(self, original_series, offset):
        adjusted_series = original_series + offset
        return adjusted_series
    
    @staticmethod
    def invert_signal(signal, invert = False):
        if invert:
            inverted_signal = [-value for value in signal]
            return inverted_signal
        else:
            return signal
    
    def interval_filter(self, array, min_interval):
        filtered_array = []
    
        for i in range(len(array)-1):
            current_element = array[i]
            next_element = array[i+1]
            if next_element - current_element >= min_interval:
                filtered_array.append(current_element)
        # Include the last element 
        filtered_array.append(array[-1])
        return filtered_array

    