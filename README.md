# Sqeezz #
## Simple and Easy Dependency Injection ##
### About the Module ###
Sqeezz is designed for Python 2.6 and 2.7, a 3.0+ version is planned and should not be too different.

The design for Sqeezz is to have simple and explict injection.

* First, it does not have any magic methods for resolving injection.
* Second, it requires that you use decorators and placeholders to indicate injection.
* Third, it is easy to read the code and know what is happening since everything is marked with placeholders and decorators.
* Last, it does not have special methods for handling design patterns, but there is a class that can decorate other classes and turn them into singletons.

The reason for doing this is to have a fast and light dependency injection option.
There are many options that want to do all of the work, but in doing so they require time and space to calculate the dependency mappings, and end up creating a resource heavy library that slows the application.
Also, many other dependency injection frameworks hide the "wiring" and you have to look for configuration files to know what is going on. 
 
This is what makes Sqeezz different, leaving the developer to the task of building the configuration and implementation of what is to be injected removes the issue of injecting the wrong dependency.
Being explict keeps Sqeezz from having the developer from having to guess what is being injected.
 
### Usage ###
#### Injection ####
For the basic usage you can do the following.

In the configuration file:
```
>>> register(foo=Foo)
```

In the application module:
```
>>> @inject
... def bar(foo=Injected):
...    ...
```
_Please note the `Injected` placeholder, this is needed as the original function signature is preserved and will throw an error that the function is missing an argument (or more if you are injecting multiple dependencies). This design may change later, but it is required for now._
 
If you want to use classes then you can do the following.

The configuration file would be the same.

In the application module:
```
>>> class Bar:
...    @inject
...    def __init__(self, foo=Injected):
...        self.foo = foo
...        ...
```
It is recommended that you assign the injected resource to the instance so you can use it in the whole class.

The `register` function allows multiple dependencies to be registered like the following.
```
>>> register(foo=Foo, bar=Bar)
```
Or...
```
>>> resources = {'foo': Foo, 'bar': Bar)
>>> register(**resources)
```

One more thing to note is the fact that the `Injected` placeholder is necessary you should put all parameters for the dependencies that are injected at the end of the other parameters for the function/method.
```
>>> @inject
... def foo(x, y, z, bar=Injected):
...    ...
```
This will work, but the following will not.
```
>>> @inject
... def foo(bar=Injected, x, y, z):
...    ...
```
This is a python syntax requirement and can't be avoided.

#### Profiles ####
Profiles allow the switching between different sets of dependencies.
This is designed so that multiple dependencies with the same name can provide different implementations and the application can be more flexible.

To switch/register a profile name you call the `profile` function.
```
>>> profile('foo')
```
And to switch to using no profile...
```
>>> profile()
```
_This will not remove the profile and you can switch back by calling the `profile` function._

To see all of the profiles you just call the `profiles` function.
There is a `current_profile` function for getting the currently active profile and will be `None` if no profiles are selected.
```
>>> print profiles()
['foo']
>>> print current_profile()
None
>>> profile('foo')
>>> print current_profile()
foo
```

If you register a dependency that is not in the default dependencies it will add it to both so that switching profiles will not cause the application to fail because the dependency could not be injected.

### Modifiers ###
There are a few modifier classes that can be used.

`Call` - This is similar to the `partial` function in the `functools` module, but removes keyword arguments that conflict with the arguments.

`Data` - This is designed to build functions that can be used with the `with` statement.

`File` - This extends the `Data` class to open files.

`Singleton` - This will create a singleton for the class it is decorating. (This is the Decorator pattern and not the decorators that are a part of Python)

`@strict_type` - This will throw a `TypeError` exception if the type is not a match.

More information on the modifiers will be provided later...