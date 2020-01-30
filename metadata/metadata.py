"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
#import functools
#import inspect
import calendar 
import hashlib
import json
import logging
import mimetypes
import os
import pathlib
import subprocess
import tempfile 
import zipfile
logger = logging.getLogger(__name__)


try:
    from PIL import Image as PImage
    from PIL.ExifTags import TAGS
    PIL_imported = True
except:
    PIL_imported = False

try:
    from wand.image import Image as WImage
    wand_imported = True
except:
    wand_imported = False

try:
    import xlrd
    xlrd_imported = True
except:
    xlrd_imported = False

try:
    from wq.io import ExcelFileIO, CsvFileIO  # https://wq.io/wq.io (NOTE: pandas also required)
    wqio_imported = True
except:
    wqio_imported = False

try:
    import pandas
    pandas_imported = True
except:
    pandas_imported = False    

try:
    from utilities.vntime import make_timestamp
    from utilities.vnfunctools import patch_func_into_cls
    from tree.nodes import VnNode 
except SystemError:
    from vntime import make_timestamp
    from vnfunctools import patch_func_into_cls
#    from .nodes import VnNode 



def file_metadata_to_dict(file_path, path_rel=None):
    ppath = pathlib.Path(file_path)
    if not ppath.exists():
        raise AttributeError("cannot locate file %s" % (ppath.as_posix(),))
    ppath = ppath.resolve()
    file_path_ = ppath.as_posix()
    metadata = {}
    metadata["file_name"] = ppath.name
    metadata["file_ext"] = ppath.suffix
    metadata["path_orig"] = file_path_
    if path_rel:
        metadata["path_orig_base"] = path_rel
        metadata["path_rel"] = ppath.relative_to(path_rel).as_posix()
    metadata["file_size"] = os.path.getsize(file_path_)
    metadata["file_atime"] = os.path.getatime(file_path_)
    metadata["file_ctime"] = os.path.getctime(file_path_)
    metadata["file_mtime"] = os.path.getmtime(file_path_)
    if ppath.is_dir():
        metadata["file_type"] = "directory"
        metadata["file_MIME"] = "inode/directory"
    elif ppath.is_file():
        metadata["file_type"] = "file"
        #metadata["file_md5"] = get_file_checksum(file_path_) # too slow for large files?
    if os.name == 'posix':  # platform.system() == 'Linux'
        metadata.update( linux_metadata(file_path_) )
    stats = ppath.stat() # ppath.stat() or os.stat(file_path_) 
    for attr in dir(stats):
        if attr.startswith('st_'):
            metadata[attr] = getattr(stats, attr)
    op = mimetypes.guess_type(ppath.name)[0]
    if op:
        metadata["file_mimetypes_MIME"] = op
    metadata["metadata_timestamp"] = make_timestamp()
    if metadata["file_ext"].lower() in ['.mpg', '.mpeg', '.mp4', '.flv', '.avi', '.wmv', '.blk']:
        metadata.update( video_metadata(file_path_) )
    if metadata["file_ext"].lower() in ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff', '.bmp']:
        metadata.update( image_metadata(file_path_) )
    if metadata["file_ext"].lower() in ['.xls', '.xlsx']:
         metadata.update( excel_metadata(file_path_) )
    if metadata["file_ext"].lower() in ['.txt', '.csv']:
        metadata.update( csv_metadata(file_path_) )
    if ppath.is_file() and zipfile.is_zipfile(file_path_):
        metadata.update( zip_metadata(file_path_) )
    return metadata

# http://stackoverflow.com/questions/27576099/pandas-convert-objectconvert-numeric-true-not-producing-np-nan-for-full-series
def to_float_or_nan(x):
    try:
        return float(x)
    except:  # except (ValueError, TypeError):
        return float('NaN')

