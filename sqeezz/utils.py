from inspect import getargspec
from itertools import izip


class FuncTools(object):
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
            spec = FuncTools.spec(func)
            for key in FuncTools.create_args_dict(func, args).iterkeys():
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
        spec_args = FuncTools.spec(func).args

        return dict(izip(spec_args, args))

    @staticmethod
    def spec(func):
        """
        A wrapper for the inspect.getargspec function.

        :param func: callable
        :return: ArgSpec object
        """
        return getargspec(func)
