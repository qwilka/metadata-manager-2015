"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import os
import unittest
from nodes import Node, vntree_from_vndict
from file_system_tree import make_file_system_tree

class TestNodes(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_setup_basic_Node_tree(self):
        rootnode   = Node("root (level0)")
        node1 = Node("node1 (level1)", rootnode)
        Node("node2 (level2)", node1)
        Node("node8 (level2)", node1)
        node3 = Node("node3 (level1)", rootnode)
        Node("node7 (level1)", rootnode)
        Node(parent=rootnode)
        node4 = Node(parent=node3, name="node4 (level2)")
        node5 = Node("node5 (level3)", node4)
        Node("node6 (level4)", node5)
        test_tree_string = """|---root (level0)
.   |---node1 (level1)
.   .   |---node2 (level2)
.   .   |---node8 (level2)
.   |---node3 (level1)
.   .   |---node4 (level2)
.   .   .   |---node5 (level3)
.   .   .   .   |---node6 (level4)
.   |---node7 (level1)
.   |---nameless node\n"""
        self.assertEqual( rootnode.to_texttree(), test_tree_string)

    def test_VnNode_tree_from_dictionary(self):
        # NOTE all items in dict_ must have attribute "name" defined
        # because VnNode assigns a default name to nameless nodes
        dict_ = {"name":"TopLevel-notroot", "number":123,
        "_childs":[
        {"name":"child10"},
        {"name":"child20"},
        {"name":"child1", "anumber":321}, 
        {"name":"child2"}, 
        {"name":"child3", 
        "_childs":[
        {"name":"child4"}, 
        {"name":"child5"}]} 
        ],
        "child1" : {"name":"childone"},   
        "child2" : {"name":"childtwo", "again":{"name":"thegrandchildren"}}
        }
        rootnode = vntree_from_vndict(dict_)
        self.assertDictEqual( dict_, rootnode.to_vndict())

    def test_make_file_system_tree(self):
        parentdir = os.path.dirname(os.getcwd()) # this file not in root directory
        dict_ = make_file_system_tree(parentdir).to_vndict()
        self.assertIsInstance(dict_, dict)
        self.assertIn("name", dict_)
        self.assertEqual( dict_["name"], os.path.basename( parentdir ) )
        filelist = os.listdir( parentdir )
        self.assertIn("_childs", dict_)
        self.assertEqual( len(dict_["_childs"]), len(filelist) )
        for child in dict_["_childs"]:
            self.assertIn(child["name"], filelist)
            filepath = os.path.join(parentdir, child["name"])
            if os.path.isdir( filepath ):
                if "_childs" in child: # files in directory 
                    self.assertEqual( len(child["_childs"]), 
                                          len(os.listdir( filepath )) )
                else:  # directory is empty
                    self.assertEqual( len(os.listdir( filepath )), 0)
            else:
                self.assertNotIn("_childs", child)
        


if __name__ == '__main__':
    unittest.main()
