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
from bokeh.layouts import gridplot

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
Reload_file = False

name_df_input= 'df_ulog.pkl'


### MAIN ###
print("---START---")


if Reload_file:
    print("Reading Ulog file ... ")

    ulog = load_ulog_file(ulog_file_name)
    px4_ulog = PX4ULog(ulog)
    px4_ulog.add_roll_pitch_yaw()

    vehicle_attitude = ulog.get_dataset('vehicle_attitude')
    timestamp = vehicle_attitude.data['timestamp']  # in microsecond
    timestamp_us_0 = [(timestamp[i] - timestamp[0]) for i in range(len(timestamp))]

    pitch = vehicle_attitude.data['pitch']
    roll = vehicle_attitude.data['roll']
    yaw = vehicle_attitude.data['yaw']


    print("Creating Dataframe")

    # intialise data of lists. 
    data = {'timestamp':timestamp, 'timestamp_us_0':timestamp_us_0,'pitch':pitch, 'roll':roll, 'yaw':yaw} 
    
    # Create DataFrame 
    df = pd.DataFrame(data) 
    df['delay_log']=df['timestamp'].diff()  # Calculate the delay  between two records in micro second , around 4000 ms = 0.0004 so 250 hz 
    df['timestamp_s_0'] = df['timestamp_us_0']/1000000
    print("Writing : df_ulog.pkl ")
    df.to_pickle("df_ulog.pkl")
else:
    print("Loading : df_ulog.pkl ")
    df = pd.read_pickle("df_ulog.pkl")

# Print the input Dataframe. 
print(df )


## PLOT WITH MATPLOTLIB
if 0:
    print("Plotting mathplotlib... ")
    #Plot Pitch and roll
    df.plot(x='timestamp_s_0', y='pitch', marker='.',title="Pitch[rad] /time0")
    df.plot(x='timestamp_s_0', y='roll', marker='.',title="Roll[rad] /time0")
    #plt.show()

    #Plot Histogram delay_log.
    df.hist(column='delay_log',bins=200, range=(3900, 4100))
    plt.show()

## PLOT WITH BOKEH # TODO  manage large number of points with downsampling
if 0:
    print("Plotting bokeh... ")
    source = ColumnDataSource(df)

    # create a new plot and add a renderer
    left = figure( title="Pitch[rad]/time0")
    left.circle(x='timestamp_s_0', y='pitch', source=source)

    # create another new plot and add a renderer
    right = figure(  title='Roll[rad]/time0')
    right.circle(x='timestamp_s_0', y='roll', source=source)

    p = gridplot([[left, right]])

    show(p)


### ANIMATION
# To make the naimation we resample de data  at 25hz (40ms)  with a linear interpolation, 
# in order to have a fix frame rate for the animation.
df_anim=df.copy()
length = -1

df_anim['x'] = length * np.sin(df_anim.pitch) 
df_anim['y'] = length * np.cos(df_anim.pitch) 


df_anim['Datetime'] = pd.to_datetime(df_anim['timestamp_us_0']*1000)
df_anim = df_anim.set_index('Datetime')

print(df_anim[10000:10010])
df_anim_r = df_anim.resample('40ms').interpolate(method='linear')

print("resampling")
print(df_anim_r[10000:10010])

# Animation

import matplotlib.pyplot as plt
import matplotlib.animation as anim

xmin=-1
ymin= -0.5
xmax=1
ymax=-1.5

start = 4500
end = start + 150

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=(-0.25, 0.25), ylim=(-1.5, 0.5))
line, = ax.plot([], [], 'o-', lw=2)
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

x = df_anim_r['x'][start:end]

y = df_anim_r['y'][start:end]
t = df_anim_r['timestamp_us_0'][start:end]
t = [(t[i] - t[0]) for i in range(len(t))] 

# print('t: ', t)
# print('x: ', x)
# print('y: ', y)

def init():

    line.set_data([], [])
    time_text.set_text('')

#animation function
def animate(i): 
    #prevent autoscaling of figure
    # plt.xlim(xmin, xmax)
    # plt.ylim(ymin,ymax)
    time_text.set_text('time = %.4fs' % (int(i)*40/1000))
    xlist = [0, x[i]]
    ylist = [0, y[i]]

    line.set_data(xlist, ylist)
    #line.set_data(x[i], y[i])
    #set new point
    # print("plot i:" + str(i)+" x:" + str(x[i])+ "  y:" + str(y[i]))
    # plt.scatter(x[i], y[i], c = "b")

#animate scatter plot
ani = anim.FuncAnimation(fig, animate, init_func = init, 
                          interval = 40, repeat = True)
plt.show()
