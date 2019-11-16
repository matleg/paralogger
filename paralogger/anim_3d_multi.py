"""
    Animated 3D sinc function
"""

import itertools
import os
import sys


import logging
logger = logging.getLogger("anime_3d_multi")

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout,
                             QWidget)
from pyqtgraph.Qt import QtCore, QtGui

from geometry_modeling import Create_geom

# import pkg_resources


os.environ["DISPLAY"] = ":0"

# resource_package = __name__

# def get_source_name(file_path_name):
#     return pkg_resources.resource_filename(resource_package,file_path_name)


# m1 = gl.GLMeshItem(meshdata=md, smooth=False, drawFaces=False, drawEdges=True, edgeColor=(1,1,0,1))


def WGS84_to_mercator(lon, lat):
    """ Convert lon, lat in [deg] to Mercator projection 
    from https://review.px4.io/
    """
    # alternative that relies on the pyproj library:
    # import pyproj # GPS coordinate transformations
    #    wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    #    mercator = pyproj.Proj('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 ' +
    #       '+lon_0=0.0 +x_0=0.0 +y_0=0 +units=m +k=1.0 +nadgrids=@null +no_defs')
    #    return pyproj.transform(wgs84, mercator, lon, lat)

    semimajor_axis = 6378137.0  # WGS84 spheriod semimajor axis
    east = lon * 0.017453292519943295
    north = lat * 0.017453292519943295
    northing = 3189068.5 * np.log((1.0 + np.sin(north)) / (1.0 - np.sin(north)))
    easting = semimajor_axis * east

    return easting, northing


def map_projection(lat, lon, anchor_lat, anchor_lon):
    """ convert lat, lon in [rad] to x, y in [m] with an anchor position """
    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    cos_d_lon = np.cos(lon - anchor_lon)
    sin_anchor_lat = np.sin(anchor_lat)
    cos_anchor_lat = np.cos(anchor_lat)

    arg = sin_anchor_lat * sin_lat + cos_anchor_lat * cos_lat * cos_d_lon
    arg[arg > 1] = 1
    arg[arg < -1] = -1

    np.set_printoptions(threshold=sys.maxsize)
    c = np.arccos(arg)
    k = np.copy(lat)
    for i in range(len(lat)):
        if np.abs(c[i]) < np.finfo(float).eps:
            k[i] = 1
        else:
            k[i] = c[i] / np.sin(c[i])

    CONSTANTS_RADIUS_OF_EARTH = 6371000
    x = (
        k
        * (cos_anchor_lat * sin_lat - sin_anchor_lat * cos_lat * cos_d_lon)
        * CONSTANTS_RADIUS_OF_EARTH
    )
    y = k * cos_lat * np.sin(lon - anchor_lon) * CONSTANTS_RADIUS_OF_EARTH

    return x, y

def prepare_data (mdf) :
    mdf[["pitch", "yaw", "roll"]] = mdf[["pitch", "yaw", "roll"]].apply(np.rad2deg)

    # Work on Gps coordinate
    lon = mdf["lon"].to_numpy() / 1e7  # degrees
    lat = mdf["lat"].to_numpy() / 1e7
    altitude = mdf["alt"].to_numpy()   # meters

    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)

    anchor_lat = 0
    anchor_lon = 0
    lat, lon = map_projection(lat, lon, anchor_lat, anchor_lon)
    lat = lat - lat[0]
    lon = lon - lon[0]
    altitude0 = altitude - altitude[0]

    mdf["lat_m"] = lat 
    mdf["lon_m"] = lon 
    mdf["alt_m"] = altitude0 

    # Reorient data (#TODO  to explore more)
    mdf["lat_m"] = mdf["lat_m"]  * 1  #x
    mdf["lon_m"] = mdf["lon_m"]  * -1 #y
    mdf["alt_m"] = mdf["alt_m"]  * 1  #z
    mdf["pitch"] = mdf["pitch"]  * 1
    mdf["roll"]  = mdf["roll"]   * 1
    mdf["yaw"]   = mdf["yaw"]    * -1

    return mdf


def add_plot(mdf , widget):
    # # Set up each plot 
    color = (0,255,120)

    # %% Altitude  plot
    start_altitude =mdf["alt"].iloc[0] 
    altitude = (mdf["alt"].to_numpy() )   -  start_altitude # meters

    p1 = widget.addPlot(title="Alt")

    p1.plot(mdf['time0_s'].to_numpy() , altitude, pen=color, name="Alt [m]")

    # Set up an animated arrow 

    arrow_alt = pg.ArrowItem(angle=90)
    p1.addItem(arrow_alt)

    # %% Pitch  plot
    pitch = mdf["pitch"].to_numpy()
    yaw = mdf["yaw"].to_numpy() 
    roll = mdf["roll"].to_numpy()

    # pitch= np.rad2deg(pitch)
    # yaw= np.rad2deg(yaw)
    # roll= np.rad2deg(roll)

    p2 = widget.addPlot(title="Pitch")
    p2.plot(mdf['time0_s'].to_numpy() , pitch, pen=color, name="pitch [deg]")
    arrow_pitch = pg.ArrowItem(angle=90)
    p2.addItem(arrow_pitch)

    p3 = widget.addPlot(title="roll")
    p3.plot(mdf['time0_s'].to_numpy() , roll, pen=color, name="roll [deg]")
    arrow_roll = pg.ArrowItem(angle=90)
    p3.addItem(arrow_roll)

    p4 = widget.addPlot(title="yaw")
    p4.plot(mdf['time0_s'].to_numpy() , yaw, pen=color, name="yaw [deg]")
    arrow_yaw = pg.ArrowItem(angle=90)
    p4.addItem(arrow_yaw)

    return {"arrow_alt":arrow_alt , "arrow_pitch" :arrow_pitch , "arrow_roll":arrow_roll , "arrow_yaw":arrow_yaw}



