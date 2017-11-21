# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 19:31:48 2017

@author: Pietro.Carnelli
"""
import numpy as np
import datetime as dt
import pandas as pd
import calendar

def ToTimeStamp(d):
    #input some datetime.datetime object and it will return an awesome timestamp
    #one at a time though... should all be in seconds... I hope... 
    return calendar.timegm(d.timetuple())

def BackToDate(u): return dt.datetime.utcfromtimestamp(u)

def ToDates(d):
    new_dates = []
    for i in range(len(d)):
        new_dates.append(dt.datetime.strptime(d[i],'%Y-%m-%d %H:%M:%S'))
    return new_dates

def DayDateRange(start_day,end_day):
    ordered_days = []
    delta = (end_day-start_day)
    
    for i in range(delta.days+1):
        ordered_days.append(start_day + dt.timedelta(days=i))
    return ordered_days

start_day = dt.datetime(2016,2,1,0,0,0)
end_day = dt.datetime(2017,5,20,0,0,0)
the_days = DayDateRange(start_day, end_day ) 
day_list_ts =[]
for i in range(len(the_days)):
    day_list_ts.append(ToTimeStamp(the_days[i]))

t_maxes_16 = np.loadtxt("weather/cet_max_2016.txt")
t_maxes_17 = np.loadtxt("weather/cet_max_2017.txt")
t_mins_16 = np.loadtxt("weather/cet_min_2016.txt")
t_mins_17 = np.loadtxt("weather/cet_min_2017.txt")
t_means_16 = np.loadtxt("weather/cet_mean_2016.txt")
t_means_17 = np.loadtxt("weather/cet_mean_2017.txt")
precipitation = np.loadtxt("weather/precip2.txt")

day_for_frame = [d.day for d in the_days]
month_for_frame = [d.month for d in the_days]
year_for_frame = [d.year for d in the_days]
precip_for_frame = []
tmax_for_frame = []
tmin_for_frame = []
tmean_for_frame = []

for d in the_days:
    
    if d.year == 2016:
        i = 0
    elif d.year == 2017:
        i = 1
    else:
        pass
        
    min_years = [t_maxes_16, t_maxes_17]
    max_years = [t_mins_16, t_mins_17]
    mean_years = [t_means_16, t_means_17]
    
    tmin = min_years[i][d.day - 1, d.month]
    tmax = max_years[i][d.day - 1, d.month]
    tmean = mean_years[i][d.day - 1, d.month]
    if d.month +i*10 <= 12:
        precip = precipitation[d.month-2 + i*12, d.day+1 ]
    else:   
        precip = None
    
    tmax_for_frame.append(tmin)
    tmin_for_frame.append(tmax)
    tmean_for_frame.append(tmean)
    precip_for_frame.append(precip)
    
data = np.column_stack((the_days,
        day_list_ts,
        tmax_for_frame,
        tmin_for_frame,
        tmean_for_frame,
        precip_for_frame))

weather_header = ['date', 'timestamp', 'tmax', 'tmin', 'tmean', 'precip']

weather_table_of_days = pd.DataFrame(data)


weather_table_of_days.to_csv('traffic_weather_data4.csv', index=False,header=weather_header)