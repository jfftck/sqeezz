from inspect import getargspec
from sqeezz.libs.decorator import decorate
from sqeezz.modifiers import _Common


class _Inject(object):
    __instance = None

    class __Inject(_Common):
        __current_profile = None
        __default_providers = {}
        __profile_providers = {}

        @classmethod
        def current_profile(cls):
            return cls.__current_profile

        @classmethod
        def p_providers(cls):
            return cls.__profile_providers

        @classmethod
        def providers(cls):
            return cls.__default_providers.copy()

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
        def register(cls, providers):
            for name, provider in providers.iteritems():
                if cls.__current_profile is None or name not in cls.__default_providers:
                    cls.__default_providers[name] = provider

                if cls.__current_profile is not None:
                    if cls.__current_profile not in cls.__profile_providers:
                        cls.__profile_providers[cls.__current_profile] = {}

                    cls.__profile_providers[cls.__current_profile][name] = provider

    @classmethod
    def __init__(cls):
        if not cls.__instance:
            cls.__instance = cls.__Inject()

    @classmethod
    def __getattr__(cls, name):
        return getattr(cls.__instance, name)

    @classmethod
    def __call__(cls, func, *args, **kwargs):
        return cls.__instance(func, args, kwargs)


class Injected(object):
    """
    This is a placeholder for injected values.
    """


def _inject(func, *args, **kwargs):
    inj = _Inject()
    providers = inj.providers()
    spec = getargspec(func)
    args = list(args)

    if inj.current_profile() in inj.p_providers():
        providers.update(inj.p_providers()[inj.current_profile()])

    while Injected in args:
        args.remove(Injected)

    for provider in spec.args:
        if provider in providers and provider not in kwargs:
            kwargs[provider] = providers[provider]

    inj.remove_dup_args(func, args, kwargs)

    return func(*args, **kwargs)


def current_profile():
    return _Inject().current_profile()


def inject(func):
    return decorate(func, _inject)


def profile(name=None):
    _Inject().profile(name)


def profiles():
    return _Inject().profiles()


def register(**providers):
    _Inject().register(providers)
