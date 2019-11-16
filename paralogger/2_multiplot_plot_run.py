
#%% Import
import math
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.opengl as gl

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout,QVBoxLayout, QLabel

from anim_3d_multi import Visualizer3D
from list_param import Device, Position
from model import Flight, timeit

os.environ["DISPLAY"] = ":0" #Use for linux  on vscode at least

name_saved_file = "mflight_plot_V1.pkl"


#%% Prepare data

with open(name_saved_file, "rb") as f:
    mflight = pickle.load(f)

#get the time bound of the general section
t_start,t_end = mflight.sections[0].get_start_end()
t_start=110
t_end = 173
#Extract th dataframe at thepilot position
mdf = mflight.get_df_by_position(Position.PILOT)[0]

df_plot = mdf.loc[mdf["lat"].notnull()]

#Clibrate it
if 1 : 
    dict_calibration = mflight.sections[0].set_calibration(mdf,t_start , t_start+5)
    print(dict_calibration)
    df_plot['pitch'] = df_plot['pitch'] - dict_calibration['pitch']
    df_plot['roll'] = df_plot['roll'] - dict_calibration['roll']
#df_plot['yaw'] = df_plot['yaw'] - avg_yaw + start_yaw_angle



#Extract a sub selection of the dataframe based on bound time
mask = (df_plot["time0_s"] > t_start) & (df_plot["time0_s"] <= t_end)
df_plot_sel = df_plot.loc[mask]


#%% 3D plot
app = QApplication(sys.argv)


#Here I use a useless layout , but maybe I need it one day  !
window = QMainWindow()
Main_Widget = QWidget()
window.setWindowTitle("Animation 3D")
window.setGeometry(0, 0, 1400, 1000)

layout = QVBoxLayout()
D3_holder = QWidget()
layout.addWidget(D3_holder)

# text_test = QLabel('Test1')

# layout.addWidget(text_test)


v = Visualizer3D(Main_Widget)  

#Main_Widget.setLayout(layout)

window.setCentralWidget(Main_Widget)

window.show() # IMPORTANT!!!!! Windows are hidden by default.

v.animation(df_plot_sel, True)

# Start the event loop.
app.exec_()



# %%
