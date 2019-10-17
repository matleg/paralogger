# -*- coding: utf-8 -*-
"""
    Animated 3D sinc function
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys

import os
os.environ['DISPLAY']=':0'

mouv=  [[2,1,2,0,45, 45],
        [2,1,2,0,45, 46],
        [2,1,2,0,45, 47],
        [2,1,2,0,45, 48],
        [2,1,2,0,45, 49],
        [2,1,2,0,46, 50],
        [2,1,2,0,46, 51],
        [2,1,2,0,46, 52],
        [2,1,2,0,46, 53]]



#m1 = gl.GLMeshItem(meshdata=md, smooth=False, drawFaces=False, drawEdges=True, edgeColor=(1,1,0,1)) 


class Visualizer(object):

    def __init__(self):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 80
        self.w.setWindowTitle('3D view track')
        self.w.setGeometry(0, 110, 1920, 1080)
        self.w.show()

        self.index = 0

        self.md = gl.MeshData.cylinder(rows=10, cols=20, radius=[2.0, 2.0], length=5.)

        self.geom = gl.GLMeshItem(meshdata=self.md, smooth=False, drawFaces=False, drawEdges=True, edgeColor=(1,1,0,1)) 

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

        self.n = 15

       
        #for i in range(self.n):
        print("in vizuliaser")

        # m1.translate(mouv[0][0],mouv[0][1],mouv[0][2])
        # m1.rotate(mouv[0][3],0,1,0)
        # m1.rotate(mouv[0][4],1,0,0)
        # m1.rotate(mouv[0][5],0,0,1)

        #self.w.addItem(m1)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
    
  
    def update(self):
        global m1 #,index
        print("in update : " + str(self.index))
                
        self.index = (self.index + 1) % len(mouv)

        i= self.index
        

        self.geom.resetTransform()
        self.geom.translate(mouv[i][0],mouv[i][1],mouv[i][2])
        self.geom.rotate(mouv[i][3],0,1,0)
        self.geom.rotate(mouv[i][4],1,0,0)
        self.geom.rotate(mouv[i][5],0,0,1)

        self.w.addItem(self.geom)


    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(30)
        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = Visualizer()
    v.animation()
