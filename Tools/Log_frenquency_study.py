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


    print("")
    print("{:<41} {:7}, {:10}".format("Name (multi id, message size in bytes)",
                                      "number of data points", "frequency"))

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

list_file= glob.glob('sample_log/*.ulg')
tot_file=len(list_file)
print(" file found ("+ str(tot_file) +") :")
for name in list_file:
    print(name)

list_file = ['sample_log/log_0_2019-9-14-21-54-24.ulg','sample_log/log_14_2019-9-24-23-31-14.ulg']

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
    print(dfg)

print ("-- END --")
