'''
DESCRIPTION
  Returns each arg packed into a list where each item is
  an object where key is type name and value is arg itself

EXAMPLES
  - $(dump 1 2)
    Result: [{'int': 2}, {'int': 2}]
  - $(dump 1 x false 'true')
    Result: [{'int': 1}, {'str': 'x'}, {'bool': False}, {'str': 'true'}]
'''

import typing

def dump(*args) -> list[typing.Any]:
  data = [ ]
  for arg in args:
    name = type(arg).__name__
    data.append({ name: arg })
  return data
