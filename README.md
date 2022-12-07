# lwjs
**Light Weight JSON Shell** is a package to allow simple inline *"like-in-bash-shell"* expressions in JSON documents. Technically, no limits exist to apply on Python objects as well. It recursively scans any given object and performs evaluation of `fun` and `ref` and `sub` and `esc` expressions.\
\
Consider the example:
```python
import lwjs

data = "$(calc 5 + 5)"
data = lwjs.cook(data)
print(data)

data = { "tasks": [ "1+1", "2+2" ], "solve": "$(map $(@calc) ${tasks})" }
data = lwjs.cook(data)
print(data)

data = { "in": { "v1": 2, "v2": 5 }, "r": "$(calc ${in.v1} + ${in.v2})" }
data = lwjs.cook(data)
print(data)

data = "Must escape '$$' character"
data = lwjs.cook(data)
print(data)
```
Legend:
- `fun` expression example is `"$(calc)"` or `"$(map)"`
- `ref` expression example is `"$(@calc)"`
- `sub` expression example is `"${tasks}"` or `"${in.v1}"` or `"${in.v2}"`
- `esc` expression example is `$`: whenever you need a `$` you have to pay `$$`

Output:
```
10
{'tasks': ['1+1', '2+2'], 'solve': [2, 4]}
{'in': {'v1': 2, 'v2': 5}, 'r': 7}
Must escape '$' character
```

NB: `calc` and `map` are `lwjs`-shipped funs: [calc.py](/lwjs/funs/calc.py), [map.py](/lwjs/funs/map.py)

# moar
Visit [tests](/test) to see more examples

