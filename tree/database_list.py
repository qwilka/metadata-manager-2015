"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


from tree.models import VnTreeModel

class DBtreeW(QWidget):
    
    def __init__(self, parent=None, dblist=None):
        super().__init__(parent)
        self.setStyleSheet("background-color:red;")
        self.dbtreeview = DBTreeView(self, dblist)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.dbtreeview)
        self.setLayout(layout)
        self.setVisible(True)


class DBTreeView(QTreeView):

    def __init__(self, parent=None, dblist=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.clicked.connect(self.on_tree_clicked)

        model = QStandardItemModel(0, 1)
        self.setModel(model)
        if dblist:
            self.update_dblist(dblist)

    def update_dblist(self, dblist=None):
        if not dblist:
            dblist = self.window().dblist
        model = self.model()
        model.clear()
        invRoot = model.invisibleRootItem()
        for ii, db in enumerate(dblist):
            #dbtitle = getattr(dblist[ii], 'title', dblist[ii].name)
            #model.setItem(ii, 0, QStandardItem(dbtitle))
            #print(dblist[ii].config_attrs)
            #print(getattr(dblist[ii].config_attrs, 'title', dblist[ii].name))
            dbitem = QStandardItem( dblist[ii].config_attrs.get('title', dblist[ii].name) )
            dbitem.setData( (ii, 'db', ''), Qt.UserRole )
            invRoot.appendRow(dbitem)
            subitem = QStandardItem("list all items in database")
            subitem.setData( (ii, 'list', ''), Qt.UserRole )
            dbitem.appendRow(subitem)
            subitem = QStandardItem('file system tree')
            if 'filesystemtreeroot' in db.config_attrs:
                UUID = db.config_attrs['filesystemtreeroot']
                subitem.setData( (ii, 'filesystemtree', UUID), Qt.UserRole )
                dbitem.appendRow(subitem)
            """for title, UUID in db.datatreelist:
                subitem = QStandardItem(title)
                subitem.setData( (ii, 'datatree', UUID), Qt.UserRole )
                dbitem.appendRow(subitem)"""

    def on_tree_clicked(self, idx):
        data_ = self.model().data(idx, Qt.UserRole)
        mainwindow = self.window()
        dblist = mainwindow.dblist
        db = dblist[data_[0]]
        if data_[1] == 'list':
            mainwindow.datatreeTV.setModel(QStandardItemModel(0, 1))
            datatreemodel = mainwindow.datatreeTV.model()
            invRoot = datatreemodel.invisibleRootItem()
            dbitems = db.filter({})
            #dbitems = sorted(dbitems) # TypeError: unorderable types: DbDocFileMetadata() < DbDocFileMetadata()
            for ii, item in enumerate(dbitems):
                itemname = getattr(item, 'name', 'no name item')
                print(ii, itemname)
                invRoot.appendRow( QStandardItem( itemname ) )
        if data_[1] == 'filesystemtree':
            print(data_[2])
            db = dblist[data_[0]]
            dbitem = db.get_dbitem(data_[2])  # get tree root from db using its UUID
            treenodes = db.tree_from_db(dbitem)
            mainwindow.datatreeTV.setup_treemodel(treenodes)
            #model = VnTreeModel(treenodes)
            mainwindow.metdatalist.setupDataMapper(mainwindow.datatreeTV)
            #mainwindow.datatreeTV.setModel(model)
            #mainwindow.datatreeTV.dataMapper.setModel(model)
        #print("data= {} {} {} {}".format(type(data_[0]), *data_))
        

#class DBTreeModel(QStandardItemModel):
#    def __init__(self, parent=None):
#        super().__init__(parent)

     
