#! /usr/bin/env python
"""
Created a pickle file from ulog from other use

Fred
12/10/2019
"""

#%% import

import os
import sys
import time
import math
import pickle

import pandas as pd
import numpy as np

from model import Flight, timeit
from list_param import Device, Position

import logging
from logging.handlers import RotatingFileHandler

#%% Config logger
logger = logging.getLogger()
# logging.basicConfig(filename='1_import.log',level=logging.DEBUG)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s ::  %(message)s"
)
file_handler = RotatingFileHandler("1_Start_import.log", "a", 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Redirect log on console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

### FUNCTIONS  ####


def timer(start, end):
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2} h {:0>2} min {:05.2f} s".format(int(hours), int(minutes), seconds)


#%% PARAMETERS
cwd = os.path.dirname(os.path.abspath(__file__))
log_name = "log_23_2019-9-29-15-15-10_heli_slow.ulg"
ulog_file_path = os.path.join(cwd, "samples", log_name)
Reload_file = True
gravity = 9.80665  # m·s-2

name_saved_file = "mflight_plot.pkl"

#%%  Prepare file
logger.info(" --- Start ----")

if Reload_file:
    # print("Reading Ulog file : " + str(ulog_file_name))

    mflight = Flight()

    mflight.add_data_file(ulog_file_path, Device.PIXRACER, Position.PILOT)
    mflight.add_info("Tulipe Glider", "Razor4", None, "Paul", 94.2, "Nice Place")

    logger.info("Writing : " + name_saved_file)

    with open(name_saved_file, "wb") as f:
        pickle.dump(mflight, f)

else:
    logger.info("Reading : " + name_saved_file)
    with open(name_saved_file, "rb") as f:
        mflight = pickle.load(f)

# Print the input Dataframe.
print(mflight)

#%%
df_data = mflight.data[0].list_avalable_data()
print(df_data)
# df_data.loc[df_data['parent']=='vehicle_local_position']

#%% Plot
mdf = mflight.get_df_by_position(Position.PILOT)[0]
print(mdf)

logger.info(" --- END ----")

print("END")

#%%
