#! /usr/bin/env python
"""
Extract parameters from an batch of ULog file
And Created a table of log parameter and their frequency

Fred
27/09/2019
"""

#%% import

from __future__ import print_function

import argparse
import sys
import time
import math
import glob

from pyulog import ULog
from pyulog.px4 import PX4ULog

import pandas as pd 
import numpy as np


from functools import lru_cache
#pylint: disable=unused-variable, too-many-branches



#%%  functions and decorator
###  DECORATOR ####

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()       
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f s' % \
                  (method.__name__, (te - ts) ))
        return result    
    return timed

### FUNCTIONS  ####


#%% PARAMETERS 

ulog_file_name = 'sample_log/log_0_2019-9-14-21-54-24.ulg'


def info_to_df(ulog, verbose,file_name):
    """Show general information from an ULog"""

    time_s= int((ulog.last_timestamp - ulog.start_timestamp)/1e6)
    print("time_s",time_s)

    sd_log = ulog.initial_parameters["SDLOG_PROFILE"]
    print("sd_log",sd_log)

    # print("")
    # print("{:<41} {:7}, {:10}".format("Name (multi id, message size in bytes)",
    #                                   "number of data points", "frequency"))

    data = []
    data_list_sorted = sorted(ulog.data_list, key=lambda d: d.name + str(d.multi_id))
    for d in data_list_sorted:
        message_size = sum([ULog.get_field_size(f.type_str) for f in d.field_data])
        num_data_points = len(d.data['timestamp'])
        name_id = "{:}".format(d.name)
        data.append(dict({'name': name_id, 'mode':sd_log  , 'frequency':num_data_points / time_s,
         'mess_size':message_size, 'file':file_name}))
        #
        # print(" {:<40}  {:2f}".format(name_id, num_data_points / time_s))


    df = pd.DataFrame(data)
    return df


#%%  MAIN 
print("\n---START---")

Reload_file = False

name_df_input= 'dfg_save.pkl'

if Reload_file :

    list_file= glob.glob('sample_log/runpendulum/*.ulg')
    tot_file=len(list_file)
    print(" file found ("+ str(tot_file) +") :")
    for name in list_file:
        print(name)

    #list_file = ['sample_log/log_0_2019-9-14-21-54-24.ulg','sample_log/log_14_2019-9-24-23-31-14.ulg']

    dfg = pd.DataFrame()
    i=0
    for file_log in  list_file:
        i+=1
        print("\nReading Ulog file  ["+ str(i) +"/"+ str(tot_file)+"] : " + file_log ) 
        ulog = ULog(file_log, None, False)
        dfi = info_to_df(ulog, False,file_log)
        #print(dfi)

        print("append dfi to dfg")

        dfg = pd.concat([dfg,dfi])

    print("Writing : df_ulog.pkl ")
    dfg.to_pickle(name_df_input)
else:
    print("Loading : df_ulog.pkl ")
    dfg = pd.read_pickle(name_df_input)

print(dfg)


print("\n Ready ")

table_freq_mean = pd.pivot_table(dfg, values=['frequency'], index=['name'],columns=['mode'],
                         aggfunc={'frequency': np.mean})

table_freq_std = pd.pivot_table(dfg, values=['frequency'], index=['name'],columns=['mode'],
                         aggfunc={'frequency': np.std})

table_size_mess_mean = pd.pivot_table(dfg, values=['mess_size'], index=['name'],columns=['mode'],
                         aggfunc={'mess_size': np.mean})


print ("\n Mean frequency: ")
print(table_freq_mean)

print ("\n Mean std deviation: ")
print(table_freq_std)

print ("\n Mean message_size: ")
print(table_size_mess_mean)

#Adding info on mode  used
print ("\n Details modes used: ")
print ("mode \t binary_value \t plain_text ")

list_used_mode = list(dfg["mode"].unique())
dict_sd_mode = {0: "Default set",
1: "Estimator replay (EKF2)",
2: "Thermal calibration",
3: "System identification",
4: "High rate",
5: "Debug",
6: "Sensor comparison",
7: "Computer Vision and Avoidance"}

def bit_mask2text(input_value,dict_values):
    #bin_value = bin(input_value).zfill(7)
    bin_value = '{0:08b}'.format(input_value)
    plain_txt_mode = '' 
    bin_value_list = list(bin_value)  
    bin_value_list_reverse = bin_value_list[::-1]  # Reverse to have the lower weight bit first
    #print(bin_value_list_reverse)
    #print(str(input_value),str(bin_value))

    i=0
    for bit in bin_value_list_reverse:
        if "1" in bit  :
            if len(plain_txt_mode ) > 0 :
                plain_txt_mode =  plain_txt_mode + " + "
            plain_txt_mode = plain_txt_mode + dict_values[i] 
        i+=1

    print("{:4d} \t {:8s} \t {:s}".format(input_value, bin_value ,plain_txt_mode))


for mode in list_used_mode:
    bit_mask2text(mode , dict_sd_mode)


print ("-- END --")
