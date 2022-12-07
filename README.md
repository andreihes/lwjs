# lwjs
**Light Weight JSON Shell** is a package to allow simple inline *"like-in-bash-shell"* expressions in JSON documents. Technically, no limits exist to apply on Python objects as well. It recursively scans any given object and performs evaluation of `fun` and `ref` and `sub` and `esc` expressions.\
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
```sh
pip install lwjs
```

# functions: $(name arg1 arg2 ... argN)
Name and args are separated by any number of spaces `" "`. Space is `0x20` only, no Unicode tricks. The number of spaces is not important and they are not preserved:\
**`"$(f x y)"` == `"$(  f   x   y  )"` == `call fun "f" with 2 args: "x" and "y"`**\
\
If spaces are important then they must be quoted using `"'"` a single-quote character:\
**`"$(f 'x y')"` == `"$('f' 'x y')"` == `call fun "f" with 1 arg: "x y"`**\
\
Quote has to be doubled if it is required within a quoted arg:\
**`"$(fun 'x''y')"` == `call "fun" with 1 arg: "x'y"`**\
\
If quote is not the first char then there is no need to doulbe it:\
**`"$(fun x''y)"` == `call "fun" with 1 arg: "x''y"`**\
\

This can be [customized](#customization)

# arguments
Whenever arg is quoted it will be passed as `str`, however for unquoted args there is a primitive-type conversion:

|Priority|Unquoted Arg Is...|Conversion Type|Conversion Logic|
|--------|------------------|---------------|----------------|
|1|`None`|NoneType|Hardcoded `None`|
|2|`^\s*null\s*$`|NoneType|Hardcoded `None`|
|3|`^\s*true\s*$`|bool|Hardcoded `True`|
|4|`^\s*false\s*$`|bool|Hardcoded `False`|
|5|`^\s*[+\-]?[0-9_]+\s*$`|int|`int(arg)`|
|6|`^\s*[+\-]?([0-9_]+\.[0-9_]*\|[0-9_]*\.[0-9_]+)\s*$`|float|`float(arg)`|

This can be [customized](#customization)

# references
Whenever the fun's name is prefixed with `@` char then it will not be called. Instead, the fun will be returned and all the args will be ignored. You may pass this fun to other fun, like `map` or anything:\
**`'''$(map $(@calc) $(json '["1+1", "5+3"]'))'''` == `[2, 8]`**
1. `$(json '["1+1", "5+3"]')` will return a list: `[ "1+1", "5+3" ]`
2. `$(@calc)` will return `calc` ref (callable)
3. `$(map ... ...)` will apply `calc` to every list's item

This can be [customized](#customization)

# substitutes: ${k1.k2. ... .kN}
Each key navigates in the initial object from the root. Integer indexes and string keys are supported. Each key must be separated by a dot `.` character. All the spaces are preserved as well thus it is not necessary to quote them, unlike the funs:\
**`"${'key 1'.'key 2'}"` == `"${key 1.key 2}"` == `root -> "key 1" -> "key 2"`**\
\
However, if the key contains a dot `.` then it must be quoted:\
**`"${'k.ey1'.'k.ey2'}"` == `root -> "k.ey1" -> "k.ey2"`**

# concatenation
Whenever fun or sub
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
