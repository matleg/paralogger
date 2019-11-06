"""
Created a pickle file from ulog from other use

Fred
12/10/2019
"""

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

# FUNCTIONS:
def config_logger():
    logger = logging.getLogger()
    # logging.basicConfig(filename='1_import.log',level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s ::  %(message)s"
    )
    file_handler = logging.handlers.RotatingFileHandler("1_log_paralogger.log", "a", 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Redirect log on console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger


def timer(start, end):
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2} h {:0>2} min {:05.2f} s".format(int(hours), int(minutes), seconds)

# PARAMETERS
logger = config_logger()
log_name = "log_6_2019-11-6-13-32-36_flight_1.ulg"
name_saved_file = "mflight_plot_V1.pkl"
reload_file = True


def load_file(ulog_file_path, reload=True):
    """ Main function to load a Ulg file and create a Flight Object
    return : Flight object ( and saved or not  in a pkl file) 
    """
    if reload_file:
        # print("Reading Ulog file : " + str(ulog_file_name))

        mflight = Flight()

        mflight.add_data_file(ulog_file_path, Device.PIXRACER, Position.PILOT)
        mflight.add_info("Tulipe Glider", "Razor4", None, "Paul", 94.2, "Nice Place")
        mflight.add_general_section()

        logger.info("Writing : " + name_saved_file)
        with open(name_saved_file, "wb") as f:
            pickle.dump(mflight, f)

    else:
        logger.info("Reading : " + name_saved_file)
        with open(name_saved_file, "rb") as f:
            mflight = pickle.load(f)


    # Print Data for debug.
    logger.debug(mflight)
    df_data = mflight.data[0].list_available_data()
    logger.debug(df_data)
    # df_data.loc[df_data['parent']=='vehicle_local_position']

    mdf = mflight.get_df_by_position(Position.PILOT)[0]
    logger.debug(mdf)



def main():
    
    logger.info(" --- Start ----")
    cwd = os.path.dirname(os.path.abspath(__file__))
    logger.info('cwd:' + cwd)
    ulog_file_path = os.path.join(cwd, "samples", log_name)
    logger.info('ulog_file_path:' + ulog_file_path)

    load_file(ulog_file_path, reload=reload_file)
    
    logger.info(" --- END ----")
    print("END")



if __name__ == '__main__':
    main()


