"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
from PyQt5.QtWidgets import QTreeView, QDataWidgetMapper
from PyQt5.QtCore import pyqtSignal

from .models import VnTreeModel, FsTreeModel
#from .file_system_tree import FsTreeModel


class VnTreeView(QTreeView):
    tree_clicked = pyqtSignal(str)
    def __init__(self, parent=None, treerootNode=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.rootIsDecorated = True
        #self.setup_treemodel(treerootNode)

    def setup_treemodel(self, treerootNode=None, treetype='FsTree'):
        if treetype=='FsTree':
            treemodel = FsTreeModel(treerootNode)
        else:
            treemodel = VnTreeModel(treerootNode)
        self.setModel(treemodel)
        self.dataMapper = QDataWidgetMapper()
        self.dataMapper.setModel(treemodel)


if __name__ == "__main__":
    pass
