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
            logger.info('%r  %2.2f s' % \
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
    msg_filter = ['battery_status', 'estimator_status',
                  'sensor_combined', 'cpuload',
                  'vehicle_gps_position', 'vehicle_local_position',
                  'vehicle_global_position', 'vehicle_attitude', 
                  'vehicle_rates_setpoint', 
                  'vehicle_attitude_groundtruth',
                  'vehicle_local_position_groundtruth', 
                  'vehicle_status', 'airspeed', 
                  'rate_ctrl_status', 'vehicle_air_data',
                  'vehicle_magnetometer', 'system_power']

                  # has been removed , because useless:
                  #     position_setpoint_triplet
                  #     'actuator_controls_1' ,'actuator_controls_0','actuator_outputs'
                  #     distance_sensor
                  #     'vehicle_local_position_setpoint', 'vehicle_angular_velocity','vehicle_attitude_setpoint' 
                  #     'tecs_status'
                  #     'rc_channels', 'input_rc',
                  #     'manual_control_setpoint','vehicle_visual_odometry'
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
@timeit
def ulog_list_data(file_path):
    """ Create a panada dataframe with all the record avaible,
     the number and frequency.
        """
    logger.info("\n Ulog ulog_list_data: " +str(file_path))

    ulog = load_ulog_file(file_path)
    logger.debug(ulog)

    time_s= int((ulog.last_timestamp - ulog.start_timestamp)/1e6)
    logger.info("time_s: ",time_s)

    data = []
    data_list_sorted = sorted(ulog.data_list, key=lambda d: d.name + str(d.multi_id))
    for d in data_list_sorted:
        parent_id = "{:}".format(d.name)
        for d2 in d.data:
            try:
                size = d.data[d2].size
                avg = np.mean(d.data[d2])
                std = np.std(d.data[d2])
            except:
                print("")

            name_id = "{:}".format(d2)
            data.append(dict({'parent': parent_id, 'name':name_id, 'size':size ,'frequency':size / time_s , 'avg':avg ,'std':std }))

    df = pd.DataFrame(data)
    return df



def ulog_param(file_path):
    """ Extract all the parameters of the Ulog
        """

    logger.info("\n Ulog_param: " +str(file_path))
    dict_param={}

    ulog = load_ulog_file(file_path)

    dict_param['initial_parameters'] = ulog.initial_parameters
    dict_param['msg_info_dict'] = ulog.msg_info_dict
    dict_param['logged_messages'] = ulog.logged_messages
    dict_param['file_corruption'] = ulog.file_corruption
    dict_param['logged_messages'] = ulog.logged_messages

    return dict_param


@timeit
def ulog_to_df(file_path):
    """ Created a Panda dataframe with all the interestion data
        All the data are join by the timestamp
        """
    logger.info("generated_dataFrame_Ulog from: " +str(file_path))

    ulog = load_ulog_file(file_path)
    px4_ulog = PX4ULog(ulog)
    px4_ulog.add_roll_pitch_yaw()

    #Dict to list all the interesting parameters to extract
    dict_param_to_get ={'vehicle_attitude' : ['timestamp','q[0]','q[1]','q[2]','q[3]','pitch','roll','yaw','yawspeed' ],
                        'vehicle_local_position' : ['timestamp','x','y','z','ax','ay','az' ],   
                        'vehicle_gps_position': ['timestamp','time_utc_usec','lat','lon','alt','alt_ellipsoid','hdop','vdop','fix_type','satellites_used' ],
                        'vehicle_air_data' : ['timestamp','baro_alt_meter','baro_temp_celcius','baro_pressure_pa','rho' ] 
    }

    df_G = pd.DataFrame(columns=['timestamp'])
    # For each cetgory : vehicle_attitude ,vehicle_local_position , etc ..
    for key in dict_param_to_get:
        logger.info("fetching category: " + str(key))

        data_category = ulog.get_dataset(key)

        data={ }

        # For data in cetgory : timestamp ,q[0] , etc ..
        for param in dict_param_to_get[key]: 
            logger.info("\t fetching data: " + str(param))

            data[param] = data_category.data[param]

        # Create DataFrame 
        dfi = pd.DataFrame(data) 
        logger.debug('\n--------\n DF for : ' + str(key))
        logger.debug(dfi)
        
        #Merge Datafrme
        df_G=pd.merge(df_G, dfi, on="timestamp" ,how='outer')
 
    return df_G

