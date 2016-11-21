class Mock(object):
    class __Mock(object):
        def __init__(self, mocks):
            self.__mocks = mocks

        def __add__(self, other):
            return self.__mocks['__add__']

        def __and__(self, other):
            return self.__mocks['__and__']

        def __call__(self, *args, **kwargs):
            return self.__mocks['__call__']

        def __contains__(self, item):
            return self.__mocks['__contains__']

        def __getattr__(self, item):
            if item in self.__mocks:
                return self.__mocks[item]

            return None

    class __MockMethod(object):
        def __init__(self, value, error):
            self.__value = value
            self.__error = error

        def __call__(self, *args, **kwargs):
            if self.__error:
                raise self.__error

            return self.__value

    def __init__(self, name):
        self.__name = name
        self.__mocks = {}
        self.__error = None

    def add_method(self, name, value):
        self.__mocks[name] = self.__MockMethod(value, self.__error)
        self.__error = None

        return self

    def add_attribute(self, name, value):
        self.__mocks[name] = value

        return self

    def create(self):
        return {self.__name: self.__Mock(self.__mocks)}

    def error(self, error):
        self.__error = error

    def value(self, value):
        self.__mocks = value


class MockInjector(object):
    class __Providers(object):
        def __init__(self, providers):
            self.__providers = providers

        def __getattr__(self, item):
            try:
                return self.__providers[item]
            except KeyError:
                return None

    def __init__(self, injection_point):
        self.__injection_point = injection_point
        self.__mocks = {}

    def add_mock(self, mock):
        self.__mocks.update(mock.create())

        return self

    def create(self):
        return {self.__injection_point: self.__Providers(self.__mocks)}
