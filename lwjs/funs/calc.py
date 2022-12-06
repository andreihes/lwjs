import re

def calc(*args) -> int|float:
  args = ''.join([str(arg).lower() for arg in args])

  if not re.match(r'^[0-9/*%\+\-\.\(\)\s]*$', args):
    raise ValueError(f'Forbidden chars in "{args}"')

  try:
    ret = eval(args)
  except Exception as e:
    raise ValueError(f'Eval failed for "{args}"') from e

  if isinstance(ret, int|float):
    return ret

  raise TypeError('Unexpected return type of "{args}"')
