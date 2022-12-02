# lwjs
**LightWeight JSON Shell** is a package to allow simple inline like-in-bash-shell expressions in your JSON documents. Technically, no limits exist to apply on Python objects as well. See few examples:
- `"$(calc 5+5)"`\
  **->** `10`\
  note the result is `int`, not `str`
- `"5 + 5 = $(calc 5 + 5)"`\
  **->** `"5 + 5 = 10"`\
  now, the result is `str` because everything got concatenated
- `{ "list": [ null, 1 ], "nvl": "$(nvl ${list.0} ${list.1})" }`\
  **->** `{ "list": [ null, 1 ], "nvl": 1 }`\
  here the result is `int`
- `{ "list": [ null, 1 ], "nvl": "$(nvl ${list.0} '${list.1}')" }`\
  **->** `{ "list": [ null, 1 ], "nvl": "1" }`\
  however, we can force it to be `str` using a quoted arg
- `{ "birth": { "Y": 2022, "M": "Jan", "D": "15" }, "short": "${birth.M} ${birth.D}, ${birth.Y}" }`\
  **->** `{ "birth": { "Y": 2022, "M": "Jan", "D": "15" }, "short": "Jan 15, 2022" }`\
  again, everything gets concatenated into `str`
- `{ "node": { "a": 1, "b": 2 }, "copy": "${node}" }`\
  **->** `{ "node": { "a": 1, "b": 2 }, "copy": { "a": 1, "b": 2 } }`\
  no need to concatenate so function's result left as is and it is `dict`

# installation
`pip install lwjs`

# code example
Consider having the below JSON object (which basically maps 1:1 to a Python dictionary). You may find the object stored directly into `text` and parsed into `data`, next cooked into `outs` and printed:
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
  "22+20": "${root.22+20}"
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
  "22+20": 42
}
```

Special `function` expressions here are `$(date 2022-01-31 + 1 month)` and `$(calc 22 + 20)`.\
Special `substitute` expressions here are `${root.today}` and `${root.22+20}`.

# functions
**`$(name arg1 arg2 ... argN)`**\
For a list of functions shipped with `lwjs` refer to `lwjs.core.funs`. Each function is located in a separate file where file name matches the function name. Also, you may "teach" `lwjs` to use custom functions from any other module. This is described in [customization](#customization).\
Techincally, function name can be quoted and contain whitespaces or quotes. However this is not used by default. You may somehow utilize this when customizing the functions.
TODO:
- Quoting
- Quoted args and not quoted args
- Basic type conversions

# substitutes
**`${key1.key2. ... .keyN}`**\
Substitute is a `.`-delimited path. Whenever a key contains a `.` you may use single-quote `'` to put it. To put a single-quot inside of quoted substitute's part just double it. Few examples:
TODO:
- 1
- 2
- 3

# customization
TODO
