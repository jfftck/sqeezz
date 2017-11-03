Sqeezz
======
Simple and Easy Dependency Injection
------------------------------------
### About Sqeezz and Modifiers ###
Sqeezz is designed for Python 2.6 and 2.7, a 3.0+ version is planned and should 
not be too different.

The design for Sqeezz is to have simple and explict injection.

* First, it does not have any magic methods for resolving injection.
* Second, it requires that you use decorators and placeholders to indicate 
  injection which makes the code easy to read and understand.
* Last, it is smaller than other solutions since it does not have to scan your 
  files to connect the classes.

The reason for doing this is to have a fast and light dependency injection 
option. There are many options that want to do all of the work, but in doing so
they require time and space to calculate the dependency mappings, and end up 
creating a resource heavy library that slows the application. Also, many other 
dependency injection frameworks hide the "wiring" and you have to look for 
configuration files to know what is going on. 
 
This is what makes Sqeezz different, leaving the developer to the task of 
building the configuration and implementation of what is to be injected removes 
the issue of injecting the wrong dependency. Being explict keeps Sqeezz from 
having the developer from having to guess what is being injected.

### Sqeezz ###

#### Injected Class ####
`Injected`  
**Parent: `None`**

This is a placeholder for injected dependencies and 
_must **NOT** be instantiated_.

#### Sqeezz Class ####
`Sqeezz`  
**Parent: `object`**

This is the main class for controlling the dependency injection and all methods 
are static.

##### Methods #####

###### Current Profile ######
static `current_profile()`  
Return Value: `str|unicode`

###### Inject ######
static `inject(func: callable, *args, **kwargs)`  
Return Value: decorated `func` callable

###### Profile ######
static `profile(name:str|unicode=None)`  
Return Value: `None`

This sets the profile name or if left blank will set back to default.

###### Profiles ######
static `profiles()`  
Return Value: `[str|unicode, ...]`

This will list the profiles that are defined.

###### Register ######
static `register(*providers:[callable, ...], **kwproviders:{alias: *, ...})`  
Return Value: `None`

This will register a provider, which can be a class or any value. 

There is two ways to define callable providers, they can be given as just 
parameters or as keyword parameters.

All other providers must be keyword parameters and that would make them aliased 
providers. This is a great way to add state configurations.

`Sqeezz.register(state={})`

This allows values to be stored and modified across the application and are 
accessed like this `state['value_name']` or modified/set like this 
`state['value_name'] = value`.

If the values are to be constant then it should be declared outside of 
dictionary like this `Sqeezz.register(value_name=value)`.

#### Inject Decorator ####

`@inject`

This adds the dependencies to the function/method that it is decorating.

#### Register Decorator ####

`@register(name:str=None)`

This will add the class/function to the dependency providers. It is recommended
to use this instead of importing, so that if the need to make it a new shared 
module/package, the project will refactor very easily.

It takes an optional string for the name, don't use unicode for this value as it
will cause an exception to be raised. If this is blank it will be based on the
class/function passed in, like `def Report()` will set the name to `'Report'`.

Example:

Class is code in the application:  
`config.py`: Importing the module will cause it to register.
```python
import team_report
```

`report.py`: This will self register when imported.
```python
@register('Report')
class TeamReport(object):
    # code here
```

`app.py`: This will inject any registered providers that are named.
```python
class ReportBuilder(object):
    @inject
    def __init__(self, Report=Injected):
        # code here
```

Class is imported from shared module:  
`config.py`: Importing the module or class from a module, and then registering
the provider.
```python
from team_report import TeamReport

Sqeezz.register(Report=TeamReport)
```

`app.py`: This will inject any registered providers that are named.
```python
class ReportBuilder(object):
    @inject
    def __init__(self, Report=Injected):
        # code here
```

Notice that the the core application does not have any changes, just the way it
is imported and registered.

Now this is a simple example, but imagine that the TeamReport class is used in
many modules and all the import statements would have to refactored if Sqeezz is
not used.

### Usage ###

#### Injection ####
For the basic usage you can do the following.

In the configuration file:
```pythonstub
>>> Sqeezz.register(Foo)
```

