
import os 
import json
import pandas as pd

class DataIO:
    
    def __init__(self, raw_data_folder_path, common_file_name):
        self.raw_data_folder_path = raw_data_folder_path
        self.common_file_name = common_file_name
       
        
    def read_file(self, file_name):
        file_path = os.path.join(self.raw_data_folder_path, file_name)
        return pd.read_csv(file_path)
    
    def save_dataframe_to_csv(self, dataframe, file_name):
        file_path = os.path.join(self.raw_data_folder_path, file_name)
        dataframe.to_csv(file_path, index = True)
        
    @staticmethod
    def load_settings(json_file_path, current_settings):
        try:
            with open(json_file_path, 'r') as json_file:
                loaded_settings = json.load(json_file)
            return loaded_settings
        except FileNotFoundError:
            # If the file doesn't exist, save the current settings to a new JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(current_settings, json_file, indent = 4)
            return current_settings
        
    def load_and_save_settings(self, exist_file, cutoff_freq, atten_order, interval_length, auto_adapt,
                               accel_long_offset_man, accel_lat_offset_man, accel_long_offset_auto, accel_lat_offset_auto,
                               invert_flag_long, invert_flag_lat):
        
        if exist_file:
            # Load settings from JSON file
            json_file_path = f'{self.common_file_name}_settings.json'
            current_settings = {
                'common_file_name': self.common_file_name,
                'raw_data_folder_path': self.raw_data_folder_path,
                'cutoff_freq': cutoff_freq,
                'atten_order': atten_order,
                'auto_adapt': auto_adapt,
                'accel_long_offset_man': accel_long_offset_man,
                'accel_lat_offset_man': accel_lat_offset_man,
                'accel_long_offset_auto': accel_long_offset_auto,
                'accel_lat_offset_auto': accel_lat_offset_auto,
                'invert_flag_long': invert_flag_long,
                'invert_flag_lat': invert_flag_lat,
                'interval_length': interval_length
            }
            loaded_settings = DataIO.load_settings(json_file_path, current_settings)
            
            # Check if any setting has changed
            settings_changed = False
            for key, value in current_settings.items():
                if loaded_settings.get(key) != value:
                    settings_changed = True
                    break
            
            if settings_changed:
                # Update variables with the new settings from JSON file
                self.common_file_name = loaded_settings['common_file_name']
                self.raw_data_folder_path = loaded_settings['raw_data_folder_path']
                cutoff_freq = loaded_settings['cutoff_freq']
                atten_order = loaded_settings['atten_order']
                auto_adapt = loaded_settings['auto_adapt']
                accel_long_offset_man = loaded_settings['accel_long_offset_man']
                accel_lat_offset_man = loaded_settings['accel_lat_offset_man']
                invert_flag_long = loaded_settings['invert_flag_long']
                invert_flag_lat = loaded_settings['invert_flag_lat']
                interval_length = loaded_settings['interval_length']
                
            # Save to a new JSON file named after common_file_name
            json_file_path = f'{self.common_file_name}_settings.json'
            with open(json_file_path, 'w') as json_file:
                json.dump(loaded_settings, json_file, indent = 4)
                
            # Return the updated settings
            return loaded_settings
                
    def add_content_to_json(self, new_content):
        json_file_path = f'{self.common_file_name}_settings.json'
        
        # Load existing settings from JSON file
        with open(json_file_path, 'r') as json_file:
            existing_content = json.load(json_file)
            
        # Append new content to existing settings
        existing_content.update(new_content)
        
        # Write updated content back to the JSON file 
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_content, json_file, indent = 4)