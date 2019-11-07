#coding:utf-8
"""
PARALOGER ANALYSIS 
Fred - 7/11/2019
"""
import sys
import os
import time
import pickle

from pyqtgraph.Qt import QtCore, QtGui

from gui.main_gui import  Ui_MainWindow

from model import timeit, Flight, Sections

import logging
from logging.handlers import RotatingFileHandler

os.environ["DISPLAY"] = ":0" #Use for linux  on vscode at least

__version__ = '0.1'

if __name__ == "__main__":
    import sys


def config_logger():
    logger = logging.getLogger()
    # logging.basicConfig(filename='1_import.log',level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s ::  %(message)s"
    )
    file_handler = logging.handlers.RotatingFileHandler("main_paralogger.log", "a", 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Redirect log on console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger

logger = config_logger()    

    



class Prog(QtGui.QMainWindow):
    

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        #Set up variable
        self.flight = None

        #add Action
        self.ui.actionOpen.triggered.connect(self.open_pickle_file)

        

    def open_pickle_file(self):
        logger.debug(" Menu :  open")
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open pickler File', "", 'Pickle Files (*.pkl)')
        if isinstance(filename, tuple):
            filename = filename[0]
        if filename:
            try:
                logger.info(" importing : " + str(filename))
                self.file_name = filename
                self.id = 0
                with open(filename, 'rb') as pickle_file:
                    self.flight = pickle.load(pickle_file)

                self.load_project_tree()

           
            except Exception as ex:
                print(ex)
        

    def load_project_tree(self):
        print("load_project_tree")


def main():
    logger.info(" --- Start ----")
    app =  QtGui.QApplication(sys.argv)
    MyProg = Prog()
    MyProg.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



# MISC
# pyuic5 paraloger_GUI1.ui > main_gui.py
