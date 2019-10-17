#! /usr/bin/env python
"""
Created plot for visualising ulog

Fred
12/10/2019
"""

#%% import

import sys
import time
import math
import pickle

import pandas as pd 
import numpy as np

from model.model import Flight
from model.list_param import Device , Position
from model.anim_3d import Visualizer3D

#from single_3d import plot_single

import logging
from logging.handlers import RotatingFileHandler

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

import os
os.environ['DISPLAY']=':0'


#%% Config logger
logger = logging.getLogger()
#logging.basicConfig(filename='1_import.log',level=logging.DEBUG)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s ::  %(message)s')
file_handler = RotatingFileHandler('plot_run.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Redirect log on console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


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

def timer(start,end):
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return ("{:0>2} h {:0>2} min {:05.2f} s".format(int(hours),int(minutes),seconds))

app = QtGui.QApplication([])



#%% PARAMETERS 
gravity = 9.80665 #m·s-2
name_saved_file= 'mflight_plot.pkl'


#%%  Prepare file 
logger.info(" --- Start ----")


#Load file from pickle
logger.info("Reading : " + name_saved_file)
with open(name_saved_file , 'rb') as f:
    mflight = pickle.load(f)

# Print the input Dataframe. 
print(mflight )

#%% Prepare dataframe
mdf = mflight.get_df_by_position(Position.PILOT)[0]
df_plot = mdf.loc[mdf['x'].notnull()]

#%% PLot still
def plot_single(x,y,z,pitch,roll, yaw):
    print('in plot_single ')
       
    w = gl.GLViewWidget()
    w.show()
    w.setWindowTitle('pyqtgraph example: GLMeshItem')
    w.setCameraPosition(distance=40)

    g = gl.GLGridItem()
    g.scale(2,2,1)
    w.addItem(g)
    # Example 4:
    # Cylinder

    md = gl.MeshData.cylinder(rows=10, cols=20, radius=[2.0, 2.0], length=5.)
    m1 = gl.GLMeshItem(meshdata=md, smooth=False, drawFaces=False, drawEdges=True, edgeColor=(1,1,1,1))
    m1.translate(x,y,z)

    m1.rotate(pitch,0,1,0)
    m1.rotate(roll,1,0,0)
    m1.rotate(yaw,0,0,1)
    w.addItem(m1)

def plot_single_row(num):
    single = df_plot.iloc[ num , : ]
    x = single.x
    y = single.y
    z = single.z
    p = np.rad2deg(single.pitch )
    r = np.rad2deg(single.roll )
    y = np.rad2deg(single.yaw )

    plot_single(x, y, z, p, r, y)

#plot_single_row(542)

#%% PLot3D

v = Visualizer3D()
t_start=50
t_end=110

mask = (df_plot['time0_s'] > t_start) & (df_plot['time0_s'] <= t_end)
df_plot_sel = df_plot.loc[mask]

v.animation(df_plot_sel,True)

#%% End
logger.info(" --- END ----")

print("END")

#%% MAIN
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


#%%
