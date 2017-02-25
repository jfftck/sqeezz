Sqeezz
======
Simple and Easy Dependency Injection
------------------------------------
### About the Module ###
Sqeezz is designed for Python 2.6 and 2.7, a 3.0+ version is planned and should not be too different.

The design for Sqeezz is to have simple and explict injection.

* First, it does not have any magic methods for resolving injection.
* Second, it requires that you use decorators and placeholders to indicate injection which makes the code easy to read and understand.
* Last, it is smaller than other solutions since it does not have to scan your files to connect the classes.

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
>>> Sqeezz.register(Foo)
```

In the application module:
```
>>> @inject
... def bar(Foo=Injected):
...    ...
```
_Please note the `Injected` placeholder, this is needed as the original function signature is preserved and will throw an error that the function is missing an argument (or more if you are injecting multiple dependencies). This design may change later, but it is required for now._
 
If you want to use classes then you can do the following.

The configuration file would be the same.

In the application module:
```
>>> class Bar:
...    @inject
...    def __init__(self, Foo=Injected):
...        self.foo = foo
...        ...
```
It is recommended that you assign the injected resource to the instance so you can use it in the whole class.

The `register` method allows multiple dependencies and aliases to be registered like the following.
```
>>> Sqeezz.register(foo=Foo, bar=Bar)
```
Or...
```
>>> resources = {'foo': Foo, 'bar': Bar)
>>> Sqeezz.register(**resources)
```

One more thing to note is the fact that the `Injected` placeholder is necessary and you must put all parameters for the dependencies that are injected at the end of the other parameters for the function/method.
```
>>> @inject
... def foo(x, y, z, bar=Injected):
...    ...
```
Above code will work, but the following will not.
```
>>> @inject
... def foo(bar=Injected, x, y, z):
...    ...
```
This is a python syntax requirement and can't be avoided.

#### Profiles ####
Profiles allow the switching between different sets of dependencies.
This is designed so that multiple dependencies with the same name can provide different implementations and the application can be more flexible.

To switch/register a profile name you call the `profile` method.
```
>>> Sqeezz.profile('foo')
```
And to switch to using no profile...
```
>>> Sqeezz.profile()
```
_This will not remove the profile and you can switch back by calling the `profile` function._

To see all of the profiles you just call the `profiles` function.
There is a `current_profile` method for getting the currently active profile and will be `None` if no profiles are selected.
```
>>> print Sqeezz.profiles()
['foo']
>>> print Sqeezz.current_profile()
None
>>> Sqeezz.profile('foo')
>>> print Sqeezz.current_profile()
foo
```

_If you register a dependency that is not in the default dependencies it will add to the default so that switching profiles will not cause the application to fail because the dependency could not be injected._

### Modifiers ###
There are a few modifier classes that can be used.

#### Callables ####
`Call(callback:callable, *args, **kwargs)`  
This is similar to the `partial` function in the `functools` module, but removes keyword arguments that conflict with the arguments.

#### File-Like Objects ####
`Data(callback:callable, *args, **kwargs)`  
This is designed to build functions that can be used with the `with` statement, like databases.

`File(path:string, file_command?: callable, *args, **kwargs)`  
This extends the `Data` class to open files.

#### Strict Type Matching ####
`@strict_type(*args:[class|(class, ...), ...], **kwargs: {var_name: class|(class, ...), ...})`  
This will throw a `TypeError` exception if the type is not a match.

`test_type(test:boolean)`  
This sets if the `@strict_type` will evaluate the types being passed (defaults to: `False`).

More information on the modifiers will be provided later...