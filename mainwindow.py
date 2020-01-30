"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import logging
import os
#import resource
import sys
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import ( QMainWindow, QMessageBox, QFileDialog, 
                             QDockWidget, QWidget, QVBoxLayout )
#    QVBoxLayout, QWidget, QTreeView, QItemDelegate, QAbstractItemView, , QApplication)
    
#    QGroupBox, QFormLayout, QLabel, QLineEdit, 
#    QScrollArea,  QSizePolicy      )
#from PyQt5.QtGui import QStandardItemModel, QStandardItem 
from PyQt5.QtCore import Qt, QSettings
#from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QSortFilterProxyModel
##from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

from UI.ui_mainwindow import Ui_MainWindow

#from tree.nodes import tree_from_JSON
from tree.models import fstreemodel_from_JSON
from tree.file_system_tree import fstree_from_JSON, make_file_system_tree, fstree_from_vndict
from tree.database_list import DBtreeW
from tree.metadata_view import MetadataList
from metadata.database_blitz import DbDocFileMetadata, VisinumDatabase, open_database, dict_from_DB
#from utilities.metadata import file_metadata_to_dict, node_metadata_to_db
from utilities.vnfunctools import patch_func_into_cls
from utilities.vnjson import attrs_to_JSON, attr_from_JSON

VisinumDB_name  = "_VisnumDB"


