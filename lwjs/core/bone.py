''' AST '''

class Dot:
  pass

class Pin(Dot, list[Dot]):
  pass

class Arg(Dot, list[Dot]):
  pass

class Quo(Dot, list[Dot]):
  pass

PAQ = Pin | Arg | Quo

class Kit(Dot, list[PAQ]):
  pass

class Raw(Dot):
  def __init__(self, raw: str):
    self.Raw: str = raw

class Sub(Dot):
  def __init__(self, sub: Kit):
    self.Sub: Kit = sub

class Fun(Dot):
  def __init__(self, name: Pin, args: Kit):
    self.Name: Pin = name
    self.Args: Kit = args

RSF = Raw | Sub | Fun
