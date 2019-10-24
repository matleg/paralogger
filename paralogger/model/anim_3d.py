# -*- coding: utf-8 -*-
"""
    Animated 3D sinc function
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import itertools
from model.geometry_modeling import Create_geom 
# import pkg_resources

import os
os.environ['DISPLAY']=':0'

# resource_package = __name__ 

# def get_source_name(file_path_name):
#     return pkg_resources.resource_filename(resource_package,file_path_name)


#m1 = gl.GLMeshItem(meshdata=md, smooth=False, drawFaces=False, drawEdges=True, edgeColor=(1,1,0,1)) 
def convert_df_2_data( mdf):

    mdf[['pitch', 'yaw','roll']] = mdf[['pitch', 'yaw','roll']].apply(np.rad2deg)

    data_table = mdf[['x','y','z','pitch','roll','yaw']].to_numpy()
    return data_table 

def calculate_average_time( mdf):
    duration = mdf.iloc[-1]['time0_s']-mdf.iloc[0]['time0_s']
    nb_record = len(mdf)
    average_step_time = duration / nb_record

    print('average_step_time',average_step_time)

    return average_step_time

def extract_path_track(mdf):
    print("add_path_track " )
    data_track = mdf[['x','y','z']].to_numpy()

    return data_track

class Visualizer3D(object):

    def __init__(self ):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 160
        self.w.setWindowTitle('3D view track')
        self.w.setGeometry(0, 110, 1920, 1080)
        self.w.show()

        self.data = None
        self.track = None
        self.track_is_ploted =False
        self.index = 0

        #Created the geometrie
 
        self.geom= Create_geom.obj("3D_model/simple_body.obj")  


        # create the background grids
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

 
    

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
    
  
    def update(self):
                
        self.index = (self.index + 1) % len(self.data)

        i= self.index 
        if i ==0 :
            print("loop animation ")
        
        
        self.geom.resetTransform()
        # Important  to rotate before translated
        self.geom.rotate(self.data[i][3],0,1,0)
        self.geom.rotate(self.data[i][4],1,0,0)
        self.geom.rotate(self.data[i][5],0,0,1)

        self.geom.translate(self.data[i][0],self.data[i][1],self.data[i][2])
     

        self.w.addItem(self.geom)

        
        # Add track if exist:
        if self.track is not None and not self.track_is_ploted:
            print("ploting track")
            plt = gl.GLLinePlotItem(pos=self.track,   antialias=True)
            self.w.addItem(plt)
            self.track_is_ploted = True


    def animation(self, mdata, plot_track):

        print('total records:' + str(len(mdata)))
        self.data = convert_df_2_data(mdata)

        if plot_track:
            self.track = extract_path_track(mdata)

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        step_interval = calculate_average_time(mdata)*100
        print('step time ms:',step_interval)

        timer.start(step_interval)



        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = Visualizer3D()
    v.animation()
