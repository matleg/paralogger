"""
    Animated 3D sinc function
"""

import itertools
import os
import sys


import logging
logger = logging.getLogger("Tab_Graph")

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout,
                             QWidget)
from pyqtgraph.Qt import QtCore, QtGui


import numpy as np #Maybe useless
import pyqtgraph as pg
from pyqtgraph.dockarea import *

def generated_layout(mdf):
    if len(mdf)>2 :

        area = DockArea()

        # Creat the docks
        d1 = Dock("Dock1 - altitude", size=(100, 150), closable=True)  
        d2 = Dock("Dock3 - Pitch",  closable=True)
        d3 = Dock("Dock4 - Roll",  closable=True)
        d4 = Dock("Dock5 - Yaw",  closable=True)
        


        area.addDock(d1, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
        area.addDock(d2, 'right', d1)     ## place d2 at right edge of dock area
        area.addDock(d3, 'above', d2)## place d3 at bottom edge of d1
        area.addDock(d4, 'above', d2)## place d3 at bottom edge of d1



        #mainLayout.addWidget(w4)

        # # Set up each plot 
        color = (0,255,120)

        # %% Altitude  plot
        p1 = pg.PlotWidget(title="Altitude")
        start_altitude =mdf["alt"].iloc[0] 
        altitude = (mdf["alt"].to_numpy() )   -  start_altitude # meters

        p1.plot(mdf['time0_s'].to_numpy() , altitude, pen=color, name="Alt [m]")
        d1.addWidget(p1)

        # Euler angle

        pitch = mdf["pitch"].to_numpy()
        yaw = mdf["yaw"].to_numpy() 
        roll = mdf["roll"].to_numpy()


        p2 = pg.PlotWidget(title="Pitch")
        p2.plot(mdf['time0_s'].to_numpy() , pitch, pen=color, name="pitch [deg]")
        d2.addWidget(p2)

        p3 = pg.PlotWidget(title="Roll")
        p3.plot(mdf['time0_s'].to_numpy() , roll, pen=color, name="roll [deg]")
        d3.addWidget(p3)

        p4 = pg.PlotWidget(title="Yaw")
        p4.plot(mdf['time0_s'].to_numpy() , yaw, pen=color, name="yaw [deg]")
        d4.addWidget(p4)
    else:
        area = QLabel()
        area.setText ("No valid data")




    
    return area

