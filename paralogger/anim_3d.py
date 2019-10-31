"""
    Animated 3D sinc function
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import itertools
from geometry_modeling import Create_geom
from PyQt5.QtWidgets import QWidget

# import pkg_resources

import os

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


def convert_df_2_data(mdf):

    mdf[["pitch", "yaw", "roll"]] = mdf[["pitch", "yaw", "roll"]].apply(np.rad2deg)

    # Reorient data
    mdf["y"] = mdf["y"] * -1
    mdf["z"] = mdf["z"] * -1
    mdf["pitch"] = mdf["pitch"] * -1
    mdf["yaw"] = mdf["yaw"] * -1

    # Work on Gps coordinate
    lon = mdf["lon"].to_numpy() / 1e7  # degrees
    lat = mdf["lat"].to_numpy() / 1e7
    altitude = mdf["alt"].to_numpy() / 1e3  # meters

    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)

    anchor_lat = 0
    anchor_lon = 0
    lat, lon = map_projection(lat, lon, anchor_lat, anchor_lon)
    lat = lat - lat[0]
    lon = lon - lon[0]
    altitude = altitude - altitude[0]

    mdf["lat_m"] = lat
    mdf["lon_m"] = lon
    mdf["alt_m"] = altitude
    data_table = mdf[
        ["x", "y", "z", "lat_m", "lon_m", "alt_m", "pitch", "roll", "yaw"]
    ].to_numpy()
    return data_table


def calculate_average_time(mdf):
    duration = mdf.iloc[-1]["time0_s"] - mdf.iloc[0]["time0_s"]
    nb_record = len(mdf)
    average_step_time = duration / nb_record

    print("average_step_time", average_step_time)

    return average_step_time


def extract_path_track(mdf):
    print("add_path_track ")
    data_track = mdf[["lat_m", "lon_m", "alt_m"]].to_numpy()

    return data_track


class Visualizer3D(object):
    def __init__(self, parent):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)

        self.w = gl.GLViewWidget(parent=parent)
        self.w.opts["distance"] = 160
        self.w.setWindowTitle("3D view track")
        self.w.setGeometry(0, 110, 720, 480)

        self.data = None
        self.track = None
        self.track_is_ploted = False
        self.index = 0

        # Created the geometrie

        models_path = os.path.dirname(os.path.abspath(__file__))
        obj = "simple_body.obj"
        obj_path = os.path.join(models_path, "3D_model", obj)
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

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
            sys.exit(QtGui.QApplication.instance().exec_())

    def update(self):

        self.index = (self.index + 1) % len(self.data)

        i = self.index
        if i == 0:
            print("loop animation ")

        self.geom.resetTransform()
        # Important  to rotate before translated
        self.geom.rotate(self.data[i][6], 0, 1, 0)
        self.geom.rotate(self.data[i][7], 1, 0, 0)
        self.geom.rotate(self.data[i][8], 0, 0, 1)

        self.geom.translate(self.data[i][3], self.data[i][4], self.data[i][5])

        self.w.addItem(self.geom)

        # Add track if exist:
        if self.track is not None and not self.track_is_ploted:
            print("ploting track")
            plt = gl.GLLinePlotItem(pos=self.track, antialias=True)
            self.w.addItem(plt)
            self.track_is_ploted = True

    def animation(self, mdata, plot_track):

        print("total records:" + str(len(mdata)))

        self.data = convert_df_2_data(mdata)

        if plot_track:
            self.track = extract_path_track(mdata)

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        step_interval = calculate_average_time(mdata) * 100
        print("step time ms:", step_interval)

        timer.start(step_interval)

        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == "__main__":
    # Load dummy file
    with open("model/sample_dict_debug_anim_3D.txt", "r") as inf:
        dict_from_file = eval(inf.read())

    v = Visualizer3D()
    v.animation(dict_from_file, True)

