"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import os
import re
import sys

valid_identifier = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def to_str(ip, strip=False):
    if isinstance(ip, bytes):
        op = ip.decode(encoding='UTF-8')
    elif isinstance(ip, str):
        op = ip
    else:
        return None
    if strip:
        op = op.strip()
    return op


def identify_number(strg):
    if type(strg).__name__ in ("float", "int"):
        return type(strg).__name__
    try:
        float(strg)
        strg_type = "float"
        if strg[0] in ("+", "-"):
            strg = strg[1:]
        if strg.isdigit():
            strg_type = "int"
        return strg_type
    except ValueError:
        return "str"


def args_into_func(func, **args): 
    '''Assign a dictionary of keyword arguments to a function
    Ref: http://stackoverflow.com/questions/817087/call-a-function-with-argument-list-in-python
    '''
    return func(**args)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False



def traverse_tree(dic, func=None, level=0):
    # http://stackoverflow.com/questions/380734/how-to-do-this-python-dictionary-traverse-and-search
    # http://stackoverflow.com/questions/12399259/finding-the-level-of-recursion-call-in-python
    for key, value in dic.items():
        if func:
            func(key)
        else:
            print(key, level)
        if value and type(value).__name__ == 'dict':
            traverse_tree(value, func, level=level+1)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS) # optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

