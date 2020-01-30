"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import uuid

# http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
# As a precaution, do not import os, sys into this module


def make_uuid(version=4, **kwargs):
    if version==1: 
        if "node" in kwargs:
            node = kwargs["node"]
        else:
            node = None
        if "clock_seq" in kwargs:
            clock_seq = kwargs["clock_seq"]
        else:
            clock_seq = None
        return uuid.uuid1(node, clock_seq).hex
    elif version in (3, 5): 
        # Warning: UUID is repeatable and potentially not unique. 
        if "namespace" in kwargs:
            namespace = eval(kwargs["namespace"]) # Eval really is dangerous
        else:
            namespace = uuid.NAMESPACE_URL
        if "name" in kwargs:
            name = kwargs["name"]
        else: 
            name = str(uuid.getnode()) # for the want of something better...
        if version==3:
            return uuid.uuid3(namespace, name).hex
        elif version==5:
            return uuid.uuid5(namespace, name).hex
    else: # Default is version=4, random UUID, most likely to be unique
        return uuid.uuid4().hex



if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS) # optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

