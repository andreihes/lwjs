''' Potentially useful stuff '''

import re
import typing
import importlib
import functools

ANY = typing.Any
FUN = typing.Callable
MAP = typing.MutableMapping
SEQ = typing.MutableSequence

class Aid:
  def __init__(self) -> None:
    self.Root: ANY = None
    self.Path: list[str] = [ ]
    self.Hits: dict[int, str] = { }
    self.Refs: dict[str, str] = { }
    self.Crcs: list[list[str]] = [ ]

def func(aid: Aid, name: str) -> FUN:
  pair = name.split('.')
  if len(pair) == 1:
    mod = 'lwjs.funs.' + name
    fun = name
  elif len(pair) == 2:
    if pair[0] in aid.Refs:
      mod = aid.Refs[pair[0]]
      fun = pair[1]
    else:
      raise ValueError(f'Have you registered ref "{pair[0]}"?')
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

def to_any(aid: Aid, obj: None|str) -> ANY:
  if obj is None:
    return None
  if re.match(r'^\s*null\s*$', obj, re.IGNORECASE):
    return None
  if re.match(r'^\s*true\s*$', obj, re.IGNORECASE):
    return True
  if re.match(r'^\s*false\s*$', obj, re.IGNORECASE):
    return False
  if re.match(r'^\s*[+\-]?[0-9_]+\s*$', obj):
    return int(obj)
  if re.match(r'^\s*[+\-]?([0-9_]+\.[0-9_]*|[0-9_]*\.[0-9_]+)\s*$', obj):
    return float(obj)
  return obj

def to_str(aid: Aid, obj: None|ANY) -> str:
  if obj is None:
    return ''
  if isinstance(obj, str):
    return obj
  if isinstance(obj, bool):
    return 'true' if obj else 'false'
  if isinstance(obj, int|float):
    return str(obj)
  return str(obj)

class Aide(Aid):
  def __init__(self) -> None:
    super().__init__()
    self._func: FUN[[Aid, str], FUN] = func
    self._to_any: FUN[[Aid, None|str], ANY] = to_any
    self._to_str: FUN[[Aid, None|ANY], str] = to_str

  @functools.cache
  def func(self, name: str) -> FUN:
    return self._func(self, name)

  def to_any(self, obj: None|str) -> ANY:
    return self._to_any(self, obj)

  def to_str(self, obj: None|ANY) -> str:
    return self._to_str(self, obj)

  def set_func(self, func: FUN[[Aid, str], FUN]) -> None:
    self._func = func

  def set_to_any(self, to_any: FUN[[Aid, None|str], ANY]) -> None:
    self._to_any = to_any

  def set_to_str(self, to_str: FUN[[Aid, None|ANY], str]) -> None:
    self._to_str = to_str

class Bugster(Exception):
  def __init__(self) -> None:
    super().__init__('Looks like a bug. Who you gonna call?')

class BadChop(Exception):
  def __init__(self, msg: str, line: str, index: int) -> None:
    # TODO: shorten long lines
    super().__init__(f'{msg}. Index {index}: "{line}"')

class BadCook(Exception):
  def __init__(self, msg: str, path: list[str], val: str) -> None:
    # TODO: shorten long values
    super().__init__(f'{msg}: "' + '" -> "'.join(path) + f'": "{val}"')
