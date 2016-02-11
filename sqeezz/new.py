import threading


class New(object):
    def __init__(self, cls):
        with threading.RLock():
            self.__cls = cls

    def __call__(self, *args, **kwargs):
        return self.__cls(*args, **kwargs)
