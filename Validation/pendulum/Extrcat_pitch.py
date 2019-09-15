#! /usr/bin/env python
"""
Extract parameters from an ULog file
"""

from __future__ import print_function

import argparse
import sys
import time
import math
from pyulog import ULog
from pyulog.px4 import PX4ULog

import pandas as pd 
import numpy as np

import matplotlib.pyplot as plt
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource

from functools import lru_cache
#pylint: disable=unused-variable, too-many-branches


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

### PARAMETERS ###

ulog_file_name = 'log_0_2019-9-14-21-54-24.ulg'


### MAIN ###
print("---START---")
print("Reading Ulog file ... ")

ulog = load_ulog_file(ulog_file_name)
px4_ulog = PX4ULog(ulog)
px4_ulog.add_roll_pitch_yaw()

vehicle_attitude = ulog.get_dataset('vehicle_attitude')
timestamp = vehicle_attitude.data['timestamp']
timestamp_0 = [(timestamp[i] - timestamp[0])/1000000 for i in range(len(timestamp))] # Divide  by 10E6  micro second to second
pitch = vehicle_attitude.data['pitch']
roll = vehicle_attitude.data['roll']
yaw = vehicle_attitude.data['yaw']


print("Creating Dataframe")

# intialise data of lists. 
data = {'timestamp':timestamp, 'timestamp_0':timestamp_0,'pitch':pitch, 'roll':roll, 'yaw':yaw} 
  
# Create DataFrame 
df = pd.DataFrame(data) 
  
# Print the output. 
print(df )


print("Creating df animation ... ")

#Plot Pitch
#df.plot(x='timestamp_0', y='pitch', marker='.')
#plt.show()

# ## PLOT WITH BOKEH

# source = ColumnDataSource(df)
# p = figure()
# p.circle(x='timestamp_0', y='pitch', source=source)

# show(p)

###  ANIMATION ###
length= 1

df_anim=df.copy()


df_anim['x'] = length * np.sin(df_anim.pitch) 
df_anim['y'] = length * np.cos(df_anim.pitch) 

print(df_anim)

print("Ploting ... ")
import matplotlib.pyplot as plt
import matplotlib.animation as anim


fig = plt.figure()
x = df_anim['x']
y = df_anim['y']
t = df_anim['timestamp']


# x=[20,23,25,27,29,31]
# y=[10,12,14,16,17,19]
# t=[2,9,1,4,3,9]

#create index list for frames, i.e. how many cycles each frame will be displayed
frame_t = []
for i, item in enumerate(t):
    frame_t.extend([i] * item)

def init():
    fig.clear()

#animation function
def animate(i): 
    #prevent autoscaling of figure
    plt.xlim(15, 35)
    plt.ylim( 5, 25)
    #set new point
    plt.scatter(x[i], y[i], c = "b")

#animate scatter plot
ani = anim.FuncAnimation(fig, animate, init_func = init, 
                         frames = frame_t, interval = 100, repeat = True)
plt.show()

############################################





# import numpy as np

# import matplotlib.animation as animation



# length= 1

# xmin = -2
# xmax = 2
# nbx = 100


# fig, ax = plt.subplots()
# point, = ax.plot([], [], ls="none", marker="o")
# # plt.xlim(xmin, xmax)
# # plt.ylim(-1,1)

# # fonction à définir quand blit=True
# # crée l'arrière de l'animation qui sera présent sur chaque image

# def animate(i): 

#     a_pitch = df.iloc[ i , : ].pitch
#     t = df.iloc[ i , : ].timestamp_0
#     x= length * math.sin(a_pitch)
#     y= length * math.cos(a_pitch)
#     print("i:" +str(i) +  "\t t:"+ str(t))
#     print("x:",x)
#     print("y:",y)
#     point.set_data(x, y)
#     return  point
    
 
# ani = animation.FuncAnimation(fig, animate,  frames=100, blit=True, interval=20, repeat=False)

# plt.show()



print("---END---")










# ##########""
# import numpy as np

# import matplotlib.animation as animation
# length= 1

# fig = plt.figure(figsize=(5, 5), facecolor='w')
# ax = fig.add_subplot(1, 1, 1)
# plt.rcParams['font.size'] = 15

# lns = []

# for index, row in df.iterrows():

#     ln, = ax.plot([0, 0], [length * math.sin(row['pitch']), length* math.cos(row['pitch'])],
#                   color='k', lw=2)
#     tm = ax.text(-1, 0.9, 'time = %.1fs' % t[i])
#     lns.append([ln, tm])
# ax.set_aspect('equal', 'datalim')
# ax.grid()
# ani = animation.ArtistAnimation(fig, lns, interval=50)