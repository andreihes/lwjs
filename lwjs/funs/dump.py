def dump(*args) -> list:
  data = [ ]
  for arg in args:
    name = type(arg).__name__
    data.append({ name: arg })
  return data
