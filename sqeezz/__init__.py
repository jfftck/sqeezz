# coding=utf-8
from .libs.decorator import decorate
from .utils import ClassUtils, FuncUtils, ImportUtils


class _Inject(FuncUtils):
    """
    This is a private singleton class that stores the injection information.
    """
    __instance = None

    class __Inject(object):
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
            if name is not None and isinstance(name, (str, unicode)):
                cls.__current_profile = name
            else:
                cls.__current_profile = None

        @classmethod
        def profiles(cls):
            return cls.__profile_providers.iterkeys()

        @classmethod
        def register(cls, providers):
            cp = cls.__current_profile
            for name, provider in providers.iteritems():
                if cp is None or name not in cls.__default_providers:
                    cls.__default_providers[name] = provider
                else:
                    if cp not in cls.__profile_providers:
                        cls.__profile_providers[cp] = {}

                    cls.__profile_providers[cp][name] = provider

    @classmethod
    def __init__(cls):
        if not cls.__instance:
            cls.__instance = cls.__Inject()

    @classmethod
    def __call__(cls, func, *args, **kwargs):
        return cls.__instance(func, args, kwargs)

    @classmethod
    def __getattr__(cls, name):
        return getattr(cls.__instance, name)


class Injected(object):
    """
    This is a placeholder for injected values.
    """
    def __new__(cls, *args, **kwargs):
        return cls


class Imported(object):
    def __init__(self, name, package=None):
        self._name = name
        self._package = package

    def create(self):
        return ImportUtils.import_module(self._name, self._package)


class ModuleLoader(object):
    @classmethod
    def register(cls, *names):
        for name in names:
            if hasattr(name, 'iteritems'):
                for n, package in name.iteritems():
                    cls._register(ImportUtils.import_module(n, package))
            else:
                cls._register(ImportUtils.import_module(name))

    @classmethod
    def register_new(cls, *names, **packages):
        for name in names:
            cls._register(ImportUtils.load_module(name, name + '.py'))
        for name, path in packages.iteritems():
            cls._register(ImportUtils.load_module(name, path))

    @staticmethod
    def _register(mod):
        if mod:
            Sqeezz.register(**mod)


class Sqeezz(object):
    @staticmethod
    def current_profile():
        return _Inject().current_profile()

    @staticmethod
    def inject(func, *args, **kwargs):
        return _inject(func, *args, **kwargs)()

    @staticmethod
    def profile(name=None):
        _Inject().profile(name)

    @staticmethod
    def profiles():
        return _Inject().profiles()

    @staticmethod
    def register(*providers, **kwproviders):
        for provider in providers:
            if hasattr(provider, '__name__'):
                kwproviders[provider.__name__] = provider
        _Inject().register(kwproviders)


def _inject(func, *args, **kwargs):
    inj = _Inject()
    providers = inj.providers()
    mapped_args = inj.create_args_dict(func, args)

    def inject_provider():
        kwargs.update(mapped_args)

        for arg_name, provider in kwargs.iteritems():
            try:
                if provider is Injected:
                    kwargs[arg_name] = providers[arg_name]
                elif isinstance(provider, Imported):
                    kwargs[arg_name] = provider.create().values()[0]
            except TypeError:
                # Could have a type error
                pass

    def set_profile_providers():
        if inj.current_profile() in inj.p_providers():
            providers.update(inj.p_providers()[inj.current_profile()])

    set_profile_providers()
    inj.remove_invalid_kwargs(func, args, kwargs)
    inject_provider()

    return func(**kwargs)


def _register(name):
    def _inner(call, *args, **kwargs):
        if name:
            Sqeezz.register(**{name: call})
        else:
            Sqeezz.register(call)

        return call(*args, **kwargs)
    return _inner


def inject(func):
    return decorate(func, _inject)


def register(name=None):
    def _inner(call):
        return decorate(call, _register(name))

    return _inner