# installation
Unexpectedly: `pip install lwjs`
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
TODO: continue from here
# functions
`$(name arg1 arg2 ... argN)`\
Name and arguments are separated by any number of whitespaces ` `. Whitespace is **0x20** only, no Unicode tricks. The number of spaces is not important and they are not preserved. If spaces are important then they must be quoted. Quotation is done using single-quote character `'`. For example: `$('my fun' 'my arg')`. This will load function with name `"my fun"` and call it passing a single argument `"my arg"`. There are no default functions (shipped with `lwjs`) that may require quoting the name. However, quoting the args may be required. You may also [customize](#customization) function load routine and somehow use function name quotation feature if needed. If you need a quote inside of a quoted name or argument then just double it:
- `"$(fun x y)"` == `"$(  fun   x   y  )"`\
  Calls function `fun` with two arguments: `"x"` and `"y"`
  
- `"$(fun 'x y')"` == `"$(  fun   'x y'   )"`\
  Calls function `fun` with one argument: `"x y"`
  
- `"$(fun Hi, '''BOB''' !)"`\
  Calls function `fun` with three arguments: `"Hi,"`, `"'BOB'"`, `"!"`
  
- `"$(fun 'Hi, ''BOB''!')"`\
  Calls function `fun` with one argument: `"Hi, 'BOB' !"`
  
For a list of functions shipped with `lwjs` refer to [lwjs.funs](/lwjs/funs). Each function is located in a separate file where file name matches the function name. Also, you may [customize](#customization) `lwjs` to use any function from any module.

# arguments
There is a conversion for simple-type **unquoted** arguments (**quoted** arguments are always a string) before calling a function. Take a look at [dump.py](/lwjs/funs/dump.py) which ooutputs a list of args passed and their types and the below list:
- String `"null"` will be passed as `None`\
  `"$(dump null 'null')"`\
  **->** `[ { "NoneType": null }, { "str": "null" } ]`
  
- String `"true"` will be passed as `True`\
  `"$(dump true 'true')"`\
  **->** `[ { "bool": true }, { "str": "true" } ]`
  
- String `"false"` will be passed as `False`\
  `"$(dump false 'false')"`\
  **->** `[ { "bool": false }, { "str": "false" } ]`
  
- String that looks like an `int` will be passed as `int`\
  `"$(dump 42 4_2 '42')"`\
  **->** `[ { "int": 42 }, { "int": 42 }, { "str": "42" } ]`
  
- String that looks like a `float` will be passed as `float`\
  `"$(dump 0.42 .4_2 '.42')"`\
  **->** `[ { "float": 0.42 }, { "float": 0.42 }, { "str": ".42" } ]`
  
See for the default conversions: [help.py#str2any](/lwjs/core/help.py). This can be [customized](#customization)

# substitutes
`${k1.k2. ... .k3}`\
Each key navigates the initial object from the root. Integer indexes and string keys are supported. Each key must be separated by a dot `.` character. All the whitespaces are preserved as well, so:
- `"${key1.key2}"`\
  -> `"key1"` -> `"key2"`
- `"${key1 .key2 }"`\
  -> `"key1 "` -> `"key2 "`

etc. So it is not necessary to quote the whitespaces, like in functions. However, if the key contains dot `.` character then it must be quoted. Here are few examples to illustrate:
- `"${'key1'.'key2'}"` == `"${key1.key2}"`\
  -> `"key1"` -> `"key2"`
- `"${'k.ey1'.'k.ey2'}"`\
  -> `"k.ey1"` -> `"k.ey2"`
- `"${k'ey1.k'ey2}"` == `"${'k''ey1'.'k''ey2'}"`\
  -> `"k'ey1"` -> `"k'ey2"`

# concatenation
Once fun `"$()"` or sub `"${}"` evaluates the result is concatenated into a string where the fun `"$()"` or the sub `"${}"` is encountered. Conversion of the fun or sub result into a string can be [customized](#customization). However, when the fun or the sub is the only expression within the string then no conversion happens. Compare the examples:
- `"$(calc 2+2)"`\
  -> `4` (`int`, not `str`)
- `"2 + 2 = $(calc 2+2) (usually)"`\
  -> `"2 + 2 = 4 (usually)"` (result is `str` now)

See for the default conversions: [help.py#any2str](/lwjs/core/help.py). This can be [customized](#customization)

# customization
#### Customize Function Load
You may find default logic implemented in [help.py#func](/lwjs/core/help.py). There are two ways to add functions from other modules. First one is use the standart `func` load routine [help.py#func](/lwjs/core/help.py) but with the `Aide` object. Register your functions using `Refs` property. They key is a part before `.` and the function name is a part after the `.`. Example:
```python
import json
import lwjs

# this is a custom function
# that we want to use further
def fun():
  return 'Hello from fun()'

# this is how it will be called
data = '$(my.fun)'

# default cook brings exception
# ValueError: Have you registered ref "my"?
# outs = lwjs.cook(data)

# register module for "my"
aid = lwjs.Aide()
aid.Refs['my'] = '__main__'

# cook with aid
outs = lwjs.cook(data, aid)

# print
print(json.dumps(outs, indent = 2))
```
Another option is to implement your own load routine. For this, you have to define a function that will recevie `name:str` as an argument and parse it on your own. Here is an example where it only can load `json.dumps` or `json.loads`:
```python
import json
import lwjs

# define custom load function
def func(Aid: lwjs.Aid, name: str) -> lwjs.FUN:
  if name == 'loads':
    return json.loads
  if name == 'dumps':
    return json.dumps
  raise ValueError('Unsupported name "${name}"')

# our data
data = { 'load': '$(loads \'{ "k1": "v1", "k2": "v2" }\')', 'dump': '$(dumps ${load})' }

# register new func
aid = lwjs.Aide()
aid.set_func(func)

# cook with aid
outs = lwjs.cook(data, aid)

# print
print(json.dumps(outs, indent = 2))
```

#### Customize Function Argument Conversions
Use `lwjs.Aids` instance and set a new `to_any` conversion function. Example:
```python
import json
import lwjs

# define conversion function
def to_any(aid: lwjs.Aid, obj: None|str) -> lwjs.ANY:
  if obj == 'HUNDRED':
    return 100
  else:
    return obj

# our data
data = '$(dump HUNDRED)'

# register new to_any
aid = lwjs.Aide()
aid.set_to_any(to_any)

# cook with aid
outs = lwjs.cook(data, aid)

# print
print(json.dumps(outs, indent = 2))
```

#### Customize Result Concatenation Conversions
Use `lwjs.Aids` instance and set a new `to_str` conversion function. Example:
```python
import json
import lwjs

# define conversion function
def to_str(aid: lwjs.Aid, obj: None|lwjs.ANY) -> str:
  if obj is None:
    return '[NULL VALUE]'
  else:
    return str(obj)

# our data
data = 'Result: $(void)'

# register new to_str
aid = lwjs.Aide()
aid.set_to_str(to_str)

# cook with aid
outs = lwjs.cook(data, aid)

# print
print(json.dumps(outs, indent = 2))
```