class Visualizer3D(object):
    def __init__(self,parent):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)

        #Main Widget containing everything
        self.mainWidget= QWidget(parent= parent)
        self.mainWidget.setGeometry(0, 0, 1400,1000)
        # general layout
        self.layout_general = QVBoxLayout(self.mainWidget)

        
        #Top Layout
        self.layout_top = QHBoxLayout( )
        self.layout_general.addLayout(self.layout_top,70)

        #Top Layout
        self.layout_bottom = QHBoxLayout()
        self.layout_general.addLayout(self.layout_bottom,30)
        
        # Live Data text area
        self.data_info_text = QLabel('Live Data info')
        self.layout_top.addWidget(self.data_info_text,15)   # 20% of the width

        #Anim 3D
        self.D3_holder = QWidget(parent=self.mainWidget )
        self.w = gl.GLViewWidget(parent= self.D3_holder)
        self.layout_top.addWidget( self.w ,85)   # 80% of the width

        # Plot
        self.plots =  pg.GraphicsWindow(title="Basic plotting examples")
        pg.setConfigOptions(antialias=True)
        self.layout_bottom.addWidget( self.plots ,20)   # 80% of the width
       

        #self.mainWidget.setLayout(self.layout)
        

        #self.w = gl.GLViewWidget()
        self.w.opts["distance"] = 160
        self.w.setWindowTitle("3D view track")
        #self.w.setGeometry(0, 110, 720, 480)

        
        self.df = None
        self.track = None
        self.track_is_ploted = False
        self.index = 0
        self.step_interval =None

        # Created the geometrie
        models_path = os.path.dirname(os.path.abspath(__file__))
        obj = "simple_body.obj"
        obj_path = os.path.join(models_path,"gui","3D_model", obj)
        self.geom = Create_geom.obj(obj_path)

        # create the background grids
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-9, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

        xsize = QtGui.QVector3D(7, 7, 7)

        ax = gl.GLAxisItem(size=xsize, antialias=True, glOptions="translucent")
        self.w.addItem(ax)

        self.w.addItem(self.geom)

    def extract_path_track(self):
        logger.info("add_path_track ")
        self.track = self.df[["lat_m", "lon_m", "alt_m"]].to_numpy()

    def calculate_average_time(self):
        duration = self.df.iloc[-1]["time0_s"] - self.df.iloc[0]["time0_s"]
        nb_record = len(self.df)
        average_step_time = duration / nb_record

        logger.info('duration: ' + str(duration) + " for nb record: " + str(nb_record))
        logger.info("average_step_time", average_step_time)

        self.step_interval = average_step_time


    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
            sys.exit(QtGui.QApplication.instance().exec_())

    def update(self):

        self.index = (self.index + 1) % len(self.df)

        i = self.index
        if i == 0:
            print("... loop animation ...")


        time00 = self.df["time0_s"].iloc[0]

        time0_s = self.df["time0_s"].iloc[i]

        time_simu= i* self.step_interval
        diff_time = time_simu - time0_s + time00

        pitch = self.df["pitch"].iloc[i]
        roll = self.df["roll"].iloc[i]
        yaw = self.df["yaw"].iloc[i]
        lat = self.df["lat_m"].iloc[i]
        lon = self.df["lon_m"].iloc[i]
        alt = self.df["alt_m"].iloc[i]


        #Update Text data
        self.data_info_text.setText(f'i: \t {i} \n'+
                                    f'time simu: \t {time_simu:.2f} \n'+
                                    f'time0_s: \t {time0_s:.2f} \n' +
                                    f'time diff: \t {diff_time:.2f} \n\n'+

                                    f'pitch: \t {pitch:.1f} \n' +
                                    f'roll: \t {roll:.1f} \n' +
                                    f'yaw: \t {yaw:.1f} \n\n' +
                                    f'x: \t {lat:.1f} \n' +
                                    f'y: \t {lon:.1f} \n' +
                                    f'z: \t {alt:.1f} \n\n'

                                    )

        #Update arrow:
        self.custom['arrow_alt'].setPos(time0_s , alt)
        self.custom['arrow_pitch'].setPos(time0_s , pitch)
        self.custom['arrow_roll'].setPos(time0_s , roll)
        self.custom['arrow_yaw'].setPos(time0_s , yaw)

        #Update 3D body
        self.geom.resetTransform()
        # Important  to rotate before translated
        self.geom.rotate(pitch, 0, 1, 0)
        self.geom.rotate(roll, 1, 0, 0)
        self.geom.rotate(yaw, 0, 0, 1)

        self.geom.translate(lat, lon, alt)

        self.geom.update()


        # Add track if exist:
        if self.track is not None and not self.track_is_ploted:
            print("ploting track")
            plt = gl.GLLinePlotItem(pos=self.track, antialias=True)
            self.w.addItem(plt)
            self.track_is_ploted = True

    def animation(self, mdata, plot_track):

        print("total records:" + str(len(mdata)))

        self.df = prepare_data(mdata)

        if plot_track:
            self.extract_path_track()

        #Plot 
        self.custom= add_plot(mdata , self.plots)

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)

        self.calculate_average_time() 

        print("step time ms:", self.step_interval) 

        timer.start(self.step_interval*1000)  # because timer.start is in ms not in s

        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == "__main__":
    # Load dummy file
    # DO NOT WORK
    with open("model/sample_dict_debug_anim_3D.txt", "r") as inf:
        dict_from_file = eval(inf.read())

    v = Visualizer3D()
    v.animation(dict_from_file, True)