In the application module:
```pythonstub
>>> @inject
... def bar(Foo=Injected):
...    # code here
```
_Please note the `Injected` placeholder, this is needed as the original function
signature is preserved and will throw an error that the function is missing an 
argument (or more if you are injecting multiple dependencies). This design may 
change later, but it is required for now._
 
If you want to use classes then you can do the following.

The configuration file would be the same.

In the application module:
```pythonstub
>>> class Bar:
...    @inject
...    def __init__(self, Foo=Injected):
...        self.foo = foo
...        # code here
```
It is recommended that you assign the injected resource to the instance so you 
can use it in the whole class.

The `register` method allows multiple dependencies and aliases to be registered 
like the following.
```pythonstub
>>> Sqeezz.register(foo=Foo, bar=Bar)
```
Or...
```pythonstub
>>> resources = {'foo': Foo, 'bar': Bar)
>>> Sqeezz.register(**resources)
```

One more thing to note is the fact that the `Injected` placeholder is necessary 
and you must put all parameters for the dependencies that are injected at the 
end of the other parameters for the function/method.
```pythonstub
>>> @inject
... def foo(x, y, z, bar=Injected):
...    # code here
```
Above code will work, but the following will not.
```pythonstub
>>> @inject
... def foo(bar=Injected, x, y, z):
...    # code here
```
This is a python syntax requirement and can't be avoided.

#### Profiles ####
Profiles allow the switching between different sets of dependencies.
This is designed so that multiple dependencies with the same name can provide 
different implementations and the application can be more flexible.

To switch/register a profile name you call the `profile` method.
```pythonstub
>>> Sqeezz.profile('foo')
```
And to switch to using no profile...
```pythonstub
>>> Sqeezz.profile()
```
_This will not remove the profile and you can switch back by calling the 
`profile` function._

To see all of the profiles you just call the `profiles` function.
There is a `current_profile` method for getting the currently active profile and
will be `None` if no profiles are selected.
```pythonstub
>>> print Sqeezz.profiles()
['foo']
>>> print Sqeezz.current_profile()
None
>>> Sqeezz.profile('foo')
>>> print Sqeezz.current_profile()
foo
```

_If you register a dependency that is not in the default dependencies it will 
add to the default so that switching profiles will not cause the application to 
fail because the dependency could not be injected._

#### ModuleLoader ####
The ModuleLoader allows you to load Python packages/modules and make them 
available for injection in one command.
```pythonstub
>>> ModuleLoader.register('foo')
```

Now it can be injected.
```pythonstub
>>> @inject
... def bar(foo=Injected):
...     # code here
```

There is also a way to load a python file directly for injection.
```pythonstub
>>> ModuleLoader.register_new('/new/foo.py')
```

And again you will be able to inject the dependency.

_Be careful to only register trusted code._


### Modifiers ###
_**The `sqeezz_modifiers` package is optional.**_  
There are a few modifiers that can be used to simplify tasks.

#### Call Class  ####
`Call(callback:callable, *args, **kwargs)`  
_`Call` is a `callable(*args, **kwargs)` object._  
**Parent: `sqeezz.utils.FuncUtils`**

This is similar to the `partial` function in the `functools` module, but removes
keyword arguments that conflict with the arguments.

#### Data Class ####
`Data(callback:callable, *args, **kwargs)`  
_`Data` is a `callable(*args, **kwargs)` object._  
**Parent: `object`**

This is designed to build functions that can be used with the `with` statement, 
like databases.

##### Methods #####

`exception(callback:callable)`  
Return Value: `Data` instance

`exit(callback:callable, *args, **kwargs)`  
Return Value: `Data` instance

#### File Class ####
`File(path:string, file_command?: callable, *args, **kwargs)`  
_`File` is a `callable(*args, **kwargs)` object._  
**Parent: `sqeezz_modifiers.Data`**

This extends the `Data` class to open files.

#### Strict Type Decorator ####
`@strict_type(*args:[class|(class, ...), ...], 
**kwargs: {var_name: class|(class, ...), ...})`

The order is the same as the function that it is decorating, so if the type of 
the first argument is not being specified then keywords must be used.

This will throw a `TypeError` exception if the type is not a match.

#### Test Type Function ####
`test_type(test:boolean)`  
Return Value: `None`

This sets if the `@strict_type` will evaluate the types being passed 
(defaults to: `False`).

More information on the modifiers will be provided later...