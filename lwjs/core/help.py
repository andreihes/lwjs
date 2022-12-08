''' Helpful stuff '''

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
    self.Dofr: bool = False
    self.Path: list[str] = [ ]
    self.Hits: dict[int, str] = { }
    self.Refs: dict[str, str] = { }
    self.Crcs: list[list[str]] = [ ]

def load(aid: Aid, name: str) -> tuple[bool, FUN]:
  call = True
  if name[0] != '@':
    pair = name.split('.')
  else:
    call = False
    pair = name[1:].split('.')

  pair = name.split('.')
  if len(pair) == 1:
    nmod = 'lwjs.funs.' + pair[0]
    nfun = pair[0]
  elif len(pair) == 2:
    if pair[0] in aid.Refs:
      nmod = aid.Refs[pair[0]]
      nfun = pair[1]
    else:
      raise KeyError(f'Key "{pair[0]}" is missing in "Refs" for "{name}"')
  else:
    raise ValueError(f'Bad fun "{name}": unexpected number of separators')

  try:
    mod = importlib.import_module(nmod)
  except Exception as e:
    raise ValueError(f'Error importing module "{nmod}" for "{name}"') from e

  try:
    fun = getattr(mod, nfun)
  except Exception as e:
    raise ValueError(f'Error getting fun "{nfun}" for "{name}"') from e

  if not isinstance(fun, FUN):
    raise TypeError(f'Not a fun "{nfun}" for "{name}"')

  return call, fun

def nget(aid: Aid, obj: ANY, key: str) -> ANY:
  if isinstance(obj, SEQ):
    try:
      ikey = int(key)
    except Exception as e:
      raise TypeError('Expected "int". Got "{key}"') from e
    if ikey < 0 or ikey >= len(obj):
      raise IndexError('Index "{ikey}" is out of bounds')
    return obj[ikey]
  if isinstance(obj, MAP):
    if key not in obj:
      raise KeyError(f'Key "{key}" is missing')
    return obj[key]
  raise TypeError(f'Unsupported "nget" type "{type(obj).__name__}"')

def nset(aid: Aid, obj: ANY, key: str, val: ANY) -> None:
  if isinstance(obj, SEQ):
    obj[int(key)] = val
    return
  if isinstance(obj, MAP):
    obj[key] = val
    return
  raise TypeError(f'Unsupported "nset" type "{type(obj).__name__}"')

def to_any(aid: Aid, obj: str) -> ANY:
  if re.match(r'^$', obj):
    return None
  if re.match(r'^null$', obj):
    return None
  if re.match(r'^true$', obj):
    return True
  if re.match(r'^false$', obj):
    return False
  if re.match(r'^[\+\-]?[0-9]+$', obj):
    return int(obj)
  if re.match(r'^[\+\-]?([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)$', obj):
    return float(obj)
  return obj

def to_str(aid: Aid, obj: ANY) -> str:
  if obj is None:
    return 'null'
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
    self._load: FUN[[Aid, str], tuple[bool, FUN]] = load
    self._nget: FUN[[Aid, ANY, str], ANY] = nget
    self._nset: FUN[[Aid, ANY, str, ANY], None] = nset
    self._to_any: FUN[[Aid, str], ANY] = to_any
    self._to_str: FUN[[Aid, ANY], str] = to_str

  @functools.cache
  def load(self, name: str) -> tuple[bool, FUN]:
    return self._load(self, name)

  def nget(self, obj: ANY, key: str) -> ANY:
    return self._nget(self, obj, key)

  def nset(self, obj: ANY, key: str, val: ANY) -> None:
    self._nset(self, obj, key, val)

  def to_any(self, obj: str) -> ANY:
    return self._to_any(self, obj)

  def to_str(self, obj: ANY) -> str:
    return self._to_str(self, obj)

  def set_load(self, load: FUN[[Aid, str], tuple[bool, FUN]]) -> None:
    self._load = load

  def set_nget(self, nget: FUN[[Aid, ANY, str], ANY]) -> None:
    self._nget = nget

  def set_nset(self, nset: FUN[[Aid, ANY, str, ANY], None]) -> None:
    self._nset = nset

  def set_to_any(self, to_any: FUN[[Aid, str], ANY]) -> None:
    self._to_any = to_any

  def set_to_str(self, to_str: FUN[[Aid, ANY], str]) -> None:
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
