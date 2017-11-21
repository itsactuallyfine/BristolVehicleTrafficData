# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 10:59:22 2017

@author: Pietro.Carnelli

lets load some link data, then split it by day, do some feature gathering and then
save output per link...

"""
import numpy as np
import pandas as pd
import calendar
import datetime as dt
import os as os
import matplotlib.pyplot as plt

#%% Claaaaasic PDawg mother fucker functions
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

def findreturn(a,b):
    c=[]
    for i in range(len(b)):
        d = int(b[i])
#        if len(a[d])>1:
#            c.append(a[d][0])
#        else:
        c.append(a[d])
#     print('no, sorry dude, the small dick(b) must go into the BIG dick(a)')
    return c

def unique1(a):
    b = set(a)
    return list(b)

def findindex(a, func):
    return [i for (i,val) in enumerate(a) if func(val)]

def flatten_data2(data):
    # so the data needs to be in the form: [[a_0,b_0],[a_0,b_1]...etc]
    #function will find all instances of a being duplicated, average them and then
    #save the value next to a_0, so that a_0 = mean(b_0,b_1...)
    #needs numpy!
    
    results = {}
    for entry in sorted(data, key=lambda t: t[0]):
        try:
            results[entry[0]] = results[entry[0]] + [entry[1]]
        except KeyError:
            results[entry[0]] = [entry[1]]
    return np.array([[key, np.min(results[key])] for key in results.keys()])

#%% gathering all the link data:

min_num_data_points_per_day = 50
bins = [0,5,10,15,20,25,30,40,50,60,70,100]
num_sampling_points = 500

link_csv_header = ['date','time_stamp','min_v_mph','max_v_mph','mean_v_mph','median_v_mph','var_v_mph','max_dvdt','min_dvdt','bin_5','bin_10','bin_15','bin_20','bin_25','bin_30','bin_40','bin_50','bin_60','bin_70','bin_100']   
    
os.chdir('traffic_data')
file_list = os.listdir() # list of all traffic link files...

for i in range(len(file_list)):
    LINK_DAY_PROFILE = []
    file_name = file_list[i]
    link_dataframe = pd.read_csv(file_name, header=0)
    
    # load all dates...
    # good_sensors = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18,20,23,24,25,26,27,28,29]
    
    overall_start_date = ToTimeStamp(dt.datetime(2016,2,1,0,0,0))
    overall_end_date = ToTimeStamp(dt.datetime(2017,5,20,0,0,0))
    
    link_ts = list(link_dataframe.time_stamp)
    link_dates = list(link_dataframe.date)
    link_vmph = list(link_dataframe.v_mph)
    
    link_dt_dates = ToDates(link_dates)
    
    overall_date_index = findindex(link_ts, lambda x: ((x>=overall_start_date)&(x<overall_end_date)))
    filtered_link_ts = findreturn(link_ts,overall_date_index)
    filtered_link_vmph = findreturn(link_vmph,overall_date_index)
    filtered_dt_dates = findreturn(link_dt_dates,overall_date_index)
    
#    start_day = min(filtered_dt_dates)
#    end_day = max(filtered_dt_dates)
    day_list = DayDateRange(BackToDate(overall_start_date) ,BackToDate(overall_end_date))
    
    
    
    for k in range(len(day_list)-1):
        
        today = day_list[k]
        today = today.replace(hour=0,minute=0,second=0)
        tomorrow = today + dt.timedelta(days=1)
        
        today_ts = ToTimeStamp(today)
        tomorrow_ts = ToTimeStamp(tomorrow)
        
        day_indices_list = findindex(filtered_link_ts, lambda x: ((x>=today_ts)&(x<tomorrow_ts)))
        day_vmph_list = findreturn(filtered_link_vmph ,day_indices_list)
        day_ts_list = findreturn(filtered_link_ts ,day_indices_list)
        
        if len(day_indices_list)>1:
            #checking again for FUCKING duplicates!!!
            link_day_data = list(zip(day_ts_list,day_vmph_list))
            A = flatten_data2(link_day_data)
            A2 = A[A[:,0].argsort()]
            
            day_ts_list2 = A2[:,0]
            day_vmph_list2 = A2[:,1]
            
        
            # Now check for length, mean and spread of data for that day
            num_data_points = len(day_ts_list2)
            ratio_num_points = num_data_points /min_num_data_points_per_day
            range_ts = (max(day_ts_list2)-min(day_ts_list2))/(60*60*24)
            day_v_mean = np.mean(day_vmph_list2)
    
            if (ratio_num_points>1)&(range_ts>0.7)&(day_v_mean>1):
                # cacluate all usefull traffic day features...
                
                day_traffic_features = []
                day_traffic_features.append(today)
                day_traffic_features.append(today_ts)
                day_traffic_features.append(min(day_vmph_list2))
                day_traffic_features.append(max(day_vmph_list2))
                day_traffic_features.append(day_v_mean)
                day_traffic_features.append(np.median(day_vmph_list2))
                day_traffic_features.append(np.var(day_vmph_list2))
                
                # more complex/convoluted features
                intrp_ts = np.linspace(today_ts,tomorrow_ts,num_sampling_points)
                intrp_vmph = np.interp(intrp_ts,day_ts_list2,day_vmph_list2)
                
        			# max/min gradiet changes
                day_traffic_features.append(max(np.diff(intrp_vmph)/np.diff(intrp_ts)))
                day_traffic_features.append(min(np.diff(intrp_vmph)/np.diff(intrp_ts)))
        
                    # quick little day histogram?
                N = np.histogram(intrp_vmph,bins)
                vmph_day_histogram = N[0]*(100/num_sampling_points)
                for h in range(len(vmph_day_histogram)):
                    day_traffic_features.append(vmph_day_histogram[h])
                
                LINK_DAY_PROFILE.append(np.transpose(day_traffic_features))
        
    if len(LINK_DAY_PROFILE)>1:
        os.chdir('../link_day_profiles')
        df = pd.DataFrame(LINK_DAY_PROFILE)
        df.to_csv('%s_day_profiles.csv' % (file_name[0:-4]),index=False,header=link_csv_header)
        os.chdir('../traffic_data')
        
    
    
    
##data4 = data3[data3[:,0].argsort()] # sorts data cleverly by column 0,
#plt.figure()
#plt.plot(day_ts_list,day_vmph_list,'*-k')
#plt.plot(day_ts_list2,day_vmph_list2,'or')
#plt.plot(day_ts_list2[1:],np.diff(day_vmph_list2)/np.diff(day_ts_list2))
#
#			# precentage of day spent with major congestion <6mph?
#congestion_index = findindex(intrp_vmph,lambda x: x<congestion_mph_limit)
#congestion_percentage = (len(congestion_index)/len(intrp_ts))*100
#day_traffic_features.append(congestion_percentage)
