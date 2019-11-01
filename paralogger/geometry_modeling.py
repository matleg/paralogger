# -*- coding: utf-8 -*-
"""
    Creating Geometry
"""

import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import itertools
import pprint

from objFileLoader import objObject


class Create_geom:
    """
    Classe used to create different Mesh geometry
    """

    @staticmethod
    def cylinder():
        md = gl.MeshData.cylinder(rows=10, cols=20, radius=[1.0, 1.0], length=3.0)

        geom = gl.GLMeshItem(
            meshdata=md,
            smooth=False,
            drawFaces=False,
            drawEdges=True,
            edgeColor=(1, 1, 0, 1),
        )
        return geom
        # draw cube

    @staticmethod
    def cube():
        vertexes = np.array(list(itertools.product(range(2), repeat=3)))

        faces = []

        for i in range(2):
            temp = np.where(vertexes == i)
            for j in range(3):
                temp2 = temp[0][np.where(temp[1] == j)]
                for k in range(2):
                    faces.append([temp2[0], temp2[1 + k], temp2[3]])

        faces = np.array(faces)

        pprint = faces

        colors = np.array([[i * 5, i * 5, i * 5, 0] for i in range(12)])

        geom = gl.GLMeshItem(
            vertexes=vertexes, faces=faces, faceColors=colors, drawEdges=True
        )
        return geom

    @staticmethod
    def obj(fpath):
        """ Load from Waveform OBJ format 
        Should be triangulated
        """
        obj = objObject()
        obj.loadFile(fpath)
        print(obj)

        vertexes = np.array(list(obj.v))

        mfaces = np.array(obj.face)
        mfaces = mfaces.astype(np.int64)
        mfaces = mfaces - 1

        geom = gl.GLMeshItem(vertexes=vertexes, faces=mfaces, drawEdges=True)
        return geom
