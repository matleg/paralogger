import os
import sys
import time
import math
import pickle

import pandas as pd
import numpy as np

from model import Flight, timeit
from list_param import Device, Position
from anim_3d import Visualizer3D


import pyqtgraph.opengl as gl

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget

os.environ["DISPLAY"] = ":0"

gravity = 9.80665  # m·s-2
name_saved_file = "mflight_plot.pkl"


with open(name_saved_file, "rb") as f:
    mflight = pickle.load(f)

# Print the input Dataframe.
# print(mflight )

mdf = mflight.get_df_by_position(Position.PILOT)[0]
df_plot = mdf.loc[mdf["lat"].notnull()]



app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("test")
v = Visualizer3D(window)  
window.show()


t_start = 20
t_end = 100

mask = (df_plot["time0_s"] > t_start) & (df_plot["time0_s"] <= t_end)
df_plot_sel = df_plot.loc[mask]

v.animation(df_plot_sel, True)


## Start Qt event loop unless running in interactive mode.

sys.exit(app.exec_())

