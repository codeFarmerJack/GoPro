# GoPro
The raw acceleration signal from GoPro contains some noises which interfere with further analysis.
So this aims to filter the acceleration in which we are interest.
I want to use the low pass filter partly or totally, it just depends on the noise distribution

Requirements:
1. Compare the difference in speed, longitudinal acceleration, lateral acceleration and jerk before
   and after low-pass filtering. Aims to assess the potential signal optimization of low-pass filter
2. Interact with the figure to faciliate analysis
   - Ensure consistent vertical line position across different subplots when moving the line.
     For example, moving the line in subplot 1 should correspondingly change its position in subplot2.
        * Draw a vertical line that can move consistently across different subplots.
   - show numerical value at intersections between vertical line and the signal
