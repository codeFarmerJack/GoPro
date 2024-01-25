
import matplotlib.pylab as plt


class DataVisualization:
    def __init__(self, total_seconds):
        self.range_x_values = {'left': None, 'right': None}
        DataVisualization.x_series = total_seconds
    
    @staticmethod
    def get_y_value(ax, x_value):
        line = ax.lines[0]
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        
        # Find the index of the closest x-value in data
        idx = (abs(x_data - x_value)).argmin()
        return y_data[idx]
    
    @staticmethod
    def update_bottom_right_text(ax, x_left, x_right, average_value):
        # Remove the existing text with "bottom_right_text" label
        existing_texts = [text for text in ax.texts if 'bottom_right_text' in text.get_label()]
        for text in existing_texts:
            text.remove()
            
        # Display average value if both left-click and right-click happen
        if x_left is not None and x_right is not None:
            
            x_value_left = DataVisualization.x_series[int(x_left)]
            x_value_right = DataVisualization.x_series[int(x_right)]
            
            x_duration = abs(x_value_right - x_value_left)
            
            ax.text(0.98, 0.02, f'X_dur: {x_duration: .1f} s, Y_ave: {average_value: .2f}', transform=ax.transAxes, color='red', fontsize=8,
                    verticalalignment='bottom', horizontalalignment='right', label = 'bottom_right_text')
        # Display coordinates on left-click or right-click
        elif x_left is not None or x_right is not None:
            x_value_clicked = x_left if x_right is None else x_right

            x_value = DataVisualization.x_series[int(x_value_clicked)]
            y_value = DataVisualization.get_y_value(ax, x_value_clicked)
            
            ax.text(0.98, 0.02, f'X: {DataVisualization.format_time_ticks(x_value)}, Y:{y_value: .2f}', transform=ax.transAxes, color='red', fontsize=8,
                    verticalalignment='bottom', horizontalalignment='right',label = 'bottom_right_text')
    
    def on_plot_click(self, event):
        if event.inaxes is not None:
            if event.button == 1:       # Left click
                self.handle_left_click(event)
            elif event.button == 3:     # Right click
                self.handle_right_click(event)
        
    def handle_left_click(self, event):
        self.range_x_values['left'] = event.xdata
        self.update_cursors_and_text()
        
    def handle_right_click(self, event):
        if event.dblclick:  # Check if it's a double-click
            self.handle_right_double_click(event)
        else:
            self.range_x_values['right'] = event.xdata
            self.update_cursors_and_text()
        
    def handle_right_double_click(self, _):
        # Reset right click and update text
        self.range_x_values['right'] = None
        self.update_cursors_and_text()
    
    def update_cursors_and_text(self):
        for ax in plt.gcf().get_axes():
            
            # Remove the existing cursor with "cursor" label
            existing_lines = [line for line in ax.lines if 'cursor' in line.get_label()]
            for line in existing_lines:
                line.remove()
                
            # Remove the existing bottom right text with "bottom_right_text" label
            existing_texts = [text for text in ax.texts if 'bottom_right_text' in text.get_label()]
            for text in existing_texts:
                text.remove()
                
            # Draw a red cursor at the updated x-value from left-click
            if self.range_x_values['left'] is not None:
                ax.axvline(x=self.range_x_values['left'], color='red', linestyle='--', label='cursor_left')
                
            # Draw a new green cursor at the updated x-value from right-click
            if self.range_x_values['right'] is not None:
                ax.axvline(x=self.range_x_values['right'], color='green', linestyle='--', label='cursor_right')
            
            if any(value is not None for value in self.range_x_values.values()):
                # If at least one click happened
                non_none_values = [value for value in self.range_x_values.values()]
                if non_none_values:
                    start_index = int(min(filter(lambda x: x is not None, non_none_values)))
                    end_index = int(max(filter(lambda x: x is not None, non_none_values)))
                
                    selected_data = ax.lines[0].get_ydata()[start_index: end_index+1]
                    average_value = sum(selected_data) / len(selected_data) if len(selected_data) > 0 else None
                
                    self.update_bottom_right_text(ax, self.range_x_values['left'], 
                                                  self.range_x_values['right'], average_value)
                
                else:
                    # Handle the case where there are no None values
                    start_index = end_index = None
                    average_value = None
            else:
                # Handle the case where all values are None
                start_index = end_index = None
                average_value = None 
                
        plt.gcf().canvas.draw()
    
    @staticmethod
    # Format x-axis tick labels as 'mm:ss'
    def format_time_ticks(x):
        minutes = int(x // 60)
        seconds = int(x % 60)
        return f'{minutes:02d}:{seconds:02d}'
        
    