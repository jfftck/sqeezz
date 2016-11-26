import threading
import __builtin__
from inspect import getargspec
from itertools import izip
from sqeezz import decorate


class _Common(object):
    def remove_dup_args(self, func, args, kwargs):
        for key in self.create_args_dict(func, args).iterkeys():
            if key in kwargs:
                del kwargs[key]

    @staticmethod
    def create_args_dict(func, args):
        spec = getargspec(func)
        return dict(izip(spec.args, args))


class Call(_Common):
    def __init__(self, call, *args, **kwargs):
        self.__call = call
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        args += self.args
        kwargs.update(self.kwargs)

        self.remove_dup_args(self.__call, args, kwargs)

        return self.__call(*args, **kwargs)


class Data(object):
    def __init__(self, callback, *args, **kwargs):
        self.__enter = Call(callback, args, kwargs)
        self.__error = None
        self.__exit = None
        self.__open_command = None

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
                        *self.__exit.args,
                        **self.__exit.kwargs)

        self.__open_command.close()

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
    def __init__(self, cls, *args, **kwargs):
        with threading.RLock():
            self.__cls = Call(cls, args, kwargs)
            self.__instance = None

    def __call__(self, *args, **kwargs):
        self.__create_instance()
        return self.__instance(*args, **kwargs)

    def __getattr__(self, name):
        self.__create_instance()
        return getattr(self.__instance, name)

    def __setattr__(self, name, value):
        self.__create_instance()
        setattr(self.__instance, name, value)

    def __create_instance(self):
        if self.__instance is None:
            with threading.RLock():
                self.__instance = self.__cls()

    def instance(self):
        return self.__instance


class _Type(_Common):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


def _type(func, *args, **kwargs):
    args = list(args)
    _strict_type = args.pop()
    mapped_args = _strict_type.create_args_dict(func, args)
    _strict_type.kwargs.update(_strict_type.create_args_dict(func, _strict_type.args))

    for key, value in _strict_type.kwargs.iteritems():
        if key in kwargs:
            if not isinstance(kwargs[key], value):
                raise TypeError('{} is not of type {}'.format(
                        repr(kwargs[key]), value))

        if key in mapped_args:
            if not isinstance(mapped_args[key], value):
                raise TypeError('{} is not of type {}'.format(
                        repr(mapped_args[key]), value))

    return func(*args, **kwargs)


def strict_type(*args, **kwargs):
    def __type(func):
        return decorate(func, Call(_type, _Type(args, kwargs)))

    return __type
