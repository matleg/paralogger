#coding:utf-8
"""
PARALOGER ANALYSIS 
Fred - 7/11/2019
"""
import sys
import os
import time
import pickle

from pyqtgraph.Qt import QtCore, QtGui, QtWidgets



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

        self.ui.treeWidget.itemClicked.connect(self.onTreeItemClicked)
        self.ui.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeWidget.customContextMenuRequested.connect(self.openMenu)

        self.ui.tableWidget.itemChanged.connect(self.onTableItemChanged)
        #self.ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.CurrentChanged)



        #setup Qtree
        self.ui.treeWidget.setHeaderLabels(["Name","Kind","Id"])
        

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

                self.update_project_tree()
   
            except Exception as ex:
                print(ex)
        
    ### TREE VIEW
    def update_project_tree(self):
        logger.info("load_project_tree")
        tw = self.ui.treeWidget
        tw.clear() 
        l1 = QtWidgets.QTreeWidgetItem([self.flight.glider, "--" ,self.flight.id])


        for sect in self.flight.sections:
            l1_child = QtWidgets.QTreeWidgetItem([str(sect.start) + " - " +str(sect.end), sect.kind ,sect.id])
            l1.addChild(l1_child)

        tw.addTopLevelItem(l1)
        tw.expandAll()

    def get_level_from_index(self,indexes):

        if len(indexes) > 0:

            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        else:
            level = -1

        return level

    
    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onTreeItemClicked(self, it, col):
        #logger.debug("clicked QTreeWidgetItem ")

        indexes = self.ui.treeWidget.selectedIndexes()

        level = self.get_level_from_index(indexes)

        if level >= 0:
            uid = it.text(2)  # The text of the node.
            logger.debug("clicked: "+ str(it) +", "+ str(col) + ", "+  str(uid) + " level: "+ str(level))
        else: 
            uid=None

        if level == 0:   # flight  level
            self.display_properties_flight(uid,level)
            
        elif level == 1:   # section level
            self.display_properties_flight(uid,level)
            

    def openMenu(self, position):
        indexes = self.ui.treeWidget.selectedIndexes()
        item = self.ui.treeWidget.itemAt(position)
        #

        menu = QtWidgets.QMenu()
        
        level = self.get_level_from_index(indexes)
        if level >0:
            uid = item.text(2)  # The text of the node.

        if level == 0:
            action_add = menu.addAction(self.tr("Add Section"))
            action_add.triggered.connect(self.add_section)
            
        elif level == 1:
            action_del = menu.addAction('Delete')
            action_del.triggered.connect(lambda: self.delete_section(uid))

            menu.addAction(self.tr("Export"))
        elif level == -1:
            action_refresh = menu.addAction(self.tr("Refresh"))
            action_refresh.triggered.connect(self.update_project_tree)
        
        menu.exec_(self.ui.treeWidget.viewport().mapToGlobal(position))

    def delete_section(self,uid):
        logger.info("delete section :" +str(uid))
        self.flight.delete_section(uid)
        self.update_project_tree()

    def add_section(self):
        logger.info("add section")
        self.flight.add_general_section()
        self.update_project_tree()
        

    ## DETAILS OBJECT
    
    def display_properties_flight(self,index , level):
        logger.debug("display_properties: " + str(index))
        
        if level == 0:
            dict_to_display =  vars(self.flight)
        elif level ==1 :
            dict_to_display = vars(self.flight.section_by_id(index)[0])

        table_view = self.ui.tableWidget
        table_view.clear()
        # set row count
        table_view.setColumnCount(2)
        table_view.setRowCount(len(dict_to_display))

        # set column count
        table_view.setColumnCount(2)

        i=0
        for name, value in dict_to_display.items(): 
            try:
                table_view.setItem(i,0, QtWidgets.QTableWidgetItem(name))

                item_value = QtWidgets.QTableWidgetItem(str(value))
                #item_value.setFlags(QtCore.Qt.ItemIsEditable)

                table_view.setItem(i,1,item_value )

                i+=1
            except :
                pass
            
    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def onTableItemChanged(self,item):
        self.changed_items.add(self.item)
        print(self.item)
        # indexes = self.ui.tableWidget.selectedIndexes()
        # print("h")
        # print("clicked QTreeWidgetItem " ,item)

    def display_properties_section(self,index):
        print("")


        


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
# panda to table view:  https://stackoverflow.com/questions/44603119/how-to-display-a-pandas-data-frame-with-pyqt5-pyside2
# 