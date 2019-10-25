#! /usr/bin/env python
"""
compare parameters of Ulog file

Fred
25/10/2019
"""

#%% import

from __future__ import print_function

import argparse
import sys
import time
import math
import glob
import os

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



def info_to_df(ulog,file_name):
    """Extract param from ulog file
    """

    initial_param = ulog.initial_parameters


    df = pd.Series(initial_param).to_frame(file_name)
    return df


#%%  MAIN 
print("\n---START---")

Reload_file = False

Folder_path= '/home/fred/Ozone/paralogger/paralogger/samples'


list_file= glob.glob(Folder_path+'/*.ulg')
tot_file=len(list_file)
print(" file found ("+ str(tot_file) +") :")
for name in list_file:
    print(name)

#list_file = ['sample_log/log_0_2019-9-14-21-54-24.ulg','sample_log/log_14_2019-9-24-23-31-14.ulg']

dfg = pd.DataFrame()
i=0
for file_log in  list_file:
    file_name= file_log.split('/')[-1]
    i+=1
    print("\nReading Ulog file  ["+ str(i) +"/"+ str(tot_file)+"] : " + file_log ) 
    ulog = ULog(file_log, None, False)
    dfi = info_to_df(ulog,file_name)
    #print(dfi)

    print("append dfi to dfg")

    if len(dfg) == 0 :
        dfg =dfi
    else:
        dfg = dfg.join(dfi,how='left')

# Find rows where all equal
dfg['identic']=dfg.eq(dfg.iloc[:, 0], axis=0).all(1)



#Created a dataframe of different
df_diff= dfg[~dfg["identic"]]

print("\n ---- DF DIFF ---- \n")
print("Number of identic parameters: ")
print(dfg['identic'].value_counts())
print("\n Details: ")
print(df_diff)

#Export_ to excel
if 1:
    df_diff.to_excel("output_differnces.xlsx")


print("\n Ready ")

#%% END
print ("-- END --")


# %%
