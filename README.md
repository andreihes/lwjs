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
- `esc` expression example is `$$`: whenever you need a `$` you have to pay `$$`

Output:
```
10
{'tasks': ['1+1', '2+2'], 'solve': [2, 4]}
{'in': {'v1': 2, 'v2': 5}, 'r': 7}
Must escape '$' character
```
NB: `calc` and `map` are `lwjs`-shipped funs: [calc.py](/lwjs/funs/calc.py), [map.py](/lwjs/funs/map.py)

# installation
```sh
pip install lwjs
```

# moar examples
Visit [tests](/test) to see more examples

# fun: $(name arg1 arg2 ... argN)
Name and args are separated by any number of spaces `" "`. Space is `0x20` only, no Unicode tricks. The number of spaces is not important and they are not preserved. If spaces are important then they must be quoted using `"'"` a single-quote character. Quote has to be doubled if it is required within a quoted arg. If quote is not the first char then there is no need to doulbe it\
\
Note the fun load logic can be [customized](#customization)

# ref: $(@name)
Whenever the fun's name is prefixed with `"@"` char then it is a ref. The fun will be returned and all the args will be ignored\
\
This behavior can be [customized](#customization)

# sub: ${k1.k2. ... .kN}
Each key navigates in the initial object from the root. Integer indexes and string keys are supported. Each key or index must be separated by a dot `"."` char. All the spaces are preserved as well thus it is not necessary to quote them, unlike the funs. However, if the key contains a dot `"."` then it must be quoted. When navigating, it is expected to see an `int` for nvigation within lists\
\
Note the navigation logic can be [customized](#customization)

# esc: $
You have to escape `"$"` by doubling it `"$$"`\
\
Note this can be [customized](#customization)

# arg
Whenever arg is quoted it will be passed as `str`. For complex quoted args [cat](#cat) rules apply. Unquoted literal args will be passed following the below conversions:

|Priority|Source Type|Obj `obj` Is...|Target Type|Conversion|
|--------|-----------|---------------|-----------|----------|
|1|str|`^$`|NoneType|`None`|
|2|str|`^null$`|NoneType|`None`|
|3|str|`^true$`|bool|`True`|
|4|str|`^false$`|bool|`False`|
|5|str|`^[\+\-]?[0-9]+$`|int|`int(obj)`|
|6|str|`^[\+\-]?([0-9]+\.[0-9]*\|[0-9]*\.[0-9]+)$`|float|`float(obj)`|
|7|str|Anything else|str|`obj`|

These conversions can be [customized](#customization)

# cat
Cat happens in case the result of fun or sub or ref is not the only one in the string. This is true for args as well (however, quoted args always forced into strings). Any value has to be presented as `str` in this case following the below conversions:

|Priority|Source Type|Obj `obj` Is...|Target Type|Conversion|
|--------|-----------|---------------|-----------|----------|
|1|NoneType|`None`|str|`"null"`|
|2|str|`any`|str|`obj`|
|3|bool|`True`|str|`"true"`|
|4|bool|`False`|str|`"false"`|
|5|int|`any`|str|`str(obj)`|
|6|float|`any`|str|`str(obj)`|
|7|any|`any`|str|`str(obj)`|

These conversions can be [customized](#customization)

# customization
Any customization involves `cook with aid` technique when you pass `lwjs.Aide` instance along with the data into `lwjs.cook`. This `lwjs.Aide` object may be equipped with multiple cooker parts which are different comparing to they original counterparts. Each original cooker part definition can be seen in [help.py](lwjs/core/help.py) as a function

<details><summary>Fun Load</summary><p>

There are two ways to alter the `fun` load routine and both involve `cook with aid` technique:
1. `"key"."value"` naming approach
```python
import lwjs

# in order to cook with aid you need lwjs.Aide object
aid = lwjs.Aide()

# enrich the Refs with necessary modules
# do not use "." in keys since default "load"
# will not be able to handle this properly
aid.Refs['J'] = 'json'
aid.Refs['O'] = 'os'

# use aid.Refs keys to refer the fun
data = "$( J.loads '[1, 2, 3]' )"

# cook with aid technique in work
data = lwjs.cook(data, aid)
print(data)

# repeat again
data = "$(O.cpu_count)"
data = lwjs.cook(data, aid)
print(data)
```
2. Replacing the original `load`
```python
import lwjs
import importlib

# define sample static method in a sample class
# we want to allow lwjs to call the static methods
class Helper:
  @staticmethod
  def fun(arg: str) -> str:
    return f'I am Helper.fun("{arg}")'

# custom load implementation follows this signature
# note the first argument: it is lwjs.Aid (not Aide)
def my_load(aid: lwjs.Aid, name: str) -> tuple[bool, lwjs.FUN]:
  tokens = name.rsplit('.', 3)
  if len(tokens) != 3:
    raise ValueError('Bad class method reference for fun')
  module = importlib.import_module(tokens[0])
  classo = getattr(module, tokens[1])
  method = getattr(classo, tokens[2])
  return True, method

# in order to cook with aid you need lwjs.Aide object
aid = lwjs.Aide()

# replace original load function with a custom implementation
aid.set_load(my_load)

data = '$(__main__.Helper.fun hello)'

# cook with aid technique in work
data = lwjs.cook(data, aid)
print(data)
```

</p></details>

<details><summary>Ref Detection</summary><p>
 
In order to change the `ref` detection logic it is necessary to redefine the original `load` routine (like shown in `Fun Load` customization). It is possible to implement any `ref` detection logic (including disabling the `ref` detection). The only requirement for `load` is to return `tuple[True, fun]` when `fun` is detected (so this will be called and all the args will be passed) and return `tuple[False, fun]` when this is a `ref` and it should not be called

</p></details>

<details><summary>Sub Navigation</summary><p>

Same `cook with aid` technique allows to redefine `nget` and `nset` operations in the `lwjs.Aide` and implement any navigation logic

</p></details>

<details><summary>Esc Escaping</summary><p>

This will disable the requirement to escape `"$"` char. However, in this case you won't be able to process strings like `"$("` or `"${"` since they will be always considered as `fun` or `sub` start. To disable `"$"` escapes use `cook with aid` technique:
```python
import lwjs

data = "This is $1"
aid = lwjs.Aide()
# set dollar-friendly propery
aid.Dofr = True
# and cook with aid
data = lwjs.cook(data, aid)
print(data)
```

</p></details>

<details><summary>Arg Conversions</summary><p>

```python
import lwjs

# define custom converter
def to_any(aid: lwjs.Aid, obj: str) -> lwjs.ANY:
  if obj == 'HUNDRED':
    return 100
  else:
    return obj

data = "$(dump HUNDRED)"
aid = lwjs.Aide()
aid.set_to_any(to_any)
data = lwjs.cook(data, aid)
print(data)
```

</p></details>

<details><summary>Cat Conversions</summary><p>

```python
import lwjs

# define custom converter
# not a very useful one
def to_str(aid: lwjs.Aid, obj: lwjs.ANY) -> str:
  return type(obj).__name__

data = "$(void) hello $(void)"
aid = lwjs.Aide()
aid.set_to_str(to_str)
data = lwjs.cook(data, aid)
print(data)
```

</p></details>
