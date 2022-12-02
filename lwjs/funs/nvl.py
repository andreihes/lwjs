'''
DESCRIPTION
  Returns first non-None argument
  If no nulls or no args then returns None

EXAMPLES
  - $(nvl 1 null 2)
    Result: 1
  - $(nvl null null 2)
    Result: 2
'''

import typing

def nvl(*args) -> typing.Any:
  for arg in args:
    if arg is not None:
      return arg
  return None
