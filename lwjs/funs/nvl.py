'''
Returns first non-None argument
If no nulls or no args then returns None
'''

import typing

def nvl(*args) -> typing.Any:
  for arg in args:
    if arg is not None:
      return arg
  return None
