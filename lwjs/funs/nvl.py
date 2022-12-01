import lwjs.core.util as util

def nvl(*args) -> util.ANY:
  for arg in args:
    if arg is not None:
      return arg
  return None
