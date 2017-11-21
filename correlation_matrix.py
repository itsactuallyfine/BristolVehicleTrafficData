# -*- coding: utf-8 -*-
"""
Created on Tue May 23 13:21:25 2017

@author: Pietro.Carnelli

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import datetime as dt
import matplotlib.cm as cm
import matplotlib.colors as colors

def findreturn(a,b):
    c=[]
    for i in range(len(b)):
        d = int(b[i])
        c.append(a[d])
                

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
    
    results = {}
    for entry in sorted(data, key=lambda t: t[0]):
        try:
            results[entry[0]] = results[entry[0]] + [entry[1]]
        except KeyError:
            results[entry[0]] = [entry[1]]
    return np.array([[key, np.min(results[key])] for key in results.keys()])


def ToTimeStamp(d):
    #input some datetime.datetime object and it will return an awesome timestamp
    #one at a time though... should all be in seconds... I hope... 
    return calendar.timegm(d.timetuple())

def traffic_v_intrp(start,end,link_id,intrp_t):
    
    link_data = pd.read_csv('All_link_data\LinkID_%s.csv' % (str(link_id)), header=0)
    TS = list(link_data.time_stamp)
    V = list(link_data.v_mph)
    
    index = findindex(TS, lambda x: ((x>=start_date)&(x<end_date))) #finds dates between values

    new_ts = findreturn(TS,index)
    new_v = findreturn(V,index)
    
    ts6 = np.float64(new_ts) #everything needs to be in the same float format
    ts7 = ts6-(max(ts6)-max(intrp_t)) # shifts the whole time thing to start at t=zero
        
    intrp_v = np.interp(intrp_t,ts7,new_v)
    
    return intrp_v

# %% import data....
# as usual start with one link at a time, aka link0
good_sensors = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18,20,23,24,25,26,27,28,29]

start_date = ToTimeStamp(dt.datetime(2016,5,1,0,0,0))
end_date = ToTimeStamp(dt.datetime(2017,5,1,0,0,0))






total_t = end_date - start_date
tp = 300 #(total_t/(len(new_ts)))/2

intrp_t = np.linspace(0,total_t,total_t/tp)


DATA = []

for i in range(len(good_sensors)):
    intrp_v =[]
    
    intrp_v = traffic_v_intrp(start_date,end_date,good_sensors[i],intrp_t)
    
    DATA.append(list(intrp_v))
 
corr_matrix = np.corrcoef(DATA)
