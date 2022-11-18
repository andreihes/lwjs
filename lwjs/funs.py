import typing

def void() -> None:
  return None

def false() -> bool:
  return False

def true() -> bool:
  return True

def dump(*args) -> list:
  data = [ ]
  for arg in args:
    name = type(arg).__name__
    data.append({ name: arg })
  return data

def nvl(*args) -> typing.Any:
  for arg in args:
    if arg is not None:
      return arg
  return None
