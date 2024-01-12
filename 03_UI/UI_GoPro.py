import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os
import json 
import subprocess
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


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

    # Columns to be visualized
    cols_to_visualize = [veh_speed_flt_kph_col, accel_long_adj, accel_lat_adj]

    
    # Function to create and display the plot in a Tkinter window
    def display_plot():
        # Create a new Tkinter window
        root = tk.Tk()
        root.title("GoPro Data Visualization - Plot")

        # Create a Matplotlib figure and axes
        fig, axes = plt.subplots(nrows=len(cols_to_visualize), ncols=1, figsize=(10, 6), sharex=True)

        # Connect the mouse click event to the callback function
        plt.gcf().canvas.mpl_connect('button_press_event', on_plot_click)

        for i, col in enumerate(cols_to_visualize):
            combined_data_flt[col].plot(ax=axes[i], label=col)
            axes[i].legend([f'{col}'], loc='upper right')

            units_dict = {veh_speed_flt_kph_col: 'kph', accel_long_adj: 'm/s²', accel_lat_adj: 'm/s²'}
            axes[i].set_ylabel(f'{col} ({units_dict.get(col, "")})')
            axes[i].grid(True, linestyle='--', alpha=0.7)

            if col == accel_long_adj:
                axes[i].set_ylim(-4.1, 4.1)
                axes[i].set_yticks([-4, -2, 0, 2, 4])
            elif col == accel_lat_adj:
                axes[i].set_ylim(-3.1, 3.1)
                axes[i].set_yticks([-3, -2, -1, 0, 1, 2, 3])

        axes[-1].set_xlabel('Time (mm:ss)')

        # Define dynamic legends for subplot 2 and subplot 3
        text_legend_2 = axes[1].text(0.78, 0.12, '', transform=axes[1].transAxes, fontsize=8,
                                    verticalalignment='center', horizontalalignment='left')
        text_legend_3 = axes[2].text(0.78, 0.12, '', transform=axes[2].transAxes, fontsize=8,
                                    verticalalignment='center', horizontalalignment='left')

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

        # Embed the Matplotlib figure into the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add Matplotlib navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Display the Tkinter window
        root.mainloop()

    # Call the display_plot function
    display_plot()

if __name__ == "__main__":
    root = tk.Tk()
    app = GoProDataVisualizationApp(root)
    root.mainloop()
