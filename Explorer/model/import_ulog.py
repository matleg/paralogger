#! /usr/bin/env python

import numpy as np
import pandas as pd
import os.path
import time
import string

import logging
logger = logging.getLogger("import_Ulog")

from pyulog import ULog
from pyulog.px4 import PX4ULog

from functools import lru_cache

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

### FUNCTIONS ###

@timeit
@lru_cache(maxsize=None)
def load_ulog_file(file_name):
    """ load an ULog file
    :return: ULog object
    """
    # The reason to put this method into helper is that the main module gets
    # (re)loaded on each page request. Thus the caching would not work there.

    # load only the messages we really need
    msg_filter = ['battery_status', 'distance_sensor', 'estimator_status',
                  'sensor_combined', 'cpuload',
                  'vehicle_gps_position', 'vehicle_local_position',
                  'vehicle_local_position_setpoint',
                  'vehicle_global_position', 'actuator_controls_0',
                  'actuator_controls_1', 'actuator_outputs',
                  'vehicle_angular_velocity', 'vehicle_attitude', 'vehicle_attitude_setpoint',
                  'vehicle_rates_setpoint', 'rc_channels', 'input_rc',
                  'position_setpoint_triplet', 'vehicle_attitude_groundtruth',
                  'vehicle_local_position_groundtruth', 'vehicle_visual_odometry',
                  'vehicle_status', 'airspeed', 'manual_control_setpoint',
                  'rate_ctrl_status', 'vehicle_air_data',
                  'vehicle_magnetometer', 'system_power', 'tecs_status']
    try:
        ulog = ULog(file_name, msg_filter, disable_str_exceptions=False)
    except FileNotFoundError:
        print("Error: file %s not found" % file_name)
        raise

    # catch all other exceptions and turn them into an ULogException
    except Exception as error:
        traceback.print_exception(*sys.exc_info())
        raise ULogException()

    # filter messages with timestamp = 0 (these are invalid).
    # The better way is not to publish such messages in the first place, and fix
    # the code instead (it goes against the monotonicity requirement of ulog).
    # So we display the values such that the problem becomes visible.
#    for d in ulog.data_list:
#        t = d.data['timestamp']
#        non_zero_indices = t != 0
#        if not np.all(non_zero_indices):
#            d.data = np.compress(non_zero_indices, d.data, axis=0)

    return ulog

#%% PARAMETERS 

gravity = 9.80665 #m·s-2


#################################################################

def ulog_list_data(file_path):
    logger.info("\n Ulog ulog_list_data: " +str(file_path))

    ulog = load_ulog_file(file_path)
    for cat in ulog.data_list:
        print(cat.name)







def ulog_to_df(file_path):
    logger.info("generated_dataFrame_Ulog from: " +str(file_path))

    ulog = load_ulog_file(file_path)
    px4_ulog = PX4ULog(ulog)
    px4_ulog.add_roll_pitch_yaw()

    vehicle_attitude = ulog.get_dataset('vehicle_attitude')
    vehicle_local_position = ulog.get_dataset('vehicle_local_position')

    timestamp = vehicle_attitude.data['timestamp']  # in microsecond
    timestamp_us_0 = [(timestamp[i] - timestamp[0]) for i in range(len(timestamp))]

    pitch = vehicle_attitude.data['pitch']
    roll = vehicle_attitude.data['roll']
    yaw = vehicle_attitude.data['yaw']
    yaw_rate = vehicle_attitude.data['yawspeed']

    # Second data
    timestamp_us_local = vehicle_local_position.data['timestamp']
    timestamp_us_0_vehicule = [(timestamp_us_local[i] - timestamp_us_local[0])/1000000 for i in range(len(timestamp_us_local))]
    accel_x = vehicle_local_position.data['ax'] / gravity 
    accel_y = vehicle_local_position.data['ay'] / gravity
    accel_z = vehicle_local_position.data['az'] / gravity

    #Info Log
    print("\nInfo_log: ")
    sd_log = ulog.initial_parameters["SDLOG_PROFILE"]
    print("SDLOG_Profile: ",sd_log)

    print("\nCreating Dataframe")

    # intialise data of lists. 
    data = {'timestamp':timestamp, 'timestamp_us_0':timestamp_us_0,'pitch':pitch, 'roll':roll, 'yaw':yaw , 'yaw_rate':yaw_rate} 
    
    # Create DataFrame 
    df = pd.DataFrame(data) 
    df['delay_log']=df['timestamp'].diff()  # Calculate the delay  between two records in micro second , around 4000 ms = 0.0004 so 250 hz 
    df['timestamp_s_0'] = df['timestamp_us_0']/1000000

    #Create Dataframe 2
    data2 = {'timestamp':timestamp_us_local,'accel_x':accel_x, 'accel_y':accel_y, 'accel_z':accel_z}
    df2 = pd.DataFrame(data2)

    #Merging the two dataframe
    df_G=pd.merge(df, df2, on="timestamp" ,how='left')

    #interpolate Nan datas:
    df_G['accel_x'].interpolate(method='polynomial', order=2 ,inplace=True)
    df_G['accel_y'].interpolate(method='polynomial', order=2 ,inplace=True)
    df_G['accel_z'].interpolate(method='polynomial', order=2 ,inplace=True)

    return df_G

