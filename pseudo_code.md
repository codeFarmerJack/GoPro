# 1. Add a function to adapt the acceleration automatically 
(1) If the json file not existed, create a new one from current settings.
(2) Create a boolean variable, auto_adpat, to specify if the auto-adaptation function will be used
    - This function can only be used when the GPS file exists and auto_adapt == true
	- If the auto_adapt == false, offset will be adapated manually as before.
(3) create a function offset_calc to calculate the acceleration offset 
(4) Assign the calculated offset to corresponding variables for further usage
(5) If auto_adapt == true, update their values in the json file
(6) If auto_adapt == true, adjust the offset automatically
(7) If auto_adapt == false, adjust the offset manually according to the json file.