def excel_metadata(fpath):
    mdata={}
    if xlrd_imported:
        wb = xlrd.open_workbook(fpath)
        mdata['excel_nsheets'] = wb.nsheets
        mdata['excel_sheet_names'] = wb.sheet_names()
        mdata['excel_user_name'] = wb.user_name
        nrows_ncols = []
        for sheet in wb.sheets():
            nrows_ncols.append( (sheet.nrows, sheet.ncols) )
        mdata['excel_sheet_nrows_ncols'] = nrows_ncols
    if wqio_imported:
        xl = ExcelFileIO(filename=fpath)
        if xl.tabular:
            mdata['excel_field_names'] = xl.field_names
            mdata['table'] = True
            mdata['table_field_names'] = xl.field_names
        else:
            mdata['table'] = False
    if wqio_imported and xl.tabular and pandas_imported:
        print(xl.tabular, fpath)
        #print(xl.field_names)
        df = xl.as_dataframe()
        # df.convert_objects(convert_numeric=True) does not work properly, so workaround:
        # http://stackoverflow.com/questions/27576099/pandas-convert-objectconvert-numeric-true-not-producing-np-nan-for-full-series
        #M = lambda x: x.isdigit()==True # does not work 'numpy.float64' object has no attribute 'isdigit'
        #df[~df.applymap(M)]='NaN'
        #df = df.convert_objects(convert_numeric=True, convert_dates=False, convert_timedeltas=False)
        df = df.applymap(to_float_or_nan)
        print(df)
        for ser in df:
            if any(itm in ser.lower() for itm in ['date', 'time']):
                continue  # bson.errors.InvalidDocument: Cannot encode object: datetime.time(10, 7, 32)
            #if any(itm in ser.lower() for itm in ['kp', 'easting', 'northing', 'adjl', 'adjr', 'msbl', 'msbr']):
            for itm in ['kp', 'easting', 'northing', 'adjl', 'adjr', 'msbl', 'msbr', 'depth', 'top']:
                if itm not in ser.lower():
                    continue
                # ii = df.columns.get_loc(ser)  
                mdata['table_col_'+itm] = {}    
                mdata['table_col_'+itm]['field_name'] = ser
                mdata['table_col_'+itm]['header'] = xl.unmap_field(ser)
                mdata['table_col_'+itm]['max'] = df[ser].max()
                mdata['table_col_'+itm]['min'] = df[ser].min()
                mdata['table_col_'+itm]['mean'] = df[ser].mean()
    return mdata

def csv_metadata(fpath):
    mdata={}
    if wqio_imported:
        csv = CsvFileIO(filename=fpath)
        if csv.tabular:
            mdata['csv_field_names'] = csv.field_names
            mdata['tabular'] = True
            mdata['tabular_field_names'] = csv.field_names
        else:
            mdata['tabular'] = False
    return mdata


def zip_metadata(fpath):
    mdata={}
    mdata['zip'] = True
    return mdata
    # NOT IMPLEMENTED: extract zipped files and index
    with zipfile.ZipFile(fpath, 'r') as zipf:
        mdata['zip_filelist'] = zipf.namelist()
        with tempfile.TemporaryDirectory(prefix=os.path.basename(fpath)) as tmpdirname:
            print('created temporary directory', tmpdirname)
            zipf.extractall(path=tmpdirname)
            for zipobj in zipf.infolist():
                with zipf.open(zipobj) as tmpzfile:
                    zipfilepath = os.path.join(tmpdirname, zipobj.filename)
                    if os.path.isfile(zipfilepath):
                        print("IS A FILE ", zipfilepath)
                    else:
                        print("NOT A FILE ", zipfilepath)
                    #print(dir(zipobj))
                    print(zipobj.filename)
                    print(zipobj.orig_filename)
                    print(zipobj.file_size)
                    print(zipobj.compress_size)
                    print(zipobj.date_time)
                    print(calendar.timegm(zipobj.date_time))
                    print(zipobj.create_system)
                    #mdata['zip_filelist'] = 
                    #print(zipobj.)
            #input("Press Enter to continue...")
    return mdata
    

def linux_metadata(fpath):
    """File metadata using commands available on Linux"""
    mdata={}
    sys_cmds = [ ("file_file_type", ['file', '--brief', fpath] ),   # file_file_type <= file --brief fpath
     ("file_file_MIME", ['file', '--mime-type', '-b', fpath] ),
     ("file_file_encoding", ['file', '--mime-encoding', '-b', fpath] ) ]
    for k, cmdli in sys_cmds:
        try:
            # running subprocess.check_output to check for exception, however this returns bytes
            op = subprocess.check_output(cmdli)
        except:
            logger.warning("Metadata '%s'; system command failure '%s'" % (k, " ".join(cmdli)))
        else:
            #metadata[k] = subprocess.getoutput(cmd) # returns str
            # avoid running system call twice, so must convert bytes
            mdata[k] = op.decode(encoding='UTF-8').strip()
    return mdata