class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName('mainwindow')

        self.setupUi(self)
        self.dbtreeW = DBtreeW(self.page_databases)
        self.page_databasesVL.addWidget(self.dbtreeW)
        self.databasesTV.setVisible(False)

        #self.actionOpenFile.triggered.connect(self.openFile)
        self.actionOpen_database.triggered.connect(self.openDatabase)
        #self.actionImportFile.triggered.connect(self.importFile)
        #self.actionExport.triggered.connect(self.exportFile)
        #self.actionSaveFile.triggered.connect(self.saveFile)
        #self.actionCloseFile.triggered.connect(self.closeFile)
        self.actionQuit.triggered.connect(self.close)
        self.actionExtract_metadata.triggered.connect(self.extract_metadata)
        
        self.workingdir = '.'
        self.dblist = []
        self.restoreSettings()
        
        #self.mdataListWid.setupDataMapper(self.dataTreeView)
        #self.metdatalist = MetadataList()
        #self.dockWidgetContents = self.metdatalist
        #self.metdatalist = self.miscTB
        #self.metdatalist.setupDataMapper(self.datatreeTV)
        ##logger.info('Memory use: %s (kb)' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,) )


        """self.miscDW2 = QDockWidget(self)
        self.miscDW2.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.miscDW2.setAllowedAreas(Qt.RightDockWidgetArea)
        self.miscDW2.setObjectName("miscDW2")
        self.dockWidgetContents2 = QWidget()
        self.dockWidgetContents2.setObjectName("dockWidgetContents2")
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.metdatalist = MetadataList(self.dockWidgetContents2) ###
        self.metdatalist.setObjectName("metdatalist")
        self.verticalLayout_5.addWidget(self.metdatalist)
        self.miscDW2.setWidget(self.dockWidgetContents2)
        self.addDockWidget(Qt.DockWidgetArea(2), self.miscDW2)"""
        #self.metdatalist = MetadataList()
        #self.metdatalist.setupDataMapper(self.datatreeTV)
        
    def openFile(self):
        reply = QFileDialog.getOpenFileName(self, "Open a Visinum file", 
                 self.workingdir, "Visinum (*.visinum);;All files (*.*)")
        fpath = reply[0]
        if not fpath:
            return
        self.workingdir = os.path.dirname(fpath)
        treemodel = fstreemodel_from_JSON(fpath)
        self.dataTreeView.setModel(treemodel)
        rootNode = self.dataTreeView.model().rootItem
        rootNode.name = "Newname was '" + rootNode.name + "'"

    def openDatabase(self):
        dirpath = QFileDialog.getExistingDirectory(self, "Select directory containing visinum database", 
                 self.workingdir, QFileDialog.ShowDirsOnly)
        if not dirpath:
            return
        elif os.path.basename(dirpath) == VisinumDB_name:
            pass            
        elif os.path.isdir( os.path.join(dirpath, VisinumDB_name) ):
            dirpath = os.path.join(dirpath, VisinumDB_name)
        elif not os.path.isdir( os.path.join(dirpath, VisinumDB_name) ):
            logger.warning("Cannot find a visinum database (%s) in directory %s" % (VisinumDB_name, dirpath))
            return
        self.workingdir = os.path.dirname(dirpath) # directory containing VisinumDB
        print(dirpath, self.workingdir)
        db = VisinumDatabase(dirpath)
        self.dblist.append( db )
        self.dbtreeW.dbtreeview.update_dblist()

    def openDatabase2(self):
        dirpath = QFileDialog.getExistingDirectory(self, "Select directory containing visinum database", 
                 self.workingdir, QFileDialog.ShowDirsOnly)
        if not dirpath:
            return
        elif os.path.basename(dirpath) == VisinumDB_name:
            pass            
        elif os.path.isdir( os.path.join(dirpath, VisinumDB_name) ):
            dirpath = os.path.join(dirpath, VisinumDB_name)
        elif not os.path.isdir( os.path.join(dirpath, VisinumDB_name) ):
            logger.warning("Cannot find a visinum database (%s) in directory %s" % (VisinumDB_name, dirpath))
            return
        self.workingdir = os.path.dirname(dirpath) # directory containing VisinumDB
        print(dirpath, self.workingdir)
        db = VisinumDatabase(dirpath)
        self.opendb.append( db )
        datatree_UUID = attr_from_JSON( os.path.join(fpath, 
                        "vnconfig.visijson"),  "datatree_UUID")
        print("datatree_UUID=", datatree_UUID)
        print("self.db=", self.db)
        dict_ = dict_from_DB(self.db, datatree_UUID)
        fstree = fstree_from_vndict(dict_)
        model = self.dataTreeView.model()
        position = model.rootItem.count_child()
        success=model.insertRows(position, numrows=1, parent=None, nodes=fstree)
        if not success:
            logger.warning("Failed to import file %s" % (fpath,))
        return fpath

    def extract_metadata(self):
        dirpath = QFileDialog.getExistingDirectory(self, "Select directory base for file metadata", 
         self.workingdir, QFileDialog.ShowDirsOnly)
        if not dirpath:
            return
        self.workingdir = dirpath
        print("extract_metadata_dir=", dirpath, self.workingdir)
        db = VisinumDatabase(dirpath)
        self.dblist.append( db )
        db.extract_file_metadata(dirpath)
        self.dbtreeW.dbtreeview.update_dblist()


    def extract_metadata2(self):
        fpath = self.openDatabase()
        rootNode = make_file_system_tree(fpath, excludedirs=[VisinumDB_name])
        #patch_func_into_cls(rootNode.__class__, node_metadata_to_db)
        rootNode.__class__.node_metadata_to_db = node_metadata_to_db
        for node in list(rootNode):
            node.node_metadata_to_db(self.db, fpath)
        logger.info("Completed processing data tree %s" % (rootNode.name,)) 
        tree_dict = rootNode.to_vndict()
        tree_UUID = rootNode.get_data("UUID")
        tree_data = DbDocFileMetadata( tree_dict )
        tree_data.save(self.db)
        self.db.commit()
        attrs_to_JSON(os.path.join(fpath, VisinumDB_name, "vnconfig.visijson"), 
                      {"visinum_type":"visinum_config", "datatree_UUID":tree_UUID})

    def get_DB_dir(self):
        fpath = QFileDialog.getExistingDirectory(self, "Select directory containing visinum database", 
         self.workingdir, QFileDialog.ShowDirsOnly)
        if not fpath:
            return
        #if os.path.basename(fpath) == VisinumDB_name:
        #    pass #  fpath = fpath         #fpath = os.path.dirname(fpath)            
        #elif os.path.isdir( os.path.join(fpath, VisinumDB_name) ):
        #    fpath = os.path.join(fpath, VisinumDB_name)
        #elif not os.path.isdir( os.path.join(fpath, VisinumDB_name) ):
        #    logger.warning("Cannot find a visinum database (%s) in directory %s" % (VisinumDB_name, fpath))
        #    return
        self.workingdir = fpath
        print("get_dir=", fpath, self.workingdir)
        return fpath


    def importFile(self):
        reply = QFileDialog.getOpenFileName(self, "Import data file", 
                 self.workingdir, "Visinum  (*.visi*);;JSON (*.json);;All files (*.*)")
        fpath = reply[0]
        if not fpath:
            return  # Cancel pressed
        self.workingdir = os.path.dirname(fpath)
        fstree = fstree_from_JSON(fpath)
        model = self.dataTreeView.model()
        position = model.rootItem.count_child()
        success=model.insertRows(position, numrows=1, parent=None, nodes=fstree)
        if not success:
            logger.warning("Failed to import file %s" % (fpath,))
            

    def exportFile(self):
        pass

    def saveFile(self):
        pass

    def closeFile(self):
        pass


    def closeEvent(self, event):
        reply = QMessageBox.warning(self, 'Closing down...', 
                    "Quit Visinum?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.saveSettings()
            event.accept()
        else:
            event.ignore()

    def restoreSettings(self):
        settings = QSettings()
        if not settings.value("MainWindow/Geometry"):
            return
        self.restoreGeometry( settings.value("MainWindow/Geometry") )
        self.restoreState( settings.value("MainWindow/State") )
        workingdir = settings.value("workingdir", defaultValue=None)
        if isinstance(workingdir, str) and os.path.isdir(workingdir):
            self.workingdir = workingdir

    def saveSettings(self):
        settings = QSettings()
        settings.setValue("MainWindow/Geometry", self.saveGeometry())
        settings.setValue("MainWindow/State", self.saveState() )
        settings.setValue("workingdir", self.workingdir )   





if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Visinum-Metadata")
    app.setOrganizationName("Qwilka")
    app.setOrganizationDomain("qwilka.com") 
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
