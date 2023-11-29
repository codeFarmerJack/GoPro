# GoPro
The raw acceleration signal from GoPro contains some noises which interfere with further analysis.
So this aims to filter the acceleration in which we are interest.
I want to use the low pass filter partly or totally, it just depends on the noise distribution

# Requirements:
## 1. Low pass filter
    Compare the difference in speed, longitudinal acceleration, lateral acceleration and jerk before
    and after low-pass filtering. Aims to assess the potential signal optimization of low-pass filter
##     2. Interact with the figure to faciliate analysis
###     2.1 Ensure consistent vertical line position across different subplots when moving the line.
          For example, moving the line in subplot 1 should correspondingly change its position in subplot2.
####         2.1.1 Draw a vertical line that can move consistently across different subplots.
               * Let the initial x_value to be set as the starting point and then update its position with each mouse click
               * Update the vertical lines' x-coordinate to the position where the mouse is clicked.
###     2.2 show numerical value at intersections between vertical line and the signal
