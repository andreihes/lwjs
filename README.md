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
|7|str|Anything else|str|`str(obj)`|

These conversions can be [customized](#customization)

# cat
Cat happens in case the result of fun or sub or ref is not the only one in the string. This is true for args as well (however, quoted args always forced into strings). Any value has to be presented as `str` in this case following the below conversions:

|Priority|Source Type|Obj `obj` Is...|Target Type|Conversion|
|--------|-----------|---------------|-----------|----------|
|1|NoneType|`None`|str|`"null"`|
|2|str|`any`|str|`obj`|
|3|bool|`True`|str|`"true"`|
|4|bool|`False`|str|`"false"`|
|5|int|`any`|str|`int(obj)`|
|6|float|`any`|str|`float(obj)`|
|7|any|`any`|str|`str(obj)`|

These conversions can be [customized](#customization)

# customization
<details><summary>Fun Load</summary>
TODO
</details>

<details><summary>Ref Detection</summary>
TODO
</details>

<details><summary>Sub Navigation</summary>
TODO
</details>

<details><summary>Esc Escaping</summary>
TODO
</details>

<details><summary>Arg Conversions</summary>
TODO
</details>

<details><summary>Cat Conversions</summary>
TODO
</details>
