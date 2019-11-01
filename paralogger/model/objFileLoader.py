#[MIT license:]
#
# Copyright (c) 2011  Dave Pape
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math, types, string
import os

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class objObject:
    ''' Class to import OBJ  file ,
    Need to be clean
    Originaly imported from pyFlightAnalysis :
    https://github.com/Marxlp/pyFlightAnalysis/blob/master/src/objloader.py
    '''




    def __init__(self, filename=None, debugmode=True):
        self.v = []
        self.vn = []
        self.vt = []
        self.mtl = []
        self.face = []
        self.geometry = []
        self.materials = {}
        self.displayListInitted = False
        self.hasNormals = False
        self.debugmode = debugmode
        self.r = []
        self.maxR = 0
        self.path = None
        if filename:
            self.loadFile(filename)   

            
    def loadFile(self, filename):
        self.fileName = filename
        self.path = os.path.dirname(filename)
        self.lineNum = 0
        for line in open(filename, 'r').readlines():
            self.lineNum += 1
            values = line.split()
            if len(values) < 1:
                continue
            elif values[0] == 'v':
                self.parseVertex(values)
            elif values[0] == 'vn':
                self.parseNormal(values)
            elif values[0] == 'vt':
                self.parseTexCoord(values)
            elif (values[0] == 'f') or (values[0] == 'fo'):
                self.parseFace(values)
            elif values[0] == 'l':
                self.parseLine(values)
            elif values[0] == 'p':
                self.parsePoints(values)

    def parseVertex(self, val):
        if len(val) < 4:
            if self.debugmode:
                print('warning: incomplete vertex info:', self.fileName, 'line', self.lineNum)
            self.v.append([0, 0, 0])
        else:
            self.v.append([float(val[1]), float(val[2]), float(val[3])])
            

            
    def parseNormal(self, val):
        if len(val) < 4:
            if self.debugmode:
                print('warning: incomplete normal info:', self.fileName, 'line', self.lineNum)
            self.vn.append([0, 0, 0])
        else:
            self.vn.append([float(val[1]), float(val[2]), float(val[3])])
            self.hasNormals = True
            
    def parseTexCoord(self, val):
        if len(val) < 3:
            if self.debugmode:
                print('warning: incomplete texcoord info:', self.fileName, 'line', self.lineNum)
            self.vt.append([0, 0])
        else:
            self.vt.append([float(val[1]), float(val[2])])
            
    def parseFace(self, val):
        if len(val) < 4:
            return
        self.face.append( val[1:])
            
    def parseLine(self, val):
        if len(val) < 3:
            return
        line = WFObject.wfline()
        line.points = self.parsePointList(val)
        self.geometry.append(line)
            
    def parsePoints(self, val):
        if len(val) < 2:
            return
        pt = WFObject.wfpoints()
        pt.points = self.parsePointList(val)
        self.geometry.append(pt)
        
    def parsePointList(self, val):
        points = []
        for v in val[1:]:
            p = { }
            data = v.split('/')
            if len(data) > 0:
                index = int(data[0])
                if index > 0:
                    p['v'] = self.v[index-1]
                elif index < 0:
                    p['v'] = self.v[len(self.v)+index]
            if len(data) > 1:
                index = int('0'+data[1])
                if index > 0:
                    p['vt'] = self.vt[index-1]
                elif index < 0:
                    p['vt'] = self.vt[len(self.vt)+index]
            if len(data) > 2:
                index = int('0'+data[2])
                if index > 0:
                    p['vn'] = self.vn[index-1]
                elif index < 0:
                    p['vn'] = self.vn[len(self.vn)+index]
            points.append(p)
        return points
            
    def parseMtllib(self, val):
        if len(val) < 2:
            return
        curmtl = WFObject.wfmaterial()
        for line in open(os.path.join(self.path,val[1])).readlines():
            values = line.split()
            if len(values) < 1:
                continue
            if values[0] == 'newmtl':
                curmtl = WFObject.wfmaterial()
                if len(values) > 1:
                    self.materials[values[1]] = curmtl
            elif values[0] == 'illum':
                if len(values) > 1:
                    curmtl.illum = int(values[1])
            elif values[0] == 'Ns':
                if len(values) > 1:
                    curmtl.Ns = float(values[1])
            elif values[0] == 'Kd':
                if len(values) > 3:
                    curmtl.Kd = [float(values[1]), float(values[2]), float(values[3]), 1]
            elif values[0] == 'Ka':
                if len(values) > 3:
                    curmtl.Ka = [float(values[1]), float(values[2]), float(values[3]), 1]
            elif values[0] == 'Ks':
                if len(values) > 3:
                    curmtl.Ks = [float(values[1]), float(values[2]), float(values[3]), 1]
            elif values[0] == 'map_Kd':
                if len(values) > 1:
                    curmtl.texture = pyglet.image.load(values[1]).get_mipmapped_texture()
                    
