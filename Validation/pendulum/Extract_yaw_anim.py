#! /usr/bin/env python
"""
Extract parameters from an ULog file
And Created an animation for th yaw angle .

Use  to validate the calibration , by overlaying  with a video

Fred
29/09/2019
"""

#%% import

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

ulog_file_name = 'sample_log/log_23_2019-9-29-15-15-10.ulg'
Reload_file = True

name_df_input= 'df_ulog_yaw.pkl'


#%%  MAIN 
print("---START---")


if Reload_file:
    print("Reading Ulog file : " + str(ulog_file_name))

    ulog = load_ulog_file(ulog_file_name)
    px4_ulog = PX4ULog(ulog)
    px4_ulog.add_roll_pitch_yaw()

    vehicle_attitude = ulog.get_dataset('vehicle_attitude')
    timestamp = vehicle_attitude.data['timestamp']  # in microsecond
    timestamp_us_0 = [(timestamp[i] - timestamp[0]) for i in range(len(timestamp))]

    pitch = vehicle_attitude.data['pitch']
    roll = vehicle_attitude.data['roll']
    yaw = vehicle_attitude.data['yaw']

    #Info Log
    print("\nInfo_log: ")
    sd_log = ulog.initial_parameters["SDLOG_PROFILE"]
    print("SDLOG_Profile: ",sd_log)

    print("\nCreating Dataframe")

    # intialise data of lists. 
    data = {'timestamp':timestamp, 'timestamp_us_0':timestamp_us_0,'pitch':pitch, 'roll':roll, 'yaw':yaw } 
    
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



#%%  Calibrate 
# For each Making an avergae on a prediod of time 
# and substatre this vaule to all values.

start_cal_s = 5
end_cal_s = 10

start_yaw_angle_deg = -10.8  #degrees
start_yaw_angle = math.radians(start_yaw_angle_deg)  #convert to Rad

mask = (df['timestamp_s_0'] > start_cal_s) & (df['timestamp_s_0'] <= end_cal_s)

avg_pitch = df.loc[mask, 'pitch'].mean()
avg_roll = df.loc[mask, 'roll'].mean()
avg_yaw = df.loc[mask, 'yaw'].mean()

print( "calibrating  from: " + str(start_cal_s) + "s to : " + str(end_cal_s) + " s" )
print( 'avg_pitch :' + str(avg_pitch) + " rad so:" + str(np.rad2deg(avg_pitch)) + " deg")
print( 'avg_roll :' + str(avg_roll) + " rad so:" + str(np.rad2deg(avg_roll)) + " deg")
print( 'avg_yaw :' + str(avg_yaw) + " rad so:" + str(np.rad2deg(avg_yaw)) + " deg" + " wanted (deg): "+ str(start_yaw_angle_deg))

df['pitch0'] = df['pitch'] - avg_pitch
df['roll0'] = df['roll'] - avg_roll
df['yaw0'] = df['yaw'] - avg_yaw + start_yaw_angle
#df['yawdeg'] = np.rad2deg(df['yaw']) 



#%% PLOT Input curve
## PLOT HIST
if 0:
    #Plot Histogram delay_log.
    df.hist(column='delay_log',bins=200, range=(3900, 4100))
    plt.show()

## PLOT WITH MATPLOTLIB PITCH ROLL
if 0:
    print("Plotting mathplotlib pitch roll ")
    #Plot Pitch and roll
    # df.plot(x='timestamp_s_0', y='pitch', marker='.',title="Pitch[rad] /time0")
    # df.plot(x='timestamp_s_0', y='roll', marker='.',title="Roll[rad] /time0")
    # #plt.show()

    plt.xlabel('Time 0')

    ax1 = df.pitch.plot(color='blue', grid=True, label='Pitch')
    ax2 = df.roll.plot(color='red', grid=True, secondary_y=False, label='Roll')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    plt.legend(h1+h2)
    plt.show()


## PLOT WITH MATPLOTLIB YAW
if 0:
    print("Plotting mathplotlib yaw ")

    plt.xlabel('Time 0')

    ax1 = df.yaw.plot(color='blue', grid=True, label='yaw')
    ax2 = df.yaw0.plot(color='red', grid=True, secondary_y=False, label='yaw0')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    plt.legend(h1+h2)
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


#%%  ANIMATION
# To make the naimation we resample de data  at 25hz (40ms)  with a linear interpolation, 
# in order to have a fix frame rate for the animation.

#Animation Parameters:
length_bar = -1
transparent_video = True
hide_axes = True
name_output_mp4 = "anim_out_yaw.mp4"
nb_frame_s = 125  # if -1 no resample



df_anim=df.copy()

