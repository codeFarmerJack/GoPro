
import matplotlib.pylab as plt


class DataVisualization:
    
    
    
    def __init__(self):
        self.target_x_value = None
    
    @staticmethod
    def get_y_value(ax, x_value):
        line = ax.lines[0]
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        
        # Find the index of the closest x-value in data
        idx = (abs(x_data - x_value)).argmin()
        return y_data[idx]
    
    @staticmethod
    def update_bottom_right_text(ax, x_value, y_value):
        
        # Remove the existing text with "bottom_right_text" label
        existing_texts = [text for text in ax.texts if 'bottom_right_text' in text.get_label()]
        
        for text in existing_texts:
            text.remove()
            
        # Add new text with x and y values
        ax.text(0.98, 0.02, f'X: {x_value:.2f}, Y:{y_value: .2f}', transform=ax.transAxes, color='red', fontsize=8,
                verticalalignment='bottom', horizontalalignment='right',label = 'bottom_right_text')
    
    
    def on_plot_click(self, event):
        
        if event.inaxes is not None and event.button == 1:
            
            self.target_x_value = event.xdata

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
                ax.axvline(x = self.target_x_value, color = 'r', linestyle = '--', label = 'cursor')
                
                y_values = self.get_y_value(ax, self.target_x_value)
                self.update_bottom_right_text(ax, self.target_x_value, y_values)
                
            plt.gcf().canvas.draw()

    
    @staticmethod
    # Format x-axis tick labels as 'mm:ss'
    def format_time_ticks(x, pos):
        minutes = int(x // 60)
        seconds = int(x % 60)
        return f'{minutes:02d}:{seconds:02d}'
        
    