def iir_lowpass_butterworth(signal_data: pd.Series,
                            passband_hz,
                            stopband_hz,
                            passband_ripple,
                            stopband_attenuation) -> pd.Series:
    """Infinite Impulse Response (IIR) lowpass butterworth filter from scipy's signal
    package. This is used to remove noise from a signal depending on criteria given.
    For a good description of parameters:
    https://www.dsprelated.com/showarticle/164.php
    Args:
        signal_array (np.array): raw data array that does not contain nan values
        passband_hz (float): This is the frequency range which we desire to let
        the signal through with minimal attenuation.
        stopband_hz (float):  This is the frequency range which the signal
        should be attenuated.
        passband_ripple (float): The max variation in the passband, in decibals.
        stopband_attenuation (float): The max level in the stopband, in decibals.
        sampling_frequency (float): sampling frequency of resampled data
    Returns:
        np.array: filtered signal array
    """
    signal_frequency = approximate_frequency(signal_data)
    # get indices of Nans in the series
    nan_indices = signal_data[signal_data.isnull()].index
    interpolated_signal = signal_data.interpolate(method="index", limit_direction="both")
    index_array = interpolated_signal.index
    signal_array = interpolated_signal.values
    # check no remaining nans
    if np.isnan(signal_array).all():
        raise MappingException("Bad signal given to IIR filter.")
    elif np.isnan(signal_array).any():
        raise MappingException("Temporary replacement of nans in IIR filter has failed.")
    # create filter
    sos_filter_design = signal.iirdesign(
        wp=passband_hz,  # Passband edge frequencies. For digital filters, these are in the same units as fs.
        ws=stopband_hz,  # Stopband edge frequencies. For digital filters, these are in the same units as fs.
        gpass=passband_ripple,  # The maximum loss in the passband (dB).
        gstop=stopband_attenuation,  # The minimum attenuation in the stopband (dB).
        analog=False,
        ftype='butter',
        output='sos',
        fs=signal_frequency)
    # apply filter
    filtered_signal = signal.sosfiltfilt(sos_filter_design, signal_array)
    # recreate series with filtered data
    filtered_series = pd.Series(data=filtered_signal, index=index_array)
    # replace temporary nan replacement values with Nans
    filtered_series[nan_indices] = np.nan
    return filtered_series