df_anim['x'] = length_bar * np.sin(df_anim['yaw0']) 
df_anim['y'] = length_bar * np.cos(df_anim['yaw0']) 


df_anim['Datetime'] = pd.to_datetime(df_anim['timestamp_us_0']*1000)
df_anim = df_anim.set_index('Datetime')


print(df_anim.head())


print("check for resampling parameters: ")
if nb_frame_s >0:
    print("resampling ... ")
    time_between_frame_ms = 1/nb_frame_s*1000
    nb_frame_s_final = nb_frame_s
    time_gap = str(time_between_frame_ms) + 'ms'
    #df_anim_r = df_anim.resample(time_gap).interpolate(method='linear')
    df_anim_r = df_anim.resample(time_gap).last()
else:
    print("not resampling ... ")
    df_anim_r = df_anim.copy()
    time_between_frame_ms = df_anim_r['delay_log'].mean()/1000
    nb_frame_s_final = 1 / time_between_frame_ms *1000



print(df_anim_r.head())

#%% PLOT RAW AND RESAMPLE WITH MATPLOTLIB
if 1:

    plt.xlabel('Time 0')

    ax1 = df_anim.yaw0.plot(color='blue', grid=True, label='yaw0',style='-*')
    ax2 = df_anim_r.yaw0.plot(color='red', grid=True, secondary_y=False, label='yaw0 _ resample',style='-*')

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    plt.legend(h1+h2)
    plt.show()

#%% Animation
print("\n Starting animation... \n")

if 1:

    import matplotlib.pyplot as plt
    import matplotlib.animation as anim

    nb_frame_tot = len(df_anim_r.index)

    #summary parameters:
    print('nb_frame_s: '+ str(nb_frame_s)+ ' \t Time_between_frame_ms: ' + str(time_between_frame_ms))
    print('nb_frame_s_final: ' +str(nb_frame_s_final))
    print('nb_frame_tot: '+ str(nb_frame_tot)+ ' \t Total time (s): ' + str(nb_frame_tot/nb_frame_s_final))
    print("transparent_video : " + str(transparent_video))
    print("hide_axes : " + str(hide_axes))

    # Here you Can specify a start row and a end row , to debug:
    start = 5000
    end = None

    #Creating the figure
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                        xlim=(-1.2, 1.2), ylim=(-1.2, 1.2))
    line, = ax.plot([], [], 'o-', lw=2)
    time_text = ax.text(0.02, 0.05, '', transform=ax.transAxes ,color='green')

    x = df_anim_r['x'][start:end]

    y = df_anim_r['y'][start:end]
    t = df_anim_r['timestamp_us_0'][start:end]
    t = [(t[i] - t[0]) for i in range(len(t))] 

    if hide_axes :
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.set_frame_on(False)

    if transparent_video :
        fig.patch.set_alpha(0.)
        mCodec= "png"
        mKarg_writter= {'transparent': True, 'facecolor': 'none'}
    else:
        mCodec= None
        mKarg_writter = None

    def init():

        line.set_data([], [])
        time_text.set_text('')

    #animation function:
    def animate(i): 

        time_text.set_text('time = %.3fs' % (int(i)*time_between_frame_ms/1000))
        xlist = [0, x[i]]
        ylist = [0, y[i]]

        line.set_data(xlist, ylist)
        #line.set_data(x[i], y[i])
        #set new point
        # print("plot i:" + str(i)+" x:" + str(x[i])+ "  y:" + str(y[i]))
        # plt.scatter(x[i], y[i], c = "b")

    # Create animation:

    ani = anim.FuncAnimation(fig, animate, init_func = init, frames = nb_frame_tot,
                            interval = time_between_frame_ms, repeat = False)


    # Display animation
    if 0 :   
        print("\n displaying animation ...")                       
        plt.show()

    # save animation to file:
    if 1:
        print("\n saving animation to file : " + str(name_output_mp4)) 
        # Set up formatting for the movie files
        Writer = anim.writers['ffmpeg']
        writer = Writer(fps = nb_frame_s_final, metadata = dict(title='Validation Video'), extra_args=['-loglevel', 'verbose'], bitrate = 1800 , codec = mCodec)


        ani.save(name_output_mp4, writer = writer ,savefig_kwargs = mKarg_writter)
print("End with Ulog file : " + str(ulog_file_name))
print("------ END ------") 



################################
## RESSOURCES:

#PX4 preview:
# YAW slow run4 29/09/2019: https://review.px4.io/plot_app?log=b469450c-b9a0-41b6-a2f5-0f8ef7ec8ca2



#Animation:
# http://adrian.pw/blog/matplotlib-transparent-animation/
# https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.animation.FuncAnimation.html


#%%
