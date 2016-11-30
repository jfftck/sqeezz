import __builtin__
import threading

from libs.decorator import decorate
from tools import FuncTools


class _Type(FuncTools):
    """
    Stores the @static_type decorator values and extends the FuncTools.
    """
    def __init__(self, args, kwargs):
        """
        Store the arguments and keyword arguments.

        :param args: list/tuple of arguments
        :param kwargs: dictionary of keyword arguments
        """
        self.args = args
        self.kwargs = kwargs


class Call(FuncTools):
    """
    Designed to hold a callable with default arguments and will remove extra
    arguments that would cause an error. It also replaces the default arguments
    with the arguments given when it is called.

    If you want something like functools.partial then you can structure the
    function like this:

    def func(arg1, arg2, **kwargs):
        ...

    Then use the Call object like this:

    Call(func, arg3='some value')

    Now when it is called it will have the third argument in the keywords:

    kwargs['arg3'] # <-- This will have your value.
    """
    def __call__(self, *args, **kwargs):
        """
        Arguments supplied will replace the arguments given during
        instantiation. The order of preference from highest to lowest is call
        arguments, call keyword arguments, instantiation arguments,
        instantiation keyword arguments.

        :param args: varargs
        :param kwargs: keywords
        :return: the stored callable's return value
        """
        mapped_args = self.create_args_dict(self.__call, self.args)
        mapped_passed_args = self.create_args_dict(self.__call, args)
        copy_kwargs = self.kwargs.copy()

        copy_kwargs.update(mapped_args)
        copy_kwargs.update(kwargs)
        copy_kwargs.update(mapped_passed_args)

        self.remove_invalid_kwargs(self.__call, [], copy_kwargs)

        return self.__call(**copy_kwargs)

    def __init__(self, call, *args, **kwargs):
        """
        Store the callable and the default arguments and keyword arguments.

        :param call: callable
        :param args: varargs
        :param kwargs: keywords
        """
        self.__call = call
        self.args = args
        self.kwargs = kwargs


