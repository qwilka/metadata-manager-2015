"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import functools
import inspect
import logging

logger = logging.getLogger(__name__)


def patch_func_into_cls(cls, func, **kwargs):
    apply_kwargs = {}
    for func_arg in inspect.getargspec(func).args:
        if func_arg in kwargs:
            apply_kwargs[func_arg]=kwargs[func_arg]
    if apply_kwargs:
        # WARNING: functools.partial does not 'curry' **apply_kwargs below,
        # to be safe use keywords args only with func_to_patch for 
        # arguments following first arg ( node/self )
        # http://stackoverflow.com/questions/24755463/functools-partial-wants-to-use-a-positional-argument-as-a-keyword-argument
        func_to_patch = functools.partial(func, **apply_kwargs)
    else:
        func_to_patch = func
    # WARNING: assuming no super-class nodes in tree!
    setattr(cls, func.__name__, func_to_patch)
    logger.debug("Patching function %s into class %s with keyword arguments %s"
                % (func.__name__, cls.__name__, apply_kwargs))


def tryto_curry_node_with_args(rootNode, func, **kwargs):
    apply_args = []
    apply_kwargs = {}
    #func_args = inspect.getargspec(func).args
    for ii, func_arg in enumerate(inspect.getargspec(func).args):
        if func_arg in kwargs:
            if ii==len(apply_args):
                apply_args.append(kwargs[func_arg])
            else:
                apply_kwargs[func_arg]=kwargs[func_arg]
    """for ii, (kwarg, value) in enumerate(kwargs.items()):
        if kwarg not in func_args:
            continue
        if ii == func_args.index(kwarg):
            apply_args.append(value)
        else:
            apply_kwargs[kwarg]=value"""
    print("func_args=", inspect.getargspec(func).args)
    print("apply_args=", apply_args)
    print("apply_kwargs=", apply_kwargs)
    if apply_args or apply_kwargs:
        # WARNING: functools.partial does not 'curry' **apply_kwargs below,
        # to be safe use keywords args only with func_to_patch
        # http://stackoverflow.com/questions/24755463/functools-partial-wants-to-use-a-positional-argument-as-a-keyword-argument
        #func_to_patch = functools.partial(func, **apply_kwargs)
        func_to_patch = functools.partial(func, *apply_args, **apply_kwargs)
    else:
        func_to_patch = func
    # WARNING: assuming no super-class nodes in tree!
    setattr(rootNode.__class__, func.__name__, func_to_patch)



if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS) # optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

