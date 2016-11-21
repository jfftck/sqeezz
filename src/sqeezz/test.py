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

    def add_mock(self, name, mock):
        self.__mocks[name] = mock

        return self

    def create(self):
        return {self.__injection_point: self.__Providers(self.__mocks)}
