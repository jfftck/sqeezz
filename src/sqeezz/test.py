class Mock(object):
    class __Mock(object):
        def __init__(self, mock):
            self.__mock = mock

        def __getattr__(self, item):
            if item in self.__mock:
                return self.__mock[item]

            return None

    class __MockMethod(object):
        def __init__(self, value):
            self.__value = value

        def __call__(self, *args, **kwargs):
            return self.__value

    def __init__(self, name):
        self.__name = name
        self.__mock = {}

    def add_method(self, name, value):
        self.__mock[name] = self.__MockMethod(value)

        return self

    def add_attribute(self, name, value):
        self.__mock[name] = value

        return self

    def create(self):
        return {self.__name: self.__Mock(self.__mock)}

    def value(self, value):
        self.__mock = value


class MockInjector(object):
    class __Providers(object):
        def __init__(self, providers):
            self.__providers = providers

        def __getattr__(self, item):
            if item in self.__providers:
                return self.__providers[item]

    def __init__(self, injection_point):
        self.__injection_point = injection_point
        self.__mocks = {}

    def add_mock(self, mock):
        self.__mocks.update(mock.create())

        return self

    def create(self):
        return {self.__injection_point: self.__Providers(self.__mocks)}
