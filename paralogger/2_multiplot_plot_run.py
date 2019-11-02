
#%% Import
import math
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd
import pyqtgraph.opengl as gl

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout,QVBoxLayout, QLabel

from anim_3d_multi import Visualizer3D
from list_param import Device, Position
from model import Flight, timeit

os.environ["DISPLAY"] = ":0"

gravity = 9.80665  # m·s-2
name_saved_file = "mflight_plot.pkl"


#%% Prepare data

with open(name_saved_file, "rb") as f:
    mflight = pickle.load(f)

mdf = mflight.get_df_by_position(Position.PILOT)[0]
df_plot = mdf.loc[mdf["lat"].notnull()]

t_start = 0
t_end = 150

mask = (df_plot["time0_s"] > t_start) & (df_plot["time0_s"] <= t_end)
df_plot_sel = df_plot.loc[mask]




#%% Prepare ploting 
#QtGui.QApplication.setGraphicsSystem('raster')
# app = QtGui.QApplication([])
# #mw = QtGui.QMainWindow()
# #mw.resize(800,800)

# win = pg.GraphicsWindow(title="Basic plotting examples")
# win.resize(1000,600)
# win.setWindowTitle('pyqtgraph example: Plotting')

# # Enable antialiasing for prettier plots
# pg.setConfigOptions(antialias=True)

# # Set up each plot 
# color = (0,255,120)
# # %% Altitude  plot
# altitude = df_plot_sel["alt"].to_numpy() / 1e3  # meters

# p1 = win.addPlot(title="Alt")
# p1.plot(df_plot_sel['time0_s'].to_numpy() , altitude, pen=color, name="Alt [m]")
# p1.plot(df_plot_sel['time0_s'].to_numpy() , df_plot_sel['baro_alt_meter'].to_numpy(), pen=(0,255,0), name="baro_alt_meter")

# # %% Pitch  plot
# pitch = df_plot_sel["pitch"].to_numpy() * -1
# yaw = df_plot_sel["yaw"].to_numpy() * -1
# roll = df_plot_sel["roll"].to_numpy()

# pitch= np.rad2deg(pitch)
# yaw= np.rad2deg(yaw)
# roll= np.rad2deg(roll)

# p2 = win.addPlot(title="Pitch")
# p2.plot(df_plot_sel['time0_s'].to_numpy() , pitch, pen=color, name="pitch [deg]")

# p3 = win.addPlot(title="roll")
# p3.plot(df_plot_sel['time0_s'].to_numpy() , roll, pen=color, name="roll [deg]")

# p4 = win.addPlot(title="yaw")
# p4.plot(df_plot_sel['time0_s'].to_numpy() , yaw, pen=color, name="yaw [deg]")


# win.nextRow()

# p6 = win.addPlot(title="Updating plot")
# curve = p6.plot(pen='y')
# data = np.random.normal(size=(10,1000))
# ptr = 0
# def update():
#     global curve, data, ptr, p6
#     curve.setData(data[ptr%10])
#     if ptr == 0:
#         p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
#     ptr += 1
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(50)


#%% 3D anim 
# window = QWidget()
# window.setWindowTitle("test")
# p5 = Visualizer3D()
# p5.animation(df_plot_sel, True)


app = QApplication(sys.argv)



window = QMainWindow()
Main_Widget = QWidget()
window.setWindowTitle("test")
window.setGeometry(0, 0, 1100, 800)

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
