"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import os
import sys
module_path = '/home/develop/Projects/src/qwilka' 
if module_path not in sys.path:
    sys.path.append(module_path)  
from utilities.vnlogger import setup_logger
logger = setup_logger(logfile="visinum_messages.log", lvl='INFO',
                                   redir_STOUT=False)
from tree.file_system_tree import make_file_system_tree
from tree.nodes import VnNode
from utilities.database import DbDocFileMetadata, open_database
from utilities.metadata import file_metadata_to_dict, node_metadata_to_db
#import utilities.metadata

datadir = "/home/develop/Downloads/MBES_data/18-F-2824 (SKL22)"
#datadir = "/home/develop/Projects/src/qwilka/visinum/tree"
#path_rel = "/home/develop/Downloads/MBES_data"
##db = FileBackend("/home/develop/Downloads/MBES_data/ttest_db",
##                  {'serializer_class': 'json'} )
#import uuid
##class Metadata(Document):
##    class Meta(Document.Meta):
##        primary_key = 'UUID'
#    def autogenerate_pk(self):
#        #self.pk = self['UUID'] 
#        self.pk = uuid.uuid4().hex

#nn = Metadata({"UUID":"1234abc"} )
#database_path = "/home/develop/Downloads/MBES_data/test_visinumdb"
db = open_database(datadir)


def metadata_from_node(self, path_rel, db):
    # print(self.get_path())
    mdata = file_metadata_to_dict(self.get_path(), path_rel)
    mdata.update(self.get_data())
    node_data = DbDocFileMetadata(mdata )
    ##print(mdata['file_name'], mdata['UUID'], node_data.pk)
    node_data.save(db)


rootNode = make_file_system_tree(datadir, excludedirs=["_VisnumDB"])
print("rootNode=", rootNode.name)
#rootNode.set_data(visinum_type='file_system_tree')

# patch function into tree class
#rootNode.__class__.metadata_from_node = metadata_from_node 
VnNode.metadata_to_db = node_metadata_to_db
#patch_Node(VnNode, node_metadata_to_db)

#with open("test_visiop1.txt", 'w') as fh:
#    fh.write(rootNode.to_texttree())
#with open("test_visiop2.txt", 'w') as fh:
 #   for node in list(rootNode):  fh.write(node.name+'   '+node.get_UUID()+'\n')

for node in list(rootNode):
    node.metadata_to_db(db, datadir)
    #node.metadata_from_node(datadir, db)
    #db.commit()
    #logger.info("Completed processing file %s" % (node.get_path(),))


tree_dict = rootNode.to_vndict()
#tree_dict["UUID"] = "THETREE"
tree_data = DbDocFileMetadata( tree_dict )
tree_data.save(db)
db.commit()

#rootNode.database = database_path
#rootNode.set_data(db=database_path)
rootNode.to_JSON( os.path.join(datadir, "_VisnumDB","filesystemtree.visinum") )

#nm = db.get(DbDocFileMetadata, {'UUID' : 'THETREE'})

#print(make_file_system_tree().to_texttree())
#mdata = file_metadata_to_dict(filename, path_rel)
#for k, v in sorted(mdata.items()):
#    print(k, v)
