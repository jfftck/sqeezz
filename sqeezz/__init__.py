class Inject(object):
    __instance = None

    class __Inject(object):
        __injected_prefix = 'injected_'
        __items = {}

        def __call__(self, item_name, func):
            def __inject(*args, **kwargs):
                if isinstance(item_name, list):
                    for item in item_name:
                        if isinstance(item, list):
                            name = item.pop(0)

                            if isinstance(item, list):
                                values = item
                            else:
                                values = [self.__class__.__items[x] for x in item]
                        else:
                            name = item
                            values = None

                        if values:
                            kwargs['{}{}'.format(self.__injected_prefix, name)] = self.__class__.__items[name](*values)
                        else:
                            kwargs['{}{}'.format(self.__injected_prefix, name)] = self.__class__.__items[name]
                else:
                    kwargs['{}{}'.format(self.__injected_prefix, item_name)] = self.__class__.__items[item_name]

                func(*args, **kwargs)

            return __inject

        @classmethod
        def register(cls, item_name, item):
            cls.__items[item_name] = item

        @classmethod
        def prefix(cls, new_prefix=None):
            if new_prefix:
                cls.__injected_prefix = new_prefix
            else:
                return cls.__injected_prefix

    @classmethod
    def __init__(cls, item_name=None):
        if not cls.__instance:
            cls.__instance = cls.__Inject()

        cls.__item_name = item_name

    @classmethod
    def __getattr__(cls, name):
        return getattr(cls.__instance, name)

    @classmethod
    def __call__(cls, func):
        return cls.__instance(cls.__item_name, func)
