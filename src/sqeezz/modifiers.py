import threading
import __builtin__


class Call(object):
    def __init__(self, call=None, *args, **kwargs):
        self.__call = call
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        args += self.args
        kwargs.update(self.kwargs)

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