class Data(object):
    """
    Creates a wrapper for a file-like object to use with the 'with' statement.

    It has three (3) callback methods:
    1. On instantiation, this is the main function and must return the
       file-like object.
    2. On exit, this is called before closing the file-like object.
    3. On exception, this allows you to act on exceptions.
    """
    def __enter__(self):
        """
        This will store and return the file-like object that the main
        function returns.

        :return: file-like object
        """
        self.__open_command = self.__enter()

        return self.__open_command

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        This will close the file-like object even on error.

        Has two (2) callbacks to handle exceptions and acting on the file-like
        object just before closing it. This is useful for databases.

        :param exc_type: exception type
        :param exc_val: exception value
        :param exc_tb: exception traceback
        :return: None
        """
        execute_exit = True

        if self.__is_callable(self.__exception) and exc_type:
            execute_exit = self.__exception((exc_type, exc_val, exc_tb),
                                            self.__open_command)

        if execute_exit and self.__is_callable(self.__exit):
            self.__exit(self.__open_command,
                        *self.__exit.spec_args,
                        **self.__exit.kwargs)

        self.__open_command.close()

    def __init__(self, callback, *args, **kwargs):
        """
        Takes a callback and arguments to be used when called with the 'with'
        statement.

        :param callback: a callable
        :param args: varargs
        :param kwargs: keywords
        """
        self.__enter = Call(callback, args, kwargs)
        self.__exception = None
        self.__exit = None
        self.__open_command = None

    @staticmethod
    def __is_callable(obj):
        """
        Private method for checking if an object is callable.

        :param obj: an object
        :return: boolean
        """
        is_callable = False

        if hasattr(obj, 'callback'):
            if hasattr(__builtin__, 'callable'):
                is_callable = callable(obj.callback)
            else:
                is_callable = hasattr(obj.callback, '__call__')

        return is_callable

    def exception(self, callback):
        """
        Sets the exception callback.

        :param callback: a callable
        :return: self
        """
        self.__exception = Call(callback)

        return self

    def exit(self, callback, *args, **kwargs):
        """
        Sets the callback to call before closing the file-like object.

        :param callback: a callable
        :param args: varargs
        :param kwargs: keywords
        :return: self
        """
        self.__exit = Call(callback, args, kwargs)

        return self


class File(Data):
    """
    A wrapper for the open function that allows you to store the arguments
    without opening the file.
    """
    def __init__(self, path, file_command=open, *args, **kwargs):
        """
        Stores the file path, function, and arguments.

        :param path: string of the file path
        :param file_command: a callable (default: open)
        :param args: varargs
        :param kwargs: keywords
        """
        self.__path = path
        self.__file_command = file_command
        super(File, self).__init__(self.__open, args, kwargs)

    def __open(self, args, kwargs):
        """
        Private method that calls the callback function and returns the
        file-like object.

        :param args: list/tuple of arguments
        :param kwargs: dictionary of keyword arguments
        :return: file-like object
        """
        return self.__file_command(self.__path, *args, **kwargs)

    def open(self, *args, **kwargs):
        """
        Allows the File object to be used without the 'with' statement.

        !!! Warning !!!
        You must handle closing the file-like object yourself.

        :param args: varargs
        :param kwargs: keywords
        :return: file-like object
        """
        return self.__open(args, kwargs)


class Singleton(object):
    """
    Creates a wrapper around an object to make it a singleton.
    """
    def __call__(self, *args, **kwargs):
        """
        Calls the instance with the provided arguments.

        :param args: varargs
        :param kwargs: keywords
        :return: object
        """
        with threading.RLock():
            self.__create_instance()
            return self.__instance(*args, **kwargs)

    def __getattr__(self, name):
        """
        Get the instance attribute.

        :param name: string
        :return: method/attribute from the instance
        """
        with threading.RLock():
            self.__create_instance()
            return getattr(self.__instance, name)

    def __init__(self, cls, *args, **kwargs):
        """
        Store the class and the instantiation arguments.

        :param cls: object
        :param args: varargs
        :param kwargs: keywords
        """
        with threading.RLock():
            self.__cls = Call(cls, args, kwargs)
            self.__instance = None

    def __setattr__(self, name, value):
        """
        Set the instance attribute.

        :param name: string
        :param value: object
        :return: None
        """
        with threading.RLock():
            self.__create_instance()
            setattr(self.__instance, name, value)

    def __create_instance(self):
        """
        Create the instance if it is not instantiated.

        :return: None
        """
        if self.__instance is None:
            with threading.RLock():
                self.__instance = self.__cls()

    def instance(self):
        """
        Direct access to the instance object.

        This is useful for using any of the magic methods, like __add__, that
        the object supports.

        The Singleton object does not override any of the magic methods.

        :return: object
        """
        return self.__instance


def _strict_type(s_type, allow_none):
    """
    Private function for the strict_type decorator.

    :param s_type: _Type object
    :return: function
    """
    def _inner(func, *args, **kwargs):
        """
        Private function that is used for the strict_type decorator.
        """
        args = list(args)
        mapped_args = s_type.create_args_dict(func, args)
        s_type.kwargs.update(s_type.create_args_dict(func, s_type.args))

        def check_type(name, arg_value, required_type):
            """
            Private function for checking type and raising a TypeError if not
            matching.
            """
            not_type = not isinstance(arg_value, required_type)
            not_none = allow_none and (not_type or arg_value is not None)
            strict_not_type = not allow_none and not_type

            if strict_not_type or not_none:
                raise TypeError('{} is {} and not of type {}'.format(
                        name, repr(arg_value), required_type))

        for key, value in s_type.kwargs.iteritems():
            if key in kwargs:
                check_type(key, kwargs[key], value)

            if key in mapped_args:
                check_type(key, mapped_args[key], value)

        return func(*args, **kwargs)
    return _inner


def singleton(cls):
    """
    Class decorator the wraps the provided class in the singleton class.

    :param cls: class
    :return: Singleton object
    """
    return Singleton(cls)


def strict_type(allow_none, *args, **kwargs):
    """
    Function/method decorator that raises a TypeError exception when the
    arguments don't have a matching type to the ones provided.

    :param allow_none: boolean
    :param args: varargs
    :param kwargs: keywords
    :return: decorator function
    """
    def _inner(func):
        """
        Private decorator function.
        """
        return decorate(func, _strict_type(_Type(args, kwargs), allow_none))

    return _inner