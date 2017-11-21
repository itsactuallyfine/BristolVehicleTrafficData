# -*- coding: utf-8 -*-
"""
data cleaning and filtering pipeline
for raw csv data downloaded form Bristol City Council webiste

1. download latest and ALL jounery time datasets..
2. import, pick out the CURRENT running sensors (bristol city council updates running sensors on their webiste)
3. Assigne NEW section ID's by sorting for "section descriptions"
4. change all time stamps to datetime.datetime and in seconds...
5. remove date between august 2016 and jan 2017 (BCC verified system wide failure)
6. remove duplicates of data
7. save all in new csv, with new time stamps, and velocity in mph

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

def flatten_data(data):
    
    results = {}
    for entry in sorted(data, key=lambda t: t[0]):
        try:
            results[entry[0]] = results[entry[0]] + [entry[1]]
        except KeyError:
            results[entry[0]] = [entry[1]]
    return np.array([[key, np.mean(results[key])] for key in results.keys()])

def bristol_traffic_time_stamps(TD):
    
    # this function converts the date/time stamp given in the stupid bristol
    # csv file into a python date.time object
    
    new_time_stamps =[] # this is the actual datetime object
    new_time_stamps2 = [] # this is the value in seconds from some point in time
    
    for i in range(len(TD)):
        months = int(TD[i][0:2]) #-1 #to correct for 12.1.2016 problem where it adds a month
        d = int(TD[i][3:5])
        y= int(TD[i][6:11])
        
        if TD[i][20:22] == 'PM':
            if int(TD[i][11:13]) == 12:
                h = int(TD[i][11:13]) - 12 # this sorts out the 12.10pm +12 hrs problem
            else:
                h = int(TD[i][11:13])+12
        if TD[i][20:22] == 'AM':
            if int(TD[i][11:13]) == 12:
                h = int(TD[i][11:13]) - 12 # sorts out 12.10 am (-12 problem)
            else:
                h = int(TD[i][11:13])
        
        minutes = int(TD[i][14:16])
        s = int(TD[i][17:19])
    
        #mill_time = new_time(s,minutes,h,d,months,y,start_year)
        py_time = dt.datetime(y,months,d,h,minutes,s)
        
        new_time_stamps.append(py_time)
        new_time_stamps2.append(int(calendar.timegm(py_time.timetuple())))
    
    return new_time_stamps,new_time_stamps2    


def ToTimeStamp(d):
    #input some datetime.datetime object and it will return an awesome timestamp
    #one at a time though... should all be in seconds... I hope... 
    return calendar.timegm(d.timetuple())


current_data = pd.read_csv('Latest_journey_times.csv', header = 0)
# cts = list(current_data.time) # Current_Time_stamps
csd = list(current_data.section_description) # Current_Sectin_Desscriptions

unique_csd = unique1(csd)

DATA = pd.read_csv('Historic_journey_times.csv', header = 0)
SD = list(DATA.section_description) #Section_Descriptions

TT = list(DATA.travel_time) # travel time
DT = list(DATA.time) # Date time
Lat = list(DATA.lat)
Long = list(DATA.long)
ES = list(DATA.est_speed)
II = list(range(len(Long)))

         

# %% Find indicies where the current sensor data is in huge traffic csv file

csd_indxs = []
for i in range(len(unique_csd)):
    
    csd_indxs.append(findindex(SD,lambda x: x==unique_csd[i]))



# %%
#ctt = findreturn(TT,csd_indxs[i])
#cdt = findreturn(DT,csd_indxs[i])

# for the summary csv at the end....
my_sensor_ID= []
summary_link_deets= []
summary_lat= []
summary_long = []
summary_start_date= []
summary_end_date= []
summary_n= []
summary_mu_v= []

# do it for one fucking link at a time
for J in range(len(csd_indxs)):

#for J in range(0,2):
    
    csd_index = csd_indxs[J]
    
    cdt = findreturn(DT,csd_index) # all current date times for the link of interest
    index_cdt = findreturn(II,csd_index)
    unfiltered_data = list(zip(cdt,index_cdt))
    
    filtered_data1 = flatten_data2(unfiltered_data)
    
    old_time_stamps = []
    filtered_link_index =[]
    for i in range(len(filtered_data1)):
        old_time_stamps.append(filtered_data1[i][0])
        filtered_link_index.append(int(filtered_data1[i][1]))
        
    # converting all time stamps to datetime.datetime.fobject
    

    [new_dates, new_ts] = bristol_traffic_time_stamps(old_time_stamps)
    
    
    bb = list(zip(new_ts,filtered_link_index))
    
    cc = sorted(bb, key=lambda x: x[0])
    new_dates.sort()

#    X = filtered_link_index
#    Y = new_ts
#    [X for (Y,X) in sorted(list(zip(Y,X)), key=lambda pair:pair[0])]
    
#    ordered_filtered_data = sorted(bb, key=lambda x: x[1])
#    """ something is wrong... the data is not sorted by date when it goes into csv"""
#    
#    AA = list(zip(*ordered_filtered_data))
    
    AA = list(zip(*cc))
    ordered_filtered_ts = AA[0]
    ordered_filtered_index = AA[1]
    
#    plt.figure()
#    plt.plot(list(range(len(AA[0]))),AA[0])
#    #plt.plot(list(range(len(Y))),Y)
#    plt.xlabel('dummy')
#    plt.ylabel('ordered filtered ts')
#    plt.show()
    
    new_link_lat = []
    new_link_long = []
    new_link_es = []
    new_link_tt = []
    new_link_deets = []
    
    new_link_lat = findreturn(Lat,ordered_filtered_index)
    new_link_long = findreturn(Long,ordered_filtered_index)
    new_link_es = findreturn(ES,ordered_filtered_index)
    new_link_tt = findreturn(TT,ordered_filtered_index)
    new_link_deets = findreturn(SD,ordered_filtered_index)
    
    # quick check that it's all working smoothly....
    TEST_dates = findreturn(DT,ordered_filtered_index)
    [TEST_new_dates, TEST_new_ts] = bristol_traffic_time_stamps(TEST_dates)
    

    new_link_data = []
    #new_link_data = list(zip(new_dates,ordered_filtered_ts,new_link_es,new_link_tt,new_link_lat,new_link_long,new_link_deets))
    new_link_data = list(zip(TEST_new_dates,TEST_new_ts,new_link_es,new_link_tt,new_link_lat,new_link_long,new_link_deets))
    # Export to CSV
    link_csv_header = ['date','time_stamp','v_mph','travel_t_s','lat','long','link_details']
    df = pd.DataFrame(new_link_data)
    df.to_csv('LinkID_%s.csv' %(str(J)), index=False, header=link_csv_header)
    
    # %% FIGURES TO PLOT AND SAVE FOR EACH LINK!!!
    
    # velocity/time graph
    plt.figure()
    plt.plot(new_link_es,new_link_tt,'*')
    plt.xlabel('Velocity/ mph')
    plt.ylabel('Travel Time/ s')
    plt.title('linkID: %s, time/velocity graph, n=%s \n %s' % (str(J), str(len(new_link_es)), str(new_link_deets[10])))
    plt.savefig('Time_Velocity_graph_link_%s.png' % (str(J)))
    #plt.show()
    plt.close()
    
    #overall time graph
    plt.figure()
    plt.plot_date(new_dates,new_link_es,'*')
    plt.xlabel('dates')
    plt.ylabel('Velocity/mph')
    plt.title('linkID: %s, velocity overall time, n=%s \n %s' % (str(J), str(len(new_link_es)), str(new_link_deets[10])))
    plt.savefig('Overall_velocity_graph_link_%s.png' % (str(J)))
    #plt.show()
    plt.close()
    
    # velocity histogram
    fig, ax = plt.subplots()
    N, bins, patches = ax.hist(new_link_es, 100)
    
    fracs = N.astype(float)/N.max()
    norm = colors.Normalize(fracs.min(), fracs.max())
    
    for thisfrac, thispatch in zip(fracs, patches):
        color = cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)
    plt.title('Velocity Histrogram: link %s n=%s, mu=%2.2f \n %s' % (str(J),str(len(new_link_es)),float(np.mean(new_link_es)),str(new_link_deets[10])))
    plt.ylabel('Frequency')
    plt.xlabel('velocity/mph (bins: %s)' % (str(len(bins))) )
    plt.savefig('Histogram_velocity_link_%s.png' % (str(J)))
    #plt.show()
    plt.close()

# %% Overall summary csv?
    my_sensor_ID.append(J)
    summary_link_deets.append(str(new_link_deets[10]))
    summary_lat.append(str(new_link_lat[0]))
    summary_long.append(str(new_link_long[0]))
    summary_start_date.append(min(TEST_new_dates))
    summary_end_date.append(max(TEST_new_dates))
    summary_n.append(len(new_link_es))
    summary_mu_v.append(np.mean(new_link_es))



# now for the end game...
Summary_Data = []
#new_link_data = list(zip(new_dates,ordered_filtered_ts,new_link_es,new_link_tt,new_link_lat,new_link_long,new_link_deets))
Summary_Data = list(zip(my_sensor_ID,summary_link_deets,summary_lat,summary_long,summary_start_date,summary_end_date,summary_n,summary_mu_v))
# Export to CSV
link_csv_header = ['my_sensor_ID','link_details','lat','long','start_date','end_date','n_points','mean_v_mph']
df = pd.DataFrame(Summary_Data)
df.to_csv('Summary_traffic_data.csv', index=False, header=link_csv_header)
