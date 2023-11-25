import os
import pandas as pd
import numpy as np
from datetime import datetime as dt, timedelta
from scipy.signal import butter, filtfilt
from gps_time import GPSTime
import matplotlib.pyplot as plt

def formatDateTime(theDateTime):
    return dt.strptime(theDateTime, Datetimeformat)

def butter_lowpass_filter(data, cutoff_freq, sample_rate, order=4):
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def getDF(filename):
    # Reas CSV file into a DataFrame and adjust the 'date' column
    df = pd.read_csv(filename, delimiter=',')
    df_len = len(df)
    for i in range(df_len):
        df.loc[i, data_date] = formatDateTime(df.loc[i, data_date][:21]) + timedelta(hours=8)
    return df, df_len

def processGPS(gps):
    # Process GPS DataFrame
    global Vspeed_orig
    global SampleRate

    gps[data_date] = pd.to_datetime(gps[data_date])
    
    # Apply Butterworth filter to smooth the speed data
    gps["Vspeed_orig_filt"] = butter_lowpass_filter(gps[Vspeed_orig], cutoff_freq=2, sample_rate=SampleRate)
    
    
    # Calculate acceleration and jerk based on the filtered speed
    accl = np.gradient(gps["Vspeed_orig_filt"]) * SampleRate
    jerk = np.gradient(accl) * SampleRate
    
    # Apply Butterworth filter to smooth acceleration and jerk
    gps["accl"] = butter_lowpass_filter(accl, cutoff_freq=2, sample_rate=SampleRate)
    gps["jerk"] = butter_lowpass_filter(jerk, cutoff_freq=2, sample_rate=SampleRate)
    
    # convert speed to km/h
    gps["Vspeed"] = gps["Vspeed_orig_filt"] * 3.6

    return gps

def processACCL(accl):
    # Process accelerometer DataFrame
    accl[data_date] = pd.to_datetime(accl[data_date])
    
    # Apply Butterworth filter to smooth accelerometer data
    accl["g_lateral"] = butter_lowpass_filter(accl["1"], cutoff_freq=2, sample_rate=SampleRate)
    accl["g_longitudinal"] = butter_lowpass_filter(accl["2"], cutoff_freq=2, sample_rate=SampleRate)
    accl["g_Z"] = butter_lowpass_filter(accl["Accelerometer [m/s2]"], cutoff_freq=2, sample_rate=SampleRate)

    return accl

def processRT(rt):
    # Process RT sensor DataFrame
    global SampleRate
    global data_date
    global data_dateRT
    global Vspeed
    global VspeedRT
    global accelerationLongi
    global accelerationLongiRT
    global accelerationLateral
    global accelerationLateralRT
    global jerk
    global jerkRT

    rt[data_date] = rt[data_dateRT].apply(lambda x: dt.fromtimestamp(x))
    
    # Calculate jerk based on the longitudinal acceleration
    rt[jerkRT] = np.gradient(rt[accelerationLongiRT]) * SampleRate
    
    # Apply Butterworth filter to smooth jerk
    rt[jerkRT] = butter_lowpass_filter(rt[jerkRT], cutoff_freq=2, sample_rate=SampleRate)
    
    # Rename columns for consistency
    rt.rename(columns={VspeedRT: Vspeed, accelerationLongiRT: accelerationLongi,
                       accelerationLateralRT: accelerationLateral, jerkRT: jerk}, inplace=True)

    return rt

def plotFigure(df):
    # Plotting function
    l = 4
    plt.figure(figsize=(15, 20))
    # if "Vspeed" in df.columns:
    # print("df.columns:", df.columns)
    plt.subplot(l, 1, 1)
    plt.plot(df[data_date], df[Vspeed], label="speed")
    plt.plot(df[data_date], df[VspeedRT], label="RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    # if "accelerationLongi" in df.columns:
    plt.subplot(l, 1, 2)
    plt.plot(df[data_date], df[accelerationLongi], label="accl_GoPro")
    plt.plot(df[data_date], df[accelerationLongiRT], label="accl_RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    # if "jerk" in df.columns:
    plt.subplot(l, 1, 3)
    plt.plot(df[data_date], df[jerk], label="jerk_GoPro")
    plt.plot(df[data_date], df[jerkRT], label="jerk_RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    # if "accelerationLateral" in df.columns:
    plt.subplot(l, 1, 4)
    plt.plot(df[data_date], df[accelerationLateral], label="accelerationLateral_GoPro")
    plt.plot(df[data_date], df[accelerationLateralRT], label="accelerationLateral_RT")
    plt.legend(fontsize=5)
    plt.legend(loc='upper left')

    plt.show()

    """ 
    def mainGoPro(filename):
    # Main function for processing GoPro data
    counter = 0
    df, df_len = getDF(filename)
    df = processGPS(df)
    counter += 1
    temp = df
    if counter > 1:
        temp = pd.concat([temp, df1], ignore_index=True)
        temp.sort_values(data_date, ascending=True, inplace=True)
    return temp
    """

if __name__ == '__main__':
    SampleRate = 10  # Herz
    Datetimeformat = '%Y-%m-%dT%H:%M:%S.%f'
    DatetimeformatModified = '%Y-%m-%d %H:%M:%S.%f'
    Vspeed_orig = "GPS (2D) [m/s]"
    modifiedRTFilename = "R_T_processed.csv"
    mergedDataFilename = "merged_data.csv"
    # mergedGPSFilename = "merged_data_GPS.csv"
    # mergedACCLFilename = "merged_data_ACCL.csv"
    # curPath = os.path.abspath(os.curdir)
    counterGPS = 0
    counterACCL = 0
# columns definition
    data_date = "date"
    data_dateRT = "Time (GPS s)"
    Vspeed = "Vspeed"
    VspeedRT ="Speed horizontal (m/s)"
    VspeedGopro = "Vspeed"
    accelerationLongi = "accelerationLongi"
    accelerationLongiRT = "Acceleration forward (m/s²)"
    accelerationLongiGopro = "accl"
    accelerationLateral = "accelerationLateral"
    accelerationLateralRT = "Acceleration lateral (m/s²)"
    accelerationLateralGopro = "g_lateral"
    jerk = "jerk"
    jerkRT = "jerk"
    jerkGopro = "jerk"
# columns definition

    data_folder_path = "/Users/jackwong/02_Coding/00_repo/01_GoPro/01_Data"
    # Change the current working directory to the specified path
    os.chdir(data_folder_path)
     
    for filename in os.listdir():
        if filename == mergedDataFilename:
            gopro = pd.read_csv(filename, delimiter=',', parse_dates=["date"])
            # print(gopro.head())
        elif filename == modifiedRTFilename:
            rt = pd.read_csv(filename, delimiter=',', parse_dates=["date"])
            # print(rt.head())
            # print(rt.columns)
            rt.rename(columns={VspeedRT: "VspeedRT", accelerationLongiRT: "accelerationLongiRT",
                               accelerationLateralRT: "accelerationLateralRT", jerkRT: "jerkRT"}, inplace=True)
            # print(rt.columns)
            
            for i in range(len(rt)):
                rt.loc[i, 'date'] = GPSTime(week_number=0, time_of_week=rt.loc[i, data_dateRT])
                rt.loc[i, 'date'] = rt.loc[i, 'date'].to_datetime()
            
            rt["date"] = rt["date"] + timedelta(hours=8) - timedelta(seconds=18)
            rt["date"] = pd.to_datetime(rt["date"])
            
            print(rt.columns)
                  
    mergedData = pd.merge(gopro,rt, on = "date")
    
    plotFigure(mergedData)
    plt.show()
     