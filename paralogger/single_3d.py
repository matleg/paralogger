# -*- coding: utf-8 -*-
"""
Simple examples demonstrating the use of GLMeshItem.

"""


from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

import os
os.environ['DISPLAY']=':0'


app = QtGui.QApplication([])

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


    

plot_single(5,10,8,0,45, 80)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

  
