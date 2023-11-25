import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# Function to create a low-pass Butterworth filter
def butter_lowpass_filter(data, cutoff_freq, sample_rate, order=4):
    # The Nyquist theorem states that in order to accurately reconstruct a signal, the sampling
    # frequency must be at least twice the maximum frequency present in the signal.
    nyquist = 0.5 * sample_rate     # the maximum frequency that can be accurately represented in the sample signal
    normal_cutoff = cutoff_freq / nyquist   # the specific frequency at which the filter begins to take effect
    # The normal_cutoff is the ratio of the actual cutoff frequency to the Nyquist frequency. It is a normalized
    # value that ranges from 0 to 1, where 1 corresponds to the Nyquist frequency.
    # when you design a filter, you may choose to specify the cutoff frequency directly or use the normal cutoff,
    # depending on the requirements of the filter design or library you are using.
    # Adjusting the cutoff frequency or normal cutoff allows you to control the trade-off between the amount of 
    # signal that is passed through and the amount that is attenuated by the filter.
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    # b, a = butter(N, Wn, btype='low', analog=False, output='ba')
    #   N: The order of the filter. Higher value of N result in a steeper roll-off but may introduce more phase
    #       distortion. Common values are 1, 2, 3, etc.
    #   Wn: The critical frequency or frequencies at which the filter's response starts to roll of.
    #       For a low-pass filter, Wn is the cut off frequency, expressed as a faction of the Nyquist
    #       frequency. For example, if the Nyquist frequency is 100Hz and you wnt a cutoff frequency   
    #       of 20Hz, you would set Wn = 0.2
    #   btype:  The type of filter. In this case, it's set to 'low' for a low-pass filter. Other opotions
    #           include 'high' for a high-pass filter, 'band' for a band-pass filter, and 'band-stop' for a
    #           band-stop (notch) filter.
    #   analog: If 'True', the filter design is in the analog domain. If 'False' (default), it's in the digital
    #           domain.
    #   output: The type of output, 'ba'(default) returns the numerator and denominator coefficients of the 
    #           transfer function.
    y = filtfilt(b, a, data)
    # 'filtfilt' stands for "filter for forward and backward". It filters the input data in both the forward 
    # and backward directions. It essentially applies  the filter twice: once in the forward direction and once 
    # in the backward direction
    
    return y

# Generate example data
time = np.linspace(0, 10, 1000, endpoint=False)  # Time vector from 0 to 10 seconds
frequency = 1  # Frequency of the signal (Hz)
data = np.sin(2 * np.pi * frequency * time) + 0.5 * np.random.normal(size=len(time))

# Parameters for the low-pass filter
cutoff_frequency = 2  # Adjust this value as needed
sample_rate = 100  # Adjust this value based on your actual sample rate

# Apply the low-pass filter
filtered_data = butter_lowpass_filter(data, cutoff_frequency, sample_rate)

# Plot the original and filtered data
plt.figure(figsize=(10, 6))
plt.plot(time, data, label='Original Data')
plt.plot(time, filtered_data, label=f'Filtered Data (cutoff={cutoff_frequency} Hz)')
plt.title('Low-pass Filter Example')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.show()
