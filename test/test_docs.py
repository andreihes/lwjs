import importlib

import lwjs

class Helper:
  @staticmethod
  def fun(arg: str) -> str:
    return f'I am Helper.fun("{arg}")'

def my_load(aid: lwjs.Aid, name: str) -> tuple[bool, lwjs.FUN]:
  tokens = name.rsplit('.', 3)
  if len(tokens) < 3:
    raise ValueError('Bad class method reference for fun')
  module = importlib.import_module('.'.join(tokens[:-2]))
  classo = getattr(module, tokens[-2])
  method = getattr(classo, tokens[-1])
  return True, method

def to_any(aid: lwjs.Aid, obj: str) -> lwjs.ANY:
  if obj == 'HUNDRED':
    return 100
  else:
    return obj

def to_str(aid: lwjs.Aid, obj: lwjs.ANY) -> str:
  return type(obj).__name__

def test_001():
  data = "$(calc 5 + 5)"
  data = lwjs.cook(data)
  assert data == 10

  data = { "tasks": [ "1+1", "2+2" ], "solve": "$(map $(@calc) ${tasks})" }
  data = lwjs.cook(data)
  assert data == { "tasks": [ "1+1", "2+2" ], "solve": [2, 4] }

  data = { "in": { "v1": 2, "v2": 5 }, "r": "$(calc ${in.v1} + ${in.v2})" }
  data = lwjs.cook(data)
  assert data == { "in": { "v1": 2, "v2": 5 }, "r": 7 }

  data = "Must escape '$$' character"
  data = lwjs.cook(data)
  assert data == "Must escape '$' character"

def test_002():
  aid = lwjs.Aide()
  aid.Refs['J'] = 'json'
  aid.Refs['O'] = 'os'
  data = "$( J.loads '[1, 2, 3]' )"
  data = lwjs.cook(data, aid)
  assert data == [1, 2, 3]

  data = "$(O.cpu_count)"
  data = lwjs.cook(data, aid)
  assert data is None or type(data) == int

def test_003():
  aid = lwjs.Aide()
  aid.set_load(my_load)
  data = f'$({__name__}.Helper.fun hello)'
  data = lwjs.cook(data, aid)
  assert data == 'I am Helper.fun("hello")'

def test_004():
  data = "$(dump HUNDRED)"
  aid = lwjs.Aide()
  aid.set_to_any(to_any)
  data = lwjs.cook(data, aid)
  assert data == [{ 'int': 100 }]

def test_005():
  data = "$(void) hello $(void)"
  aid = lwjs.Aide()
  aid.set_to_str(to_str)
  data = lwjs.cook(data, aid)
  assert data == 'NoneTypestrNoneType'
