class Inject(object):
    __instance = None

    class __Inject(object):
        class __Bindings(object):
            def __init__(self, bindings):
                self.__bindings = bindings

            def __getattr__(self, name):
                try:
                    return self.__bindings[name]
                except KeyError:
                    return None

            def __setattr__(self, name, value):
                self.__bindings[name] = value

        class __Injected(object):
            class Unset(object):
                pass

            def __init__(self, providers, bindings):
                self.__providers = providers
                self.__bindings = bindings

            def provider(self, name):
                return getattr(self.__providers, name)

            def binding(self, name, value=Unset):
                if isinstance(value, self.Unset):
                    return getattr(self.__bindings, name)
                else:
                    setattr(self.__bindings, name, value)

                return self

        class __Providers(object):
            def __init__(self, providers):
                self.__providers = providers

            def __getattr__(self, name):
                try:
                    return self.__providers[name]
                except KeyError:
                    return None

        __all_bindings = {}
        __current_profile = None
        __default_providers = {}
        __injection_point = 'injected'
        __profile_providers = {}

        def __call__(self, func):
            def __inject(*args, **kwargs):
                if self.injection_point() not in kwargs:
                    providers = self.__providers()
                    bindings = self.__bindings()

                    if self.__profile() in self.__p_providers():
                        providers.update(self.__p_providers()[self.__profile()])

                    kwargs[self.injection_point()] = self.__Injected(
                        self.__Providers(providers), self.__Bindings(bindings))

                return func(*args, **kwargs)

            return __inject

        @classmethod
        def __bindings(cls):
            return cls.__all_bindings

        @classmethod
        def __p_providers(cls):
            return cls.__profile_providers

        @classmethod
        def __profile(cls):
            return cls.__current_profile

        @classmethod
        def __providers(cls):
            return cls.__default_providers.copy()

        @classmethod
        def binding(cls, name, value):
            cls.__all_bindings[name] = value

        @classmethod
        def injection_point(cls, injection_point=None):
            if injection_point is not None and isinstance(injection_point, basestring):
                cls.__injection_point = injection_point
            else:
                return cls.__injection_point

        @classmethod
        def profile(cls, name=None):
            if name is not None and isinstance(name, basestring):
                cls.__current_profile = name
            else:
                cls.__current_profile = None

        @classmethod
        def profiles(cls):
            return cls.__profile_providers.iterkeys()

        @classmethod
        def register(cls, provider_name, provider):
            if cls.__current_profile is None or provider_name not in cls.__default_providers:
                cls.__default_providers[provider_name] = provider

            if cls.__current_profile is not None:
                if cls.__current_profile not in cls.__profile_providers:
                    cls.__profile_providers[cls.__current_profile] = {}

                cls.__profile_providers[cls.__current_profile][provider_name] = provider

    @classmethod
    def __init__(cls):
        if not cls.__instance:
            cls.__instance = cls.__Inject()

    @classmethod
    def __getattr__(cls, name):
        return getattr(cls.__instance, name)

    @classmethod
    def __call__(cls, func):
        return cls.__instance(func)
