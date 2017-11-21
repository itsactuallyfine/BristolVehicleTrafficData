# -*- coding: utf-8 -*-
"""
Fast Fourier Transform vehicle traffic data plots

"""
import numpy as np
import pandas as pd
import os as os
import matplotlib.pyplot as plt

#matplotlib params
SMALLER_SIZE = 15
SMALL_SIZE = 25
MEDIUM_SIZE = 30
BIGGER_SIZE = 31

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALLER_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


# import summary link data...
summary_link_data = pd.read_csv('Summary_traffic_data_12.06.2k17.csv',header=0)
summary_ids = list(summary_link_data.my_sensor_ID)
summary_link_deets = list(summary_link_data.link_details)

#%%
os.chdir('towards_FFT_day_profiles')
file_list = os.listdir('.') # list of all traffic link files...
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
link_ids = [file_name.split('.')[0].split('_')[1] for file_name in file_list]

#for k in range(len(link_ids)):
for k in range(0,1):
    file_name = file_list[k]
    link_dataframe = pd.read_csv(file_name, header=0)

    timestamps = np.array(link_dataframe.columns[2:])
    timestamps = np.array([float(i) for i in timestamps])
    timestamps = timestamps / 60**2
    #vmphs_10days = np.array(link_dataframe.iloc[:100, 2:])
    days_dataframe_list = [link_dataframe[link_dataframe.week_day_num == i] for i in range(0,7) ]

#k = 1

    os.chdir('../plots_of_day_profiles')

    for i in range(0,7):

        fig = plt.figure()
        df = days_dataframe_list[i]
        mean = np.array(df.mean())[1:]
        std_dev = np.array(df.std())[1:]

        for j in range(len(days_dataframe_list[i])):
            #plt.plot(timestamps, df.iloc[j,2:], 'ok')
    #        plt.scatter(timestamps, df.iloc[j,2:], np.abs(df.iloc[j,2:] - mean))

            plt.scatter(timestamps, df.iloc[j,2:], c=(np.abs(df.iloc[j,2:] - mean))/std_dev, s = 10, edgecolors='face', cmap='gnuplot')


        plt.plot(timestamps, mean, '-g', linewidth=3)
        #plt.colorbar()
        cbar = plt.colorbar()
        cbar.set_label('Standard Deviations from the Mean Velocity', fontsize=23)
        cbar.ax.tick_params(labelsize=22)
        #cbar.ax.set_ylabel(fontsize=15)
        plt.title("Typical {0} Velocity Profile for Link {1}:\n{2}".format(days[i], link_ids[k], summary_link_deets[int(link_ids[k])]))
        plt.xlim(0,24)
        plt.xticks(np.arange(0,28,4))
        plt.xlabel("Time [Hours]")
        plt.ylabel("Velocity [mph]")
        fig.set_size_inches(16,9)
        #plt.plot(timestamps, mean + std_dev, 'r-', timestamps, mean - std_dev, 'r-',)
        plt.savefig("{0}s_on_link_{1}.png".format(days[i], link_ids[k]), dpi=100, bbox_inches='tight')


    os.chdir('../towards_FFT_day_profiles')
