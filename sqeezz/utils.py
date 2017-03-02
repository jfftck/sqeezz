from inspect import getargspec, isclass
from itertools import izip

import __builtin__


class FuncUtils(object):
    @staticmethod
    def remove_invalid_kwargs(func, args, kwargs):
        """
        Removes any conflicting keyword arguments by comparing a mapped
        arguments dictionary to the keyword arguments dictionary.

        :param func: callable
        :param args: arguments list/tuple
        :param kwargs: keyword arguments dictionary
        :return: None
        """
        if kwargs:
            spec = FuncUtils.spec(func)
            for key in FuncUtils.create_args_dict(func, args).iterkeys():
                if key in kwargs and spec.keywords is not None:
                    del kwargs[key]

            if spec.keywords is None:
                for key in kwargs.iterkeys():
                    if key not in spec.args:
                        del kwargs[key]

    @staticmethod
    def create_args_dict(func, args):
        """
        Creates a dictionary of arguments based on the parameter variable names
        of a function.

        :param func: callable
        :param args: argument list/tuple
        :return: dictionary of arguments mapped to parameters
        """
        spec_args = FuncUtils.spec(func).args

        return dict(izip(spec_args, args))

    @staticmethod
    def spec(func):
        """
        A wrapper for the inspect.getargspec method.

        :param func: callable
        :return: ArgSpec object
        """
        return getargspec(func)


class ClassUtils(object):
    @staticmethod
    def is_class(cls):
        """
        A wrapper for the inspect.isclass method.

        :param cls: class
        :return: boolean
        """
        return isclass(cls)


def is_callable(obj):
    """
    Private method for checking if an object is callable.

    :param obj: object
    :return: boolean
    """
    _callable = False

    if hasattr(obj, 'callback'):
        if hasattr(__builtin__, 'callable'):
            _callable = callable(obj.callback)
        else:
            _callable = hasattr(obj.callback, '__call__')

    return _callable
