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

# moar
Visit project [homepage](https://github.com/andreihes/lwjs) for more documentation and examples
