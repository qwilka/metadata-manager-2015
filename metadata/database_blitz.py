"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import logging
import os
logger = logging.getLogger(__name__)

from blitzdb import FileBackend, Document


from tree.file_system_tree import ( FsNode, fstree_from_JSON, 
                  make_file_system_tree, fstree_from_vndict )
from metadata.metadata import node_metadata_to_dict
from utilities.vnuuid import make_uuid


VisinumDB_name  = "_VisnumDB"
metadataDB_name = 'metadataDB'


class DbDocFileMetadata(Document):
    class Meta(Document.Meta):
        primary_key = 'UUID'
        collection  = metadataDB_name


def open_database(db_path):
    if os.path.basename(db_path) != VisinumDB_name:
        db_path = os.path.join(db_path, VisinumDB_name)
    db = FileBackend(db_path, {'serializer_class': 'json'} )
    logger.info("Opening Visinum database %s" % (db_path,))
    return db

def dict_from_DB(db, UUID, DbDocClass=DbDocFileMetadata):
    if UUID:
        dbdoc = db.get(DbDocClass, {'UUID' : UUID})
    return dbdoc.attributes


class VisinumDatabase:
    
    def __init__(self, dbpath, name=VisinumDB_name,
                 DbDocClass=DbDocFileMetadata):  # , attrs={}, **kwargs
        self.DbDocClass = DbDocClass
        self.name = name
        self.open_database(dbpath)  # sets self.dbpath and self.db as reference to database

    def open_database(self, dbpath):  # (self, dbpath, attrs={}, **kwargs)
        if os.path.basename(dbpath) == self.name:
            self.dbpath = dbpath  # opening existing Visinum database
        elif os.path.isdir( os.path.join(dbpath, self.name) ):
            self.dbpath = os.path.join(dbpath, self.name) # opening existing database
            logger.info("Found Visinum database %s in directory %s" % (self.name, dbpath))
        elif os.path.isdir( dbpath ):
            self.dbpath = os.path.join(dbpath, self.name) 
            logger.info("Creating new Visinum database %s in directory %s" % (self.name, dbpath))
        else:
            logger.error("Database path (dbpath) incorrectly specified %s" % (dbpath,))
            raise ValueError("Database path (dbpath) incorrectly specified %s" % (dbpath,))
        self.db = FileBackend(self.dbpath, {'serializer_class': 'json'} )
        logger.info("Opening Visinum database %s" % (self.dbpath,)) 
        config_attrs = self.get_config()
        """try:
            #config_attrs = self.db.get(self.DbDocClass, {'visinum_type' : 'db_config'})
            config_attrs = self.get_config()
        except self.DbDocClass.DoesNotExist:
            self.set_config( {'visinum_type' : 'db_config',
                            'title' : os.path.basename( os.path.dirname(self.dbpath) ),
                            'path_orig' : self.dbpath,
                            'UUID': make_uuid(version=3, namespace='uuid.NAMESPACE_URL', name=self.dbpath)
                            } )
            #config_attrs.update(attrs)
            #self.create_new_item(config_attrs, config_attrs, **kwargs )"""
        self.config_attrs = config_attrs

    def get_config(self, attr=None ):
        try:
            dbitem = self.db.get(self.DbDocClass, {'visinum_type' : 'db_config'})
            config_attrs = dbitem.attributes
        except self.DbDocClass.DoesNotExist:
            try:
                config_UUID = make_uuid(version=3, namespace='uuid.NAMESPACE_URL', name=self.dbpath)
                dbitem = self.db.get(self.DbDocClass, {'UUID' : config_UUID})
                config_attrs = dbitem.attributes
            except self.DbDocClass.DoesNotExist:
                # cannot find db configuration, setup (reset) new configuration
                config_attrs = {'visinum_type' : 'db_config',
                    'title' : os.path.basename( os.path.dirname(self.dbpath) ),
                    'UUID': make_uuid(version=3, namespace='uuid.NAMESPACE_URL', name=self.dbpath),
                    'path_orig' : self.dbpath  }
                self.set_config(config_attrs, reset=True )
                logger.warning("Cannot find db configuration, re-setting configuration %s" % (config_attrs['UUID'],))
        if attr: # if attr and attr in config_attrs:
            return config_attrs[attr]
        return config_attrs


    def set_config(self, attrs={}, reset=False, **kwargs ):
        if reset:
            config_attrs = {}
        else:
            config_attrs = self.get_config()
        config_attrs.update(attrs)
        for k, v in kwargs.items():
            config_attrs[k] = v
        UUID = self.set_dbitem(config_attrs)
        self.config_attrs = config_attrs
        return UUID

        
    def extract_file_metadata(self, dirpath, update=True):
        rootNode = make_file_system_tree(dirpath, excludedirs=[self.name])
        """UUID = self.save_item(rootNode.to_vndict(), {'visinum_type':'datatree',
                               'name':'datatree ' + rootNode.name,
                               'visinum_datatree':'file_system',
                               'visinum_node':rootNode.__class__.__name__,
                               'fpath':dirpath})"""
        rootNode.__class__.metadata_to_dict = node_metadata_to_dict
        for node in list(rootNode):
            mdata = {}
            if update:
                try:
                    dbdoc = self.get_dbitem(node._UUID)
                    mdata.update( dbdoc.attributes )
                    del dbdoc
                except:
                    pass
            mdata.update( node.metadata_to_dict(self.db, dirpath) )
            dbdoc = self.DbDocClass(mdata )
            dbdoc.save(self.db)
            logger.info('Metadata extracted from %s' % (node.get_path(dirpath),) )
        logger.info("Completed processing data tree %s " % (rootNode.name, )) 
        self.db.commit()
        for node in list(rootNode):
            dbdoc = self.db.get(self.DbDocClass, {'UUID' : node._UUID})
            if node is rootNode:
                dbdoc.parent = None
                #dbdoc.visinum_type = 'datatree'
                dbdoc.visinum_datatree = 'file_system'
                #self.set_config(filesystemtreeroot=rootNode._UUID)
                self.set_config(filesystemtreeroot=rootNode._UUID)  # filesystemtreeroot=dbdoc
                ##self.datatreelist.append( ('file system', rootNode._UUID) )
            else:
                #dbdoc.parent = node.parent.UUID
                dbdoc.visinum_parent = self.db.get(self.DbDocClass, {'UUID' : node.parent._UUID})
            dbdoc.visinum_node = node.__class__.__name__
            dbdoc.visinum_childs = []  # database will not accept _childs as a doc attribute
            for child in node._childs:
                #_childs.append(child.UUID)
                dbdoc.visinum_childs.append( self.db.get(self.DbDocClass, {'UUID' : child._UUID}) )
            dbdoc.visinum_nchilds = len(node._childs)
            dbdoc.save(self.db)
        self.db.commit()           
        logger.info("Metadata committed to DB %s" % (rootNode.name, ))

    def set_dbitem(self, attrs={}, commit=True, **kwargs):
        for k, v in kwargs.items():
            attrs[k] = v
        if not 'UUID' in attrs:
            attrs['UUID'] = make_uuid()
        dbItem = self.DbDocClass(attrs )
        dbItem.save(self.db)
        if commit:
            self.db.commit()
        return attrs['UUID']

    def get_dbitem(self, attrs={}, DbDocClass=None):
        if not DbDocClass:
            DbDocClass = self.DbDocClass
        if isinstance(attrs, str):
            attrs = {'UUID' : attrs}
        return self.db.get(DbDocClass, attrs)

    def filter(self, query, DbDocClass=None):
        if not DbDocClass:
            DbDocClass = self.DbDocClass
        return self.db.filter(DbDocClass, query)

    def tree_from_db(self, dbitem, root_node=None, parent=None):
        #dbitem = self.get_dbitem(rootUUID)
        metadata =  dbitem.attributes # {k:v for k, v in dict_.items() if k != "_childs"}
        node = FsNode(metadata['path'], parent=parent, metadata=metadata)
        if not root_node:
            root_node = node
        if 'visinum_childs' in metadata:
            for child in metadata['visinum_childs']:
                self.tree_from_db(child, root_node, node)
        return root_node


if __name__ == '__main__':   # tests
    pass
