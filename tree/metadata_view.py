"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import ast
import json
import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import ( QVBoxLayout, QWidget, QTreeView, QItemDelegate, 
                             QAbstractItemView )
from PyQt5.QtGui import QStandardItemModel, QStandardItem 
from PyQt5.QtCore import Qt, QSortFilterProxyModel

from metadata.database_blitz import VisinumDatabase, open_database, dict_from_DB # DbDocFileMetadata, 

class MetadataList(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        #self.resize(100, 100)

        #sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #sizePolicy.setHorizontalStretch(2)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        #self.setSizePolicy(sizePolicy)

        self.mdataview = QTreeView()
        self.mdataview.setHeaderHidden(True)
        self.mdataview.setSortingEnabled(True)
        self.mdataview.setAlternatingRowColors(True)
        self.mdataview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.mdataview.sortByColumn(0, Qt.AscendingOrder)  # Qt.DescendingOrder
        model = QStandardItemModel(0, 2)
        self.mdataview.setModel(model)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mdataview)
        self.setLayout(layout)
        self.setVisible(True)         

    def setupDataMapper(self, treeview):
        self._dataMapper = treeview.dataMapper
        self._dataMapper.setItemDelegate(MetadataDelegate(self)) # self._parent.parent().parent().db
        self._dataMapper.addMapping(self.mdataview, 1)
        treeview.selectionModel().currentChanged.connect(self.setSelection)

    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current) 

    def clearData(self, layout=None):
        # NOT IMPLEMENTED----------------------------------------------
        if hasattr(self, "_dataMapper"):
            self._dataMapper.clearMapping()
        #self.wid.setVisible(False)



class MetadataDelegate(QItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def setEditorData(self, editor, idx):
        modeldata = idx.data(Qt.UserRole)  # idx.data(Qt.DisplayRole)
        ##print(modeldata)
        #print("in setEditorData, db=", editor.window().db)
        #####dict_ = eval(modeldata)
        #if editor.window().db:
        #    dict_ = dict_from_DB(editor.window().db, dict_["UUID"])
        #else:
        dict_ = eval(modeldata) # this expanding DbDocFileMetadata for childs, not desirable, but hard to find an alternative to eval
        #dict_ = ast.literal_eval(modeldata)
        #jsonString = json.dumps(modeldata)
        #dict_ = json.loads(jsonString)
        ###modeldata2 = modeldata.replace("'", '"')
        ###dict_ = json.loads(modeldata2)
        model = editor.model()
        model.clear()
        model = QStandardItemModel(0, 2)
        editor.setHeaderHidden(False)
        model.setHorizontalHeaderLabels(['Attribute', 'Value'])
        # using QSortFilterProxyModel to facilitate sorting the metdata list
        # QSortFilterProxyModel (or related) seems to be what is causing this following warning:
        # 'Trying to create a QVariant instance of QMetaType::Void type, an invalid QVariant will be constructed instead'
        proxymodel = QSortFilterProxyModel()
        proxymodel.setSourceModel(model)
        proxymodel.setDynamicSortFilter(True)
        proxymodel.setSortCaseSensitivity( Qt.CaseInsensitive )
        # none of these 3 lines appear to have any effect on sorting the metadata list
        #proxymodel.setFilterCaseSensitivity(Qt.CaseInsensitive) 
        #proxymodel.sort(0, Qt.AscendingOrder)  # Qt.DescendingOrder
        #proxymodel.setSortRole(Qt.DisplayRole)
        editor.setModel(proxymodel)
        for ii, (key, value) in enumerate(sorted(dict_.items())):
            model.setItem(ii, 0, QStandardItem(key))
            model.setItem(ii, 1, QStandardItem(str(value)) )
        #QItemDelegate.setEditorData(self, editor, idx)

    def setModelData(self, editor, model, idx):
        # NOT IMPLEMENTED----------------------------------------------
        if editor.objectName() in ['ftype', 'dtype', 'stype', 'fpath', 'UUID']:
            modeldata = idx.data(Qt.DisplayRole)
            dict_ = eval(modeldata)
            newvalue = editor.text()
            dict_[editor.objectName()] = newvalue
            model.setData(idx, str(dict_))
        elif editor.objectName() in ['timestamp']:
            return
        else:
            QItemDelegate.setModelData(self, editor, model, idx)

