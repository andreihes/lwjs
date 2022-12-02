'''
Returns each arg packed into a list where each item is
an object where key is type name and value is arg itself
'''

import typing

def dump(*args) -> list[typing.Any]:
  data = [ ]
  for arg in args:
    name = type(arg).__name__
    data.append({ name: arg })
  return data
