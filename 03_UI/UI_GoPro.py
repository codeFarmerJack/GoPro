import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os
import json 
import subprocess

class GoProDataVisualizationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("GoPro Data Visualization")
        
        # Default values
        self.common_file_name = "GX020188_HERO11"
        self.raw_data_folder_path = "/Users/jackwong/02_Coding/00_repo/01_GoPro/RawData"
        self.sample_rate = 10
        self.cutoff_freq = 0.3
        self.atten_order = 3
        self.accel_long_offset = -0.78
        self.accel_lat_offset = 0.48
        
        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Common File Name
        self.common_file_name_label = tk.Label(self.master, text="Common File Name:")
        self.common_file_name_entry = tk.Entry(self.master)
        self.common_file_name_entry.insert(0, self.common_file_name)
        
        # Raw Data Folder Path
        self.raw_data_folder_path_label = tk.Label(self.master, text="Raw Data Folder Path:")
        self.raw_data_folder_path_entry = tk.Entry(self.master)
        self.raw_data_folder_path_entry.insert(0, self.raw_data_folder_path)
        
        # Sample Rate
        self.sample_rate_label = tk.Label(self.master, text="Sample Rate:")
        self.sample_rate_entry = tk.Entry(self.master)
        self.sample_rate_entry.insert(0, self.sample_rate)
        
        # Cutoff Frequency
        self.cutoff_freq_label = tk.Label(self.master, text="Cutoff Frequency:")
        self.cutoff_freq_entry = tk.Entry(self.master)
        self.cutoff_freq_entry.insert(0, self.cutoff_freq)
        
        # Attenuation Order
        self.atten_order_label = tk.Label(self.master, text="Attenuation Order:")
        self.atten_order_entry = tk.Entry(self.master)
        self.atten_order_entry.insert(0, self.atten_order)
        
        # Acceleration Long Offset
        self.accel_long_offset_label = tk.Label(self.master, text="Acceleration Long Offset:")
        self.accel_long_offset_entry = tk.Entry(self.master)
        self.accel_long_offset_entry.insert(0, self.accel_long_offset)
        
        # Acceleration Lat Offset
        self.accel_lat_offset_label = tk.Label(self.master, text="Acceleration Lat Offset:")
        self.accel_lat_offset_entry = tk.Entry(self.master)
        self.accel_lat_offset_entry.insert(0, self.accel_lat_offset)
        
        # Run Button
        self.run_button = tk.Button(self.master, text="Run Calculation", command=self.run_calculation)
        
        # Grid layout
        self.common_file_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.common_file_name_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2, sticky="ew")
        self.raw_data_folder_path_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.raw_data_folder_path_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="ew")
        self.browse_button.grid(row=1, column=3, padx=5, pady=5)
        self.sample_rate_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sample_rate_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.cutoff_freq_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.cutoff_freq_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.atten_order_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.atten_order_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.accel_long_offset_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.accel_long_offset_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.accel_lat_offset_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.accel_lat_offset_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        self.run_button.grid(row=7, column=1, pady=10, columnspan=2)
        
        # Configure column weights for resizing
        for i in range(5):  # Assuming you have 5 columns
            self.master.columnconfigure(i, weight=1)

    def run_calculation(self):
        # Update variables with user input
        self.common_file_name = self.common_file_name_entry.get()
        self.raw_data_folder_path = self.raw_data_folder_path_entry.get()
        self.sample_rate = int(self.sample_rate_entry.get())
        self.cutoff_freq = float(self.cutoff_freq_entry.get())
        self.atten_order = int(self.atten_order_entry.get())
        self.accel_long_offset = float(self.accel_long_offset_entry.get())
        self.accel_lat_offset = float(self.accel_lat_offset_entry.get())

        # Run the GoProDataVisualization.py script
        script_path = "GoProDataVisualization.py"
        command = f"python {script_path}"
        subprocess.run(command, shell=True)

        # After the calculation, open the Tkinter window to interact with the plot figure
        self.display_plot()

    
    def display_plot(self):
        # Open a new Tkinter window to display the plot figure
        plot_window = tk.Toplevel(self.master)
        plot_window.title("GoPro Data Visualization - Plot")

        # Create a Matplotlib figure and axes 
        fig, axes = plt.subplot(nrows=len(cols_to_visualize))

if __name__ == "__main__":
    root = tk.Tk()
    app = GoProDataVisualizationApp(root)
    root.mainloop()