def video_metadata(fpath):
    try:  # avprobe -v 0 -show_format -of json fpath
        op = subprocess.check_output(['avprobe','-v', '0', '-show_format', '-of', 'json', fpath ])
    except:
        logger.warning("avprobe failure for file '%s'" % (fpath,))
        return {}
    op = op.decode(encoding='UTF-8').strip()
    mdata = {}
    dict_ = json.loads(op)
    dict_ = dict_['format']
    for k, v in dict_.items():
        mdata['video_avprobe_'+k] = v
    try:   # avprobe -v 0 -show_streams -of json fpath
        op = subprocess.check_output(['avprobe','-v', '0', '-show_streams', '-of', 'json', fpath ])
    except:
        pass
    else:
        op = op.decode(encoding='UTF-8').strip()
        dict_ = json.loads(op)
        for ii, stream in enumerate(dict_['streams']):
            for k, v in stream.items():
                mdata['video_avprobe_stream{}_{}'.format(ii, k)] = v 
    return mdata


def image_metadata(fpath):
    mdata = {}
    if PIL_imported:
        with PImage.open(fpath) as img:
            #img = PImage.open(fpath)
            img_attrs = ['bits', 'filename', 'format', 'format_description', 'size', 'mode', 'layers'] # 'app', 'info', 
            for attr in img_attrs:
                value = getattr(img, attr, None)
                if value:
                    mdata['image_PIL_'+attr] = value
    if wand_imported:
        with WImage(filename=fpath) as img:
            img_attrs = ['compression', 'compression_quality', 'depth','format', 'resolution', 'signature', 'size', 'type'] 
            for attr in img_attrs:
                value = getattr(img, attr, None)
                if value:
                    mdata['image_wand_'+attr] = value
            for k, v in img.metadata.items():  # read EXIF metadata
                mdata['image_wand_'+k] = v
    return mdata


'''
def node_metadata_to_dict(node, db, path_rel=None, nodedata=True):
    mdata = file_metadata_to_dict(node.get_path(), path_rel)
    if nodedata: # include node data (over-ridding file metadata where duplicated)
        mdata.update(node.get_data())
    return mdata
'''

# node_metadata_to_dict2
def node_metadata_to_dict(node, path_rel=None, nodedata=True):  # removed arg 'db'
    mdata = file_metadata_to_dict(node.get_path(), path_rel)
    if nodedata: # include node data (over-ridding file metadata where duplicated)
        mdata.update(node.get_data())
    return mdata


def get_op_sys_cmd(cmdstr, dict_=None, itemkey=None):
    try:
        op = subprocess.getoutput(cmdstr)
    except:
        return False
    if isinstance(dict_, dict) and isinstance(itemkey, str):
        dict_[itemkey] = op
        return True
    return op


def get_file_checksum(filename, blocksize=65536, alg='md5'):
    #http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
    if alg.upper() in ('SHA1', 'SHA-1'):
        hash = hashlib.sha1()
    else:
        hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()


'''
def fs_to_db(dirpath, dbcoll):
    rootNode = make_file_system_tree(dirpath)
    print(rootNode.to_texttree())
    rootNode.__class__.metadata_to_dict = node_metadata_to_dict2
    for node in list(rootNode):
        mdata = {}
        mdata.update( node.metadata_to_dict(dirpath) )
        if node is rootNode:
            mdata['fs_parent'] = None
            mdata['_id'] = os.path.basename(dirpath)
            dbcoll.insert(mdata)
            node.visinum_dbid = mdata['_id']
        else:
            mdata['fs_parent'] = node.parent.visinum_dbid
            node.visinum_dbid = dbcoll.insert_one(mdata).inserted_id
    for node in list(rootNode):
        if node.count_child() > 0:
            fs_childs = []
            for child in node._childs: 
                fs_childs.append(child.visinum_dbid)
            dbcoll.find_one_and_update({"_id":node.visinum_dbid}, 
                                       {"$set":{"fs_childs":fs_childs}})
'''


if __name__ == '__main__':
    # this is necessary because of Python3's messed-up import system:
    import sys
    module_path = os.path.dirname('/home/develop/Projects/src/qwilka/visinum') #
    if module_path not in sys.path:
        sys.path.append(module_path) 
    from database import VisinumDatabase
    dirpath='/home/develop/Downloads/MBES_data/18-F-2824 (SKL22)'
    db = VisinumDatabase(dirpath)
    db.extract_file_metadata(dirpath)

