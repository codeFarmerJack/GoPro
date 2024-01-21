# Define this class specfically for the plotting purpose

import matplotlib.pyplot as plt
class PlotManager:
    def __init__(self):
        # Initialize a dictionary to store text instances for each subplot
        self.subplot_texts = {}
        
    def on_the_plot(self, event, axes):
        if event.inaxes is not None and event.button == 1:
            target_x_value = event.xdata
            
            for ax in axes:
                # Remove the existing cursor with 'cursor' label
                existing_lines = [line for line in ax.lines if 'cursor' in line.get_label()]
                for line in existing_lines:
                    line.remove()
                    
                # Draw a new cursor at the updated x-value
                self.draw_cursor(ax, x_values = [target_x_value])
                
                y_values  = self.get_y_value(ax, target_x_value)
                
                # Update test for each subplot 
            plt.gcf().canvas.draw()
    
    def update_text(self, ax, x_value, y_value):
        # Check if text instance exists for the current subplot 
        if ax not in self.subplot_texts:
            # Create a new text instance if not exists
            self.subplot_texts[ax] = ax.text(0.95, 0.05, '', transfrom=ax.transAxes, 
                                             color='red', fontsize=8, 
                                             verticalalignment='bottom', horizontalalignment='right')
        
        # Update the text content for the current subplot
        self.subplot_texts[ax].set_text(f'X: {x_value: .2f}, Y: {y_value: .2f}')
        
    def draw_cursor(self, ax, x_values):
        for x in x_values:
            ax.axvline(x = x, color = 'r', linestyle = '--', label = 'cursor')
    
    def get_y_value(self, ax, x_value):
        line = ax.lines[0]
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        
        # Find the index of the closest x-value in data
        idx = (abs(x_data - x_value)).argmin()
        
        return y_data[idx]
        
    def update_bottom_right_text(ax, x_value, y_value):
        # Assuming the last axis is the bottom right one
        bottom_right_ax = ax
        
        # Add new text with x and y values
        bottom_right_ax.text(0.95, 0.05, f'X: {x_value:.2f}, Y:{y_value: .2f}',
                            transform=bottom_right_ax.transAxes, color='red', fontsize=8,
                            verticalalignment='bottom', horizontalalignment='right')
                