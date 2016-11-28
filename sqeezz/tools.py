from inspect import getargspec
from itertools import izip


class FuncTools(object):
    @staticmethod
    def remove_dup_kwargs(func, args, kwargs):
        """
        This method will remove any conflicting keyword arguments by comparing
        a mapped arguments dictionary to the keyword arguments dictionary.

        :param func: function
        :param args: arguments list/tuple
        :param kwargs: keyword arguments dictionary
        :return: None
        """
        if not kwargs:
            return

        for key in FuncTools.create_args_dict(func, args).iterkeys():
            if key in kwargs:
                del kwargs[key]

    @staticmethod
    def create_args_dict(func, args):
        spec_args = FuncTools.spec(func).args

        return dict(izip(spec_args, args))

    @staticmethod
    def spec(func):
        return getargspec(func)