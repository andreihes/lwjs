''' Potentially useful stuff '''

import re
import typing
import importlib
import functools

ANY = typing.Any
FUN = typing.Callable
MAP = typing.MutableMapping
SEQ = typing.MutableSequence

class Aide:
  def __init__(self, obj: ANY) -> None:
    self.Root: ANY = obj
    self.Path: list[str] = [ ]
    self.Hits: dict[int, str] = { }
    self.Refs: dict[str, str] = { }

  def str2any(self, obj: None|str) -> ANY:
    if obj is None:
      return None
    if re.match(r'^\s*null\s*$', obj, re.IGNORECASE):
      return None
    if re.match(r'^\s*true\s*$', obj, re.IGNORECASE):
      return True
    if re.match(r'^\s*false\s*$', obj, re.IGNORECASE):
      return False
    if re.match(r'^\s*[+\-]?[0-9]+\s*$', obj):
      return int(obj)
    if re.match(r'^\s*[+\-]?([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)\s*$', obj):
      return float(obj)
    return obj

  def any2str(self, obj: None|ANY) -> str:
    if obj is None:
      return ''
    if isinstance(obj, str):
      return obj
    if isinstance(obj, bool):
      return 'true' if obj else 'false'
    if isinstance(obj, int|float):
      return str(obj)
    return str(obj)

  @functools.cache
  def func(self, name: str) -> FUN:
    pair = name.split('.')
    if len(pair) == 1:
      mod = 'lwjs.funs.' + name
      fun = name
    elif len(pair) == 2:
      mod = self.Refs[pair[0]]
      fun = pair[1]
    else:
      raise ValueError(f'Bad fun ref "{name}"')
    try:
      mod = importlib.import_module(mod)
    except Exception as e:
      raise ValueError(f'Unknown mod in fun ref: "{name}"') from e
    try:
      fun = getattr(mod, fun)
    except Exception as e:
      raise ValueError(f'Unknown fun in fun ref: "{name}"') from e
    if not isinstance(fun, FUN):
      raise ValueError(f'Fun ref is not a fun: "{name}"')
    return fun

class Bugster(Exception):
  def __init__(self) -> None:
    super().__init__('Looks like a bug. Who you gonna call?')

class BadChop(Exception):
  def __init__(self, msg: str, line: str, index: int) -> None:
    if len(line) > 60:
      line = '...' + line[index - 20:index + 20] + '...'
    super().__init__(f'{msg}. Index {index}: "{line}"')

class BadCook(Exception):
  def __init__(self, msg: str, path: list[str]) -> None:
    super().__init__(f'{msg}. Path: {"/".join(path)}')
