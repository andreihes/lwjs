# lwjs
**LightWeight JSON Shell** is a module to allow simple inline like-in-bash-shell expressions in your JSON documents. Technically, no limits exist to apply on Python objects as well.

# installation
TODO

# example
Example first. Consider having the below JSON object (which basically maps 1:1 to a Python dictionary):
```json
{
  "root":
  {
    "today": "$(date)",
    "22+20": "$(expr 22 + 20)"
  },
  "today": "${root.today}",
  "22+20": "${root.22+20}"
}
```
Special `function` expressions here are `$(date)` and `$(expr 22 + 20)`. This is how to use a function:\
**`$(name arg1 arg2 ... argN)`**\
\
Special `substitute` expressions here are `${root.today}` and `${root.22+20}`. This is how to use substitute:\
**`${key1.key2. ... .keyN}`**\
\
Now let's feed it into **lwjs** and it will transform all functions and substitutes:
1. TODO
2. TODO
3. TODO
4. TODO

# functions
TODO

# substitutes
TODO
