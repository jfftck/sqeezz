import threading


class Singleton(object):
    def __init__(self, cls):
        with threading.RLock():
            self.__cls = cls
            self.__instance = None

    def __call__(self, *args, **kwargs):
        if not self.__instance:
            self.__instance = self.__cls(*args, **kwargs)

        return self.__instance

    def __getattr__(self, item):
        return getattr(self.__cls, item)
