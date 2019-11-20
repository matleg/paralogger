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

from gui.main_gui import Ui_MainWindow

from model import timeit, Flight, Sections
from gui.Tab_3D import Visualizer3D
from gui.Tab_Graph import generated_layout
from gui.Tab_Table import pandasTableModel
from gui.Tab_log import QTextEditLogger

import logging
from logging.handlers import RotatingFileHandler

os.environ["DISPLAY"] = ":0"  #Use for linux  on vscode at least

__version__ = '0.1'

if __name__ == "__main__":
    import sys

log_file_name = "main_paralogger.log"


def config_logger():
    logger = logging.getLogger()
    # logging.basicConfig(filename='1_import.log',level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(module)s :: %(funcName)s ::  %(message)s")
    file_handler = logging.handlers.RotatingFileHandler(log_file_name, "a", 1000000, 1)
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
        super().__init__(None)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer(self)

        #set up the log tab
        logTextBox = QTextEditLogger(self)

        logTextBox.setFormatter(
            logging.Formatter('"%(asctime)s - %(levelname)s \t- %(module)s \t- %(funcName)s ::  %(message)s"'))
        logging.getLogger().addHandler(logTextBox)
        layout_log = QtWidgets.QVBoxLayout()
        layout_log.addWidget(logTextBox.widget)
        self.ui.tab_log.setLayout(layout_log)
        logger.info("--- Start ---")

        #Set up variable
        self.flight = None
        self.visualizer_3d = None

        #add Action
        self.ui.actionOpen.triggered.connect(self.open_pickle_file)
        self.ui.actionSave_as.triggered.connect(self.save_pickle_file)
        self.ui.actionVersion.triggered.connect(self.about_popup)
        self.ui.actionHelp.triggered.connect(self.openUrl_help)
        self.ui.actiondebug_open.triggered.connect(self.debug)

        self.ui.treeWidget.itemClicked.connect(self.onTreeItemClicked)
        self.ui.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeWidget.customContextMenuRequested.connect(self.openMenu)

        #setup Qtree
        self.ui.treeWidget.setHeaderLabels(["Name", "Kind", "Id"])

        #setup table view detail section
        self.ui.model = QtGui.QStandardItemModel(self)  # SELECTING THE MODEL - FRAMEWORK THAT HANDLES QUERIES AND EDITS
        self.ui.tableView.setModel(self.ui.model)  # SETTING THE MODEL
        self.ui.model.dataChanged.connect(self.on_datachange_model)

    def debug(self):
        ''' only use for speed up de developement
        '''
        self.open_pickle_file("mflight_plot_V1.pkl")

    def open_pickle_file(self, filename=None):
        logger.debug(" Menu :  open")

        if filename == False:
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
                logger.error(ex)

    def save_pickle_file(self):
        try:
            tuple_saved_file = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '', 'Pickle(*.pkl)')
            name_saved_file = tuple_saved_file[0] + '.pkl'
            logger.info("Saving as : " + name_saved_file[0] + '.pkl')
            with open(name_saved_file, "wb") as f:
                pickle.dump(self.flight, f)

        except Exception as ex:
            logger.error(ex)

    def about_popup(self):
        """ About section 
        Display various info  for debug and  log file details
        """

        # from https://stackoverflow.com/questions/54447535/how-to-fix-typeerror-in-qtwidgets-qmessagebox-for-popup-messag
        cwd = os.path.dirname(os.path.abspath(__file__))
        log_file_path = ulog_file_path = os.path.join(cwd, log_file_name)

        with open(log_file_path, 'r') as file:
            log_content = file.read()

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Version : " + str(__version__) + "\n"
                    "Log file name: " + str(log_file_name) + "\n"
                    "curent working directory: " + str(cwd))
        msg.setInformativeText("More info on :\nhttps://github.com/fredvol/paralogger ")
        msg.setWindowTitle("About")
        msg.setDetailedText(log_content)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)  #| QtWidgets.QMessageBox.Cancel)

        retval = msg.exec_()

    def openUrl_help(self):
        url = QtCore.QUrl('https://github.com/fredvol/paralogger')
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')

    ### TREE VIEW
    def update_project_tree(self):
        logger.info("load_project_tree")
        tw = self.ui.treeWidget
        tw.clear()
        l1 = QtWidgets.QTreeWidgetItem([self.flight.glider, "--", self.flight.id])

        for sect in self.flight.sections:
            l1_child = QtWidgets.QTreeWidgetItem([str(sect.start) + " - " + str(sect.end), sect.kind, sect.id])
            l1.addChild(l1_child)

        tw.addTopLevelItem(l1)
        tw.expandAll()

    def get_level_from_index(self, indexes):

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

        indexes = self.ui.treeWidget.selectedIndexes()

        level = self.get_level_from_index(indexes)

        if level >= 0:
            uid = it.text(2)  # The text of the node.
            logger.debug("clicked: " + str(it) + ", " + str(col) + ", " + str(uid) + " level: " + str(level))
        else:
            uid = None

        if level == 0:  # flight  level
            self.populate(uid, level)

        elif level == 1:  # section level
            #update all tabs
            self.display_tab_graph(uid)
            self.display_tab_Table(uid)
            self.display_tab_3D(uid)

            self.populate(uid, level)

    def openMenu(self, position):
        indexes = self.ui.treeWidget.selectedIndexes()
        item = self.ui.treeWidget.itemAt(position)
        #

        menu = QtWidgets.QMenu()

        level = self.get_level_from_index(indexes)
        if level > 0 and item != None:
            uid = item.text(2)  # The text of the nodel

        if level == 0:
            action_add = menu.addAction(self.tr("Add Section"))
            action_add.triggered.connect(self.add_section)
            action_refresh = menu.addAction(self.tr("Refresh"))
            action_refresh.triggered.connect(self.update_project_tree)

        elif level == 1:
            action_del = menu.addAction('Delete')
            action_del.triggered.connect(lambda: self.delete_section(uid))

            action_refresh = menu.addAction(self.tr("Refresh"))
            action_refresh.triggered.connect(self.update_project_tree)

        menu.exec_(self.ui.treeWidget.viewport().mapToGlobal(position))

    def delete_section(self, uid):
        logger.info("delete section :" + str(uid))
        self.flight.delete_section(uid)
        self.update_project_tree()

    def add_section(self):
        logger.info("add section")
        self.flight.add_general_section()
        self.update_project_tree()

    #### TAB WIDGET ACTIONS

    def display_tab_3D(self, uid):

        df_to_plot = self.flight.apply_section(uid)

        # mainLayout = QtWidgets.QVBoxLayout()

        self.visualizer_3d = Visualizer3D(self.ui.tab_3d)
        # self.setCentralWidget(self.ui.main_tabWidget)

        # mainLayout.addWidget(v.mainWidget)

        self.visualizer_3d.animation(df_to_plot, True, timer=self.timer)

        self.ui.tab_3d.setLayout(self.visualizer_3d.layout_general)

    def display_tab_Table(self, uid):
        df_to_plot = self.flight.apply_section(uid)

        model = pandasTableModel(df_to_plot)
        if len(self.ui.tab_table.children()) > 0:
            print(" existing")
            self.ui.tab_table.children()[1].setModel(model)
        else:
            mainLayout = QtWidgets.QVBoxLayout()

            view = QtWidgets.QTableView()
            view.setModel(model)

            print("")
            #view.model.

            mainLayout.addWidget(view)

            self.ui.tab_table.setLayout(mainLayout)

    def display_tab_graph(self, uid):

        df_to_plot = self.flight.apply_section(uid)
        inside_widget = generated_layout(df_to_plot)

        #empty actual area if exist
        if len(self.ui.tab_graph.children()) > 0:
            print("not empty")
            layout = self.ui.tab_graph.children()[0]

            for i in reversed(range(layout.count())):
                widgetToRemove = layout.itemAt(i).widget()
                # remove it from the layout list
                layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
            layout.addWidget(inside_widget)

        else:
            mainLayout = QtWidgets.QVBoxLayout()
            mainLayout.addWidget(inside_widget)
            self.ui.tab_graph.setLayout(mainLayout)

    ## DETAILS OBJECT

    def on_datachange_model(self, signal):
        row = signal.row()  # RETRIEVES ROW OF CELL THAT WAS DOUBLE CLICKED
        column = signal.column()  # RETRIEVES COLUMN OF CELL THAT WAS DOUBLE CLICKED
        cell_dict = self.ui.model.itemData(signal)  # RETURNS DICT VALUE OF SIGNAL
        cell_value = cell_dict.get(0)  # RETRIEVE VALUE FROM DICT

        uid = self.ui.model.itemData(signal.sibling(0, 1)).get(0)

        index = signal.sibling(row, 0)
        index_dict = self.ui.model.itemData(index)
        index_value = index_dict.get(0)
        logger.debug('Edited Row {}, Col {} value: {} index_value: {}, uid: {}'.format(
            row, column, cell_value, index_value, uid))

        ## Update the Data model ( self.flight) from the changed done in self.ui_model
        if self.flight.id == uid:
            setattr(self.flight, index_value, cell_value)
        else:
            for sect in self.flight.sections:
                if sect.id == uid:
                    setattr(sect, index_value, cell_value)

        ## Update tree view:
        self.update_project_tree()

    def populate(self, uid, level):
        """ Add data in the Table view , via model
        """
        # MODEL ONLY ACCEPTS STRINGS - MUST CONVERT.

        logger.debug("display_properties: " + str(uid))
        self.ui.model.clear()

        if level == 0:
            dict_to_display = vars(self.flight)
        elif level == 1:
            dict_to_display = vars(self.flight.section_by_id(uid))

        for name, value in dict_to_display.items():
            row = []
            cell_name = QtGui.QStandardItem(str(name))
            row.append(cell_name)
            cell_value = QtGui.QStandardItem(str(value))
            row.append(cell_value)

            self.ui.model.appendRow(row)

        # self.show()


def main():
    logger.info(" --- Start ----")
    app = QtGui.QApplication(sys.argv)
    MyProg = Prog()
    MyProg.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# MISC
# pyuic5 paraloger_GUI1.ui > main_gui.py
# panda to table view:  https://stackoverflow.com/questions/44603119/how-to-display-a-pandas-data-frame-with-pyqt5-pyside2
#
