"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import json
import logging
import os

logger = logging.getLogger(__name__)

def to_JSON(filepath, obj_):
    with open(filepath, 'w') as jfile:
        json.dump(obj_, jfile)


def from_JSON(filepath):
    with open(filepath, 'r') as jfile:
        obj_ = json.load(jfile)
    return obj_


def attrs_to_JSON(filepath, datadict=None, **kwargs):
    if os.path.isfile(filepath):
        jsondata = from_JSON(filepath)
    else:
        jsondata = {}
    if not isinstance(jsondata, dict):
        logger.debug("Data in file %s not a dictionary" % (filepath,))
        return False
    if datadict and isinstance(datadict, dict):
        jsondata.update(datadict)
    for k, v in kwargs.items():
        jsondata[k] = v
    to_JSON(filepath, jsondata)
    return True


def attr_from_JSON(filepath, attr_name):
    json_ = from_JSON(filepath)
    if not isinstance(json_, dict):
        logger.debug("Data in file %s not a dictionary" % (filepath,))
        return False
    if attr_name in json_:
        return json_[attr_name]
    else:
        return None


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS) # optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
