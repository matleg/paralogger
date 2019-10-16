from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np 


import os
os.environ['DISPLAY']=':0'

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 100
w.showMaximized()
w.setWindowTitle('pyqtgraph example: GLViewWidget')

ax = gl.GLAxisItem()
ax.setSize(20,20,20)
w.addItem(ax)

pos = np.mgrid[0:1,0:1,0:1].reshape(3,1,1).transpose(1,2,0)

size = np.empty((1,1,3)) 
size[...,0:2] = 1
size[...,2] = 5

bg = gl.GLBarGraphItem(pos, size)
##bg.setColor(1., 1., 1., 1.)
w.addItem(bg)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()