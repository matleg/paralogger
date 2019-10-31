import sys
import time
import math
import pickle

import pandas as pd
import numpy as np

from model import Flight, timeit
from list_param import Device, Position
from anim_3d import Visualizer3D

# from single_3d import plot_single

import logging
from logging.handlers import RotatingFileHandler

# from pyqtgraph.Qt import QtCore, QtGui
# import pyqtgraph as pg
import pyqtgraph.opengl as gl

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
import os

os.environ["DISPLAY"] = ":0"

# app = QtGui.QApplication([])
app = QApplication(sys.argv)


window = QWidget()
window.setWindowTitle('test')
# window.setGeometry(100, 100, 280, 80)
# window.move(60, 15)
# helloMsg = QLabel('<h1>Hello World!</h1>', parent=window)
# helloMsg.move(60, 15)



gravity = 9.80665  # m·s-2
name_saved_file = "mflight_plot.pkl"


with open(name_saved_file, "rb") as f:
    mflight = pickle.load(f)

# Print the input Dataframe.
# print(mflight )

#%% Prepare dataframe
mdf = mflight.get_df_by_position(Position.PILOT)[0]
df_plot = mdf.loc[mdf["lat"].notnull()]

print(
    "Time0_s range: "
    + str(df_plot["time0_s"].min())
    + " : "
    + str(df_plot["time0_s"].max())
)

#%% PLot still
def plot_single(x, y, z, pitch, roll, yaw):
    print("in plot_single ")

    w = gl.GLViewWidget(parent=window)
    w.show()
    w.setWindowTitle("pyqtgraph example: GLMeshItem")
    w.setCameraPosition(distance=40)

    g = gl.GLGridItem()
    g.scale(2, 2, 1)
    w.addItem(g)
    # Example 4:
    # Cylinder

    md = gl.MeshData.cylinder(rows=10, cols=20, radius=[2.0, 2.0], length=5.0)
    m1 = gl.GLMeshItem(
        meshdata=md,
        smooth=False,
        drawFaces=False,
        drawEdges=True,
        edgeColor=(1, 1, 1, 1),
    )
    m1.translate(x, y, z)

    m1.rotate(pitch, 0, 1, 0)
    m1.rotate(roll, 1, 0, 0)
    m1.rotate(yaw, 0, 0, 1)
    w.addItem(m1)


def plot_single_row(num):
    single = df_plot.iloc[num, :]
    x = single.x
    y = single.y
    z = single.z
    p = np.rad2deg(single.pitch)
    r = np.rad2deg(single.roll)
    y = np.rad2deg(single.yaw)

    plot_single(x, y, z, p, r, y)


# plot_single_row(542)

#%% PLot3D

v = Visualizer3D()
t_start = 20
t_end = 100

mask = (df_plot["time0_s"] > t_start) & (df_plot["time0_s"] <= t_end)
df_plot_sel = df_plot.loc[mask]

#%%
v.animation(df_plot_sel, True)

#%% End

print("END")

#%% MAIN
## Start Qt event loop unless running in interactive mode.
sys.exit(app.exec_())    

    


#%%
