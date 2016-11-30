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

        :param args: argument list/tuple
        :param kwargs: keyword argument dictionary
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
    def __enter__(self):
        self.__open_command = self.__enter()

        return self.__open_command

    def __exit__(self, exc_type, exc_val, exc_tb):
        execute_exit = True

        if self.__is_callable(self.__error) and exc_type:
            execute_exit = self.__error((exc_type, exc_val, exc_tb),
                                        self.__open_command)

        if execute_exit and self.__is_callable(self.__exit):
            self.__exit(self.__open_command,
                        *self.__exit.spec_args,
                        **self.__exit.kwargs)

        self.__open_command.close()

    def __init__(self, callback, *args, **kwargs):
        self.__enter = Call(callback, args, kwargs)
        self.__error = None
        self.__exit = None
        self.__open_command = None

    @staticmethod
    def __is_callable(obj):
        is_callable = False

        if hasattr(obj, 'callback'):
            if hasattr(__builtin__, 'callable'):
                is_callable = callable(obj.callback)
            else:
                is_callable = hasattr(obj.callback, '__call__')

        return is_callable

    def error(self, callback):
        self.__error = Call(callback)

        return self

    def exit(self, callback, *args, **kwargs):
        self.__exit = Call(callback, args, kwargs)

        return self


class File(Data):
    def __init__(self, path, file_command=open, *args, **kwargs):
        self.__path = path
        self.__file_command = file_command
        super(File, self).__init__(self.__open, *args, **kwargs)

    def __open(self, *args, **kwargs):
        return self.__file_command(self.__path, *args, **kwargs)

    def open(self, *args, **kwargs):
        return self.__open(*args, **kwargs)


class Singleton(object):
    def __call__(self, *args, **kwargs):
        with threading.RLock():
            self.__create_instance()
            return self.__instance(*args, **kwargs)

    def __getattr__(self, name):
        with threading.RLock():
            self.__create_instance()
            return getattr(self.__instance, name)

    def __init__(self, cls, *args, **kwargs):
        with threading.RLock():
            self.__cls = Call(cls, args, kwargs)
            self.__instance = None

    def __setattr__(self, name, value):
        with threading.RLock():
            self.__create_instance()
            setattr(self.__instance, name, value)

    def __create_instance(self):
        if self.__instance is None:
            with threading.RLock():
                self.__instance = self.__cls()

    def instance(self):
        return self.__instance


def _type(_strict_type):
    def _inner(func, *args, **kwargs):
        args = list(args)
        mapped_args = _strict_type.create_args_dict(func, args)
        _strict_type.kwargs.update(_strict_type.create_args_dict(func, _strict_type.args))

        for key, value in _strict_type.kwargs.iteritems():
            if key in kwargs:
                if not isinstance(kwargs[key], value):
                    raise TypeError('{} is {} and not of type {}'.format(
                            key, repr(kwargs[key]), value))

            if key in mapped_args:
                if not isinstance(mapped_args[key], value):
                    raise TypeError('{} is {} and not of type {}'.format(
                            key, repr(mapped_args[key]), value))

        return func(*args, **kwargs)
    return _inner


def singleton(cls):
    return Singleton(cls)


def strict_type(*args, **kwargs):
    def __type(func):
        return decorate(func, _type(_Type(args, kwargs)))

    return __type
