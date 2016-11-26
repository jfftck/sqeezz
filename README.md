# Sqeezz #
## Simple and Easy Dependency Injection ##
### About the Module ###
The design for this module is on simplicity and explict injection.

* First it does not have any magic methods for resolving injection.
* Second it requires that you use decorators and placeholders to indicate injection.
* Third it does not protect the resource that is injected, so if it mutable it will affect the other modules using the resource. 
* Last it does not have special methods for handling design patterns, but there is a class that can decorate other classes and turn them into singletons.

The reason for doing this is to have a fast and light dependency injection option. There are many options that want to do all of the work, but in doing so they require time and space to calculate the dependency mappings, and end up creating a resource heavy library that slows the application.
 
This is what makes Sqeezz different, leaving the developer to the task of building the configuration and implementation of what is to be injected removes the issue of injecting the wrong resource.
 
### Usage ###
For the basic usage you can do the following.

In the configuration file:
```
register(foo=Foo)
```

In the application module:
```
@inject
def bar(foo=Injected):
    ...
```
_Please note the `Injected` placeholder, this is needed as the original function signature is preserved and will throw an error that the function is missing an argument (or more if you are injecting multiple resources). This design may change later, but it is required for now._
 
If you want to use classes then you can do the following.

The configuration file would be the same.

In the application module:
```
class Bar:
    @inject
    def __init__(self, foo=Injected):
        self.foo = foo
        ...
```
It is recommended that you assign the injected resource to the instance so you can use it in the whole class.

The `register` function allows multiple resources to be registered like the following.
```
register(foo=Foo, bar=Bar)
```
```
resources = {'foo': Foo, 'bar': Bar)
register(**resources)
```

One more thing to note is the fact that the `Injected` placeholder is necessary you should put all resources that are injected at the end of the parameters for the function/method.
```
@inject
def foo(x, y, z, bar=Injected):
    ...
```
This will work, but the following will not.
```
@inject
def foo(bar=Injected, x, y, z):
    ...
```
This is a python syntax requirement and can't be avoided.

### Modifiers ###
There are a few modifier classes that can be used.

`Call` - This is similar to the `partial` function in the `functools` module, but removes keyword arguments that conflict with the arguments.

`Data` - This is designed to build functions that can be used with the `with` statement.

`File` - This extends the `Data` class to open files.

`Singleton` - This will create a singleton for the class it is decorating. (This is the Decorator pattern and not the decorators that are a part of Python)

More information on the modifiers will be provided later...