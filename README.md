# lwjs
**LightWeight JSON Shell** is a package to allow simple inline like-in-bash-shell expressions in your JSON documents. Technically, no limits exist to apply on Python objects as well. See few examples:
- `"$(calc 5+5)"`\
  **->** `10`
  
- `"5 + 5 = $(calc 5 + 5)"`\
  **->** `"5 + 5 = 10"`
  
- `{ "in": { "v1": 2, "v2": 5 }, "r": "$(calc ${in.v1} + ${in.v2})" }`\
  **->** `{ "in": { "v1": 2, "v2": 5 }, "r": 7 }`
  
- `"$(json $(read ~/data.json))"`\
  **->** `{ "data": [ 1, 2, 3 ] }`
  
NB: `calc`, `json`, `read` are `lwjs`-shipped funs: [calc.py](/lwjs/funs/calc.py), [json.py](/lwjs/funs/json.py), [read.py](/lwjs/funs/read.py)

# installation
Unexpectedly, it is `pip install lwjs`

# example
Consider having the below JSON object (which basically maps 1:1 to a Python dictionary). You may find the string object definition stored directly into `text` and parsed into `data`, next cooked into `outs` with `lwjs` and printed:
```python
import lwjs
import json

text = '''
{
  "root": {
    "adate": "$(date 2022-01-31 + 1 month)",
    "22+20": "$(calc 22 + 20)"
  },
  "adate": "${root.adate}",
  "22+20": "${root.22+20}",
  "notes": "You only have to escape $$ character"
}
'''

# parsed object
data = json.loads(text)

# cooked it
outs = lwjs.cook(data)

# pretty printed it
print(json.dumps(outs, indent = 2))
```
Result:
```json
{
  "root": {
    "adate": "2022-02-28",
    "22+20": 42
  },
  "adate": "2022-02-28",
  "22+20": 42,
  "notes": "You only have to escape $ character"
}
```

Special `function` expressions here are `"$(date 2022-01-31 + 1 month)"` and `"$(calc 22 + 20)"`.\
Special `substitute` expressions here are `"${root.adate}"` and `"${root.22+20}"`.\
Special `escape` character here is `$`. Whenever you need a `$` you have to pay two: `$$`

# more examples
Visit [tests](/test) to see more examples

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
## Customize Function Load
TODO

## Customize Function Argument Conversions
TODO

## Customize Result Concatenation Conversions
TODO

