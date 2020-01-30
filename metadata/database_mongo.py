"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import logging
import os
logger = logging.getLogger(__name__)

import pymongo
from bson.objectid import ObjectId

from visinum.tree.nodes import VnNode


#dbhost = pymongo.MongoClient('localhost', 3001)  # 27017
#db = dbhost['test_database']     # dbhost.meteor  'test_database'
#testcollection = db['posts']    # db.posts   


class MnNode(VnNode):
    """Node class adapted for creating a tree from items in a MongoDB."""
    def __init__(self, _id, name=None,  parent=None, metadata=None):
        super().__init__(name, parent, metadata)
        self._id = _id
        


def tree_from_db(item_id, dbcoll, treeattr, root_node=None, parent=None):
    #_dict= dbcoll.find_one({"_id":root_id})
    #print(_dict)
    curs= dbcoll.find({"_id":item_id})
    if curs.count()>1:
        logger.warning("Duplicate items with _id %s in collection %s" % (item_id, dbcoll))
    _dict = list(curs)[0]
    #print(dir(curs))
    #print(list(curs))
    #if isinstance(item_id, ObjectId):
    #    item_name = str()
    #node = VnNode(name=str(item_id), parent=parent, metadata={'name':_dict['name']})
    #node = MnNode(str(item_id), name=_dict['name'], parent=parent)
    node = VnNode(name=_dict['name'], parent=parent, metadata={'mongodb_id':str(item_id)})
    if not root_node:
        root_node = node
    if treeattr in _dict:
        for child_id in _dict[treeattr]:
            tree_from_db(child_id, dbcoll, treeattr, root_node=root_node, parent=node)
    return root_node


if __name__ == '__main__':  
    import datetime
    item = {"author": "SMcE",
            "text": "Another test item",
            "tags": ["mongodb", "python", "visinum"],
            "date": datetime.datetime.utcnow()}
    dbhost = pymongo.MongoClient('localhost', 3001)  # 27017
    db = dbhost['test_database']     # dbhost.meteor  'test_database'
    testcollection = db['testitems']            
    uid = testcollection.insert_one(item).inserted_id
    print(db.collection_names(include_system_collections=False))
    print(testcollection.find_one())
    new_items = [{"author": "SMcE",
            "text": "tes bulk insert",
            "tags": ["bulk", "insert"],
            "date": datetime.datetime(2009, 11, 12, 11, 14)},
            {"author": "Eliot",
            "title": "MongoDB is fun",
            "text": "and pretty easy too!",
            "date": datetime.datetime(2009, 11, 10, 10, 45)}]
    result = testcollection.insert_many(new_items)
    print(result.inserted_ids)
    for item in testcollection.find():
        print(item)
