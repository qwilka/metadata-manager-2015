"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import logging
import os
import sys
logger = logging.getLogger(__name__)

import pymongo
from bson.objectid import ObjectId

# Import the whole Visinum package, this is necessary because Python3 does not do relative imports:
#module_path = os.path.dirname('/home/develop/Projects/src/qwilka/visinum') 
module_path = os.path.abspath('../../')
if module_path not in sys.path:
    sys.path.append(module_path) 

from visinum.tree.file_system_tree import ( FsNode, fstree_from_JSON, 
                  make_file_system_tree, fstree_from_vndict )

from visinum.metadata.metadata import node_metadata_to_dict    #  fs_to_db
from visinum.metadata.database_mongo import tree_from_db
from visinum.utilities.vnuuid import make_uuid


def fs_to_db(dirpath, dbcoll):
    rootNode = make_file_system_tree(dirpath, excludedirs=['_VisnumDB'])
    #print(rootNode.to_texttree())
    rootNode.__class__.metadata_to_dict = node_metadata_to_dict
    for node in list(rootNode):
        mdata = {}
        mdata.update( node.metadata_to_dict(dirpath) )
        if node is rootNode:
            mdata['fs_parent'] = None
            #mdata['_id'] = os.path.basename(dirpath)  # use the root directory name as _id for the root item
            mdata['_id'] = make_uuid(version=3, namespace='uuid.NAMESPACE_URL', name=dirpath)
            dbcoll.insert(mdata)
            node.visinum_dbid = mdata['_id']
        else:
            mdata['fs_parent'] = node.parent.visinum_dbid
            #node.visinum_dbid = dbcoll.insert_one(mdata).inserted_id  # random ObjectId
            node.visinum_dbid = make_uuid(version=3, namespace='uuid.NAMESPACE_URL', name=node.get_data('path'))
            print(node.name, node.get_data('path'), node.visinum_dbid)
            mdata['_id'] = node.visinum_dbid
            dbcoll.insert_one(mdata)
    for node in list(rootNode):
        if node.count_child() > 0:
            fs_childs = []
            for child in node._childs: 
                fs_childs.append(child.visinum_dbid)
            dbcoll.find_one_and_update({"_id":node.visinum_dbid}, 
                                       {"$set":{"fs_childs":fs_childs}})


def to_jstree(self): 
    """Creates a tree in a form suitable for use with jsTree.
    This function will be patched into the VnNode class, 
    'self' is a node instance. 
    Returns a dictionary, so may need to be wrapped in a list
    for use with jsTree."""
    _dict = {"text":self.name}
    if self._childs:
        _dict['children'] = []
        for child in self._childs:
            dd = child.to_jstree()
            _dict['children'].append(dd)
    return _dict 



if __name__ == '__main__':  
    # datapath is the root directory of the data files 
    datapath = '/home/develop/Downloads/MBES_data/L21_2010-10-25_post-hydrotest'
    #datapath = '/home/develop/Downloads/MBES_data/5pt'
    dataname = os.path.basename(datapath)
    dbhost = pymongo.MongoClient('localhost', 27017)  # port 3001 connects to Meteor DB; MongoDB port is normally 27017
    db = dbhost['visinum']    # set database name
    dbcoll = db['surveyitems']   # set collection name
    dbcoll.delete_many({})   # delete existing items in collection, for testing only
    fs_to_db(datapath, dbcoll)
    rootnode_id = make_uuid(version=3, namespace='uuid.NAMESPACE_URL', name=datapath)
    rootNode = tree_from_db(rootnode_id, dbcoll, treeattr='fs_childs')   # rootNode = tree_from_db(dataname, dbcoll, treeattr='fs_childs')
    print(rootNode.to_texttree(printdata=True)) # prints out the tree in text format
    rootNode.__class__.to_jstree = to_jstree # patch function into VnNode class
    jsTree_list = [rootNode.to_jstree()]  # wrap dictionary returned by to_jstree in a list for jsTree
    #print(jsTree_list)   # print out the whole jsTree list
    #print(jsTree_list[0]['text']) # print out the name/text of the root node
    dbcoll.insert({'_id':'fsdatatree_'+dataname, 
                  'datatree':jsTree_list})  

