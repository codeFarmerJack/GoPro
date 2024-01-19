# Pseudo Code
# GoPro raw data processing procedures:
# 1. Read GPS data and Accelerometer into dataframes separately
# 2. Convert 'cts' column of both dataframes into timestamps
#     Formula: = A2/1000/86400  
#     Format: 'mm:ss.s'
# 3. Align the two dataframes according to the converted 'cts' columns
# 4. Process vehicle speed, longitudinal acceleration, lateral acceleration with low-pass filter
# 5. Plot the filtered signals
# 6. Update the bar to faclitate data analysis.

from GoProDataProcessingFunctions import *

if __name__ == '__main__':

    # Navigate to the folder with GoPro raw data
    raw_data_folder_path = r"/Users/jackwong/02_Coding/00_repo/01_GoPro/RawData"
    os.chdir(raw_data_folder_path)
    
    common_file_name = r'GX010193_HERO11'
    # Input files
    GoPro_GPS_Data = f'{common_file_name} Black-GPS9.csv'
    GoPro_ACCL_Data = f'{common_file_name} Black-ACCL.csv'
    
    # Output files:
    Combined_File = f'{common_file_name} Black_Combined.csv'
    filtered_combined_data_name = f'{common_file_name} Black-Combined_filtered.csv'
    
    sample_rate = 10         # 10 Hz
    
    # Low-pass filter parameter setting
    cutoff_freq = 0.15   # cutoff frequency of filter 
        # Adjust this cutoff frequency as needed
        # Increasing the cutoff frequency allows more higher-frequency components of the signal to 
        #   pass through the filter, resulting in less filtering
        # Decreasing the cutoff frequency filters out more high-frequency components, smoothing the
        #   signal more aggressively
    atten_order = 3
        # The filter order determines how steeply the filter attenuates frequencies beyond the cutoff
        #   The higher filter order results in a steeper roll-off beyond the cutoff frequency but may
        #   introduce more phase distortion.
        #   A lower filter order provides a gentler roll-off but may not attenuate high frequencies 
        #   as effectively.
        # related link: https://www.elprocus.com/butterworth-filter-formula-and-calculations/
        
    # Acceleration offset 
    accel_long_offset = 0
    accel_lat_offset = 0
    
    # Specify if the sign of the signal is inverted
    invert_flag_long = False
    invert_flag_lat = False
    
    # Load settings from JSON file
    json_file_path = f'{common_file_name}_settings.json'
    current_settings = {
        "common_file_name": common_file_name,
        "raw_data_folder_path": raw_data_folder_path,
        # Low-pass filter parameter setting
        "cutoff_freq": cutoff_freq,
        "atten_order": atten_order,
        # Acceleration offset 
        "accel_long_offset": accel_long_offset,
        "accel_lat_offset": accel_lat_offset,
        # Specify if the sign of the signal is inverted
        "invert_flag_long": invert_flag_long,
        "invert_flag_lat": invert_flag_lat                
    }
    loaded_settings = load_settings(json_file_path, current_settings)
    
    # Check if any setting has changed
    settings_changed = False
    for key, value in current_settings.items():
        if loaded_settings.get(key) != value:
            settings_changed = True
            break

    if settings_changed:
        # Update variables with the new settings
        common_file_name = loaded_settings["common_file_name"]
        raw_data_folder_path = loaded_settings["raw_data_folder_path"]
        cutoff_freq = loaded_settings["cutoff_freq"]
        atten_order = loaded_settings["atten_order"]
        accel_long_offset = loaded_settings["accel_long_offset"]
        accel_lat_offset = loaded_settings["accel_lat_offset"]
        invert_flag_long = loaded_settings["invert_flag_long"]
        invert_flag_lat = loaded_settings["invert_flag_lat"]
    
        # Save to a new JSON file named after common_file_name
        json_file_path = f'{common_file_name}_settings.json'
        if os.path.isfile(GoPro_ACCL_Data):
            with open(json_file_path, 'w') as json_file:
                json.dump(loaded_settings, json_file, indent=4)
    
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
    accel_long_adj = 'accel_long_adj'
    accel_lat_adj = 'accel_lat_adj'
    accel_long_inv = 'accel_long_inv'
    accel_lat_inv = 'accel_lat_inv'
    
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
                                 left_index=True, right_index=True, how='right')
    
    # Fill NaN values with zero in the merged DataFrame
    combined_data_raw = combined_data_raw.fillna(0)

    combined_data_flt = data_filter(combined_data_raw, veh_speed_col, accel_long_col, accel_lat_col, sample_rate, cutoff_freq , atten_order)
    
    # Convert the index to a datetime format
    timestamp_datetime = pd.to_datetime(combined_data_flt.index, format='%M:%S.%f')
    
    # Extract time component and convert timedelta values to seconds
    time_component = timestamp_datetime - pd.to_datetime(timestamp_datetime.date)
    total_seconds = time_component.total_seconds()
    
    # Adjust offset of acceleration
    combined_data_flt[accel_long_adj] = adjust_offset(combined_data_flt[accel_long_flt_col], accel_long_offset)
    combined_data_flt[accel_lat_adj] = adjust_offset(combined_data_flt[accel_lat_flt_col], accel_lat_offset)
    
    # Invert the sign of acceleration if invert_flag == True
    combined_data_flt[accel_long_inv] = invert_signal(combined_data_flt[accel_long_adj], invert_flag_long)
    combined_data_flt[accel_lat_inv] = invert_signal(combined_data_flt[accel_lat_adj], invert_flag_lat)
    
    # Count the nubmer of times abs(accel_long) lies between (2, 4), and above 4
    accel_long_thd_1 = 2    # Unit: m/s^2
    accel_long_thd_2 = 4    # Unit: m/s^2 
    accel_long_btwn_count, accel_long_above_count = cnt_btwn_and_abv_thd(combined_data_flt[accel_long_inv], accel_long_thd_1, accel_long_thd_2)

    # Count the nubmer of times abs(accel_long) lies between (2, 3), and above 3
    accel_lat_thd_1 = 2     # Unit: m/s^2
    accel_lat_thd_2 = 3     # Unit: m/s^2
    accel_lat_btwn_count, accel_lat_above_count = cnt_btwn_and_abv_thd(combined_data_flt[accel_lat_inv], accel_lat_thd_1, accel_lat_thd_2)
    
    save_dataframe_to_csv(combined_data_flt, filtered_combined_data_name)
    
    target_x_value = None    
    
    # Columns to be visualized
    cols_to_visualize = [veh_speed_flt_kph_col, accel_long_inv, accel_lat_inv]
    
    fig, axes = plt.subplots(nrows=len(cols_to_visualize), ncols=1, figsize=(10, 6), sharex=True)
    
    # Connect the mouse click event to the callback function
    plt.gcf().canvas.mpl_connect('button_press_event', on_plot_click)
    
    for i, col in enumerate(cols_to_visualize):
        combined_data_flt[col].plot(ax=axes[i], label = col)
        axes[i].legend([f'{col}'], loc='upper right')
        
        units_dict = {veh_speed_flt_kph_col: 'kph', accel_long_inv:'m/s²', accel_lat_inv:'m/s²'}
        axes[i].set_ylabel(f'{col} ({units_dict.get(col, "")})')
        axes[i].grid(True, linestyle='--', alpha=0.7)
        
        if col == accel_long_inv:
            axes[i].set_ylim(-4.1, 4.1)
            axes[i].set_yticks([-4, -2, 0, 2, 4])
        elif col == accel_lat_inv:
            axes[i].set_ylim(-3.1, 3.1)
            axes[i].set_yticks([-3, -2, -1, 0, 1, 2, 3])
    
    axes[-1].set_xlabel('Time (mm:ss)')
    
    # Calculate the total duration of the signal
    total_duration_seconds = total_seconds[-1]
    
    # Set the xtick intervals 
    interval_length = 120   # Unit: s
    # Calculate the number of intervals with 60s spacing
    num_intervals = int(total_duration_seconds / interval_length)
    
    xtick_positions_target = np.array(range(0, (num_intervals+1) * interval_length, interval_length))
    
    # The indices of elements in total_seconds that present in xtick_positions_target
    xtick_positions_indices = np.where(np.isin(total_seconds, xtick_positions_target))
    # Extract the first element of the tuple xtick_positions_indices[0], i.e. the array of indices
    indices_array = xtick_positions_indices[0]
    
    # The interval between two indices has to be at least min_interval
    filtered_indices = interval_filter(indices_array, min_inverval=580)
    
    # Determine the xtick position and labels
    xtick_positions = pd.Index(filtered_indices)
    xtick_labels = [f'{int(seconds) // 60:02d}:{int(seconds) % 60:02d}' for seconds in xtick_positions_target]

    axes[-1].set_xticks(xtick_positions)
    axes[-1].set_xticklabels(xtick_labels, fontsize=8)
    
    # Rotate xtick labels for better readability
    axes[-1].tick_params(axis='x', rotation=45)
    
        
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
    
    # Save the figure
    plt.savefig(f'{common_file_name}_figure.png')
    
    plt.show()

    
