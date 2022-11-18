import re
import json
import typing
import importlib
import functools

import lwjs.bone as bone

RSF = bone.Raw | bone.Sub | bone.Fun
PAQ = bone.Pin | bone.Arg | bone.Quo

class BadChop(Exception):
  def __init__(self, msg: str, line: str, index: int) -> None:
    # TODO: shorten long lines
    super().__init__(f'{msg}. Index {index}: "{line}"')

class Context:
  def __init__(self, root: typing.Any) -> None:
    self.Root: typing.Any = root
    self.Path: list[str] = [ ]
    self.Hits: dict[int, str] = { }

def try2pri(obj: typing.Any) -> typing.Any:
  # TODO: define all conversion rules
  if obj is None:
    return None

  if not isinstance(obj, str):
    return obj

  if obj == 'null':
    return None

  if re.match(r'^\s*true\s*$', obj):
    return True

  if re.match(r'^\s*false\s*$', obj):
    return False

  if re.match(r'^\s*[+\-]?[0-9]+\s*$', obj):
    return int(obj)

  if re.match(r'^\s*[+\-]?([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)\s*$', obj):
    return float(obj)

  return obj

def any2str(obj: typing.Any) -> str:
  # TODO: define all conversion rules
  if obj is None:
    return 'null'

  if isinstance(obj, str):
    return obj

  if isinstance(obj, bool):
    return 'true' if obj else 'false'

  if isinstance(obj, int|float):
    return str(obj)

  try:
    return json.dumps(obj, default = str)
  except:
    return str(obj)

# TODO: add path-mgmt API
# TODO: add more checks and clean exceptions
# TODO: ensure name points exactly to a Callable function
FUNC_PATH: dict[str, str] = { }

@functools.cache
def func(name: str) -> typing.Callable:
  pair = name.split('.')
  if len(pair) == 1:
    mod = 'lwjs.funs'
    fun = name
  elif len(pair) == 2:
    mod = FUNC_PATH[pair[0]]
    fun = pair[1]
  else:
    raise ValueError()

  mod = importlib.import_module(mod)
  return getattr(mod, fun)
