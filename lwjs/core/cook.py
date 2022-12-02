''' Recursive cooker '''

import lwjs.core.bone as bone
import lwjs.core.chop as chop
import lwjs.core.help as help

def cook(obj: help.ANY) -> help.ANY:
  if isinstance(obj, help.Aide):
    return cook_deep(obj.Root, obj)
  else:
    aid = help.Aide(obj)
    return cook_deep(obj, aid)

def cook_deep(obj: help.ANY, aid: help.Aide) -> help.ANY:
  if isinstance(obj, str):
    return cook_str(obj, aid)
  if isinstance(obj, help.MAP):
    return cook_map(obj, aid)
  if isinstance(obj, help.SEQ):
    return cook_seq(obj, aid)
  return obj

def cook_str(obj: str, aid: help.Aide) -> help.ANY:
  hit = id(obj)
  if hit in aid.Hits:
    return aid.Hits[hit]
  cut = roast(obj, aid)
  if isinstance(cut, str):
    aid.Hits[id(cut)] = cut
  else:
    cut = cook_deep(cut, aid)
  return cut

def cook_map(obj: help.MAP, aid: help.Aide) -> help.MAP:
  for key, val in obj.items():
    aid.Path.append(key)
    obj[key] = cook_deep(val, aid)
    aid.Path.pop()
  return obj

def cook_seq(obj: help.SEQ, aid: help.Aide) -> help.SEQ:
  for idx, val in enumerate(obj):
    aid.Path.append(val)
    obj[idx] = cook_deep(val, aid)
    aid.Path.pop()
  return obj

def roast(obj: str, aid: help.Aide) -> help.ANY:
  try:
    pin = chop.chop(obj)
  except Exception as e:
    raise help.BadCook('Unroastable', aid.Path, obj) from e
  return roast_deep(pin, aid)

def roast_deep(dot: bone.Dot, aid: help.Aide) -> help.ANY:
  if isinstance(dot, bone.PAQ):
    return roast_paq(dot, aid)
  if isinstance(dot, bone.Kit):
    return roast_kit(dot, aid)
  if isinstance(dot, bone.Raw):
    return roast_raw(dot, aid)
  if isinstance(dot, bone.Sub):
    return roast_sub(dot, aid)
  if isinstance(dot, bone.Fun):
    return roast_fun(dot, aid)
  raise help.Bugster()

def roast_paq(paq: bone.PAQ, aid: help.Aide) -> help.ANY:
  if len(paq) == 1:
    data = roast_deep(paq[0], aid)
    return aid.str2any(data) if isinstance(paq, bone.Arg) else data
  line = ''
  for dot in paq:
    data = roast_deep(dot, aid)
    line += aid.any2str(data)
  return line

def roast_kit(kit: bone.Kit, aid: help.Aide) -> list[help.ANY]:
  return [ roast_paq(paq, aid) for paq in kit ]

def roast_raw(raw: bone.Raw, aid: help.Aide) -> str:
  return raw.Raw

def roast_sub(sub: bone.Sub, aid: help.Aide) -> help.ANY:
  here = aid.Root
  path = roast_kit(sub.Sub, aid)
  if path in aid.Crcs:
    raise help.BadCook('Circular ref', aid.Path, f'${{{".".join(path)}}}')
  aid.Crcs.append(path)
  for idx, key in enumerate(path):
    key = navigate(here, idx, key, aid)
    val = here[key]
    if isinstance(val, str):
      val = cook_str(val, aid)
      here[key] = val
    here = here[key]
  aid.Crcs.pop()
  return here

def navigate(obj: help.ANY, idx: int, key: str, aid: help.Aide) -> str|int:
  # expect a valid int index for SEQ
  if isinstance(obj, help.SEQ):
    try:
      ikey = int(key)
    except Exception as e:
      msg = f'Expected "int" at sub[{idx}]. Got "{key}"'
      raise help.BadCook(msg, aid.Path, key) from e
    if ikey < 0 or ikey >= len(obj):
      msg = f'Index "{key}" at sub[{idx}] is out of bounds'
      raise help.BadCook(msg, aid.Path, 'TODO:')
    return ikey
  # expect a valid str key for MAP
  if isinstance(obj, help.MAP):
    if key not in obj:
      msg = f'Missing key "{key}" at sub[{idx}]'
      raise help.BadCook(msg, aid.Path, 'TODO:')
    return key
  # other types are not supported
  msg = f'Bad type "{type(obj).__name__}" at sub[{idx}]'
  raise help.BadCook(msg, aid.Path, 'TODO:')

def roast_fun(fun: bone.Fun, aid: help.Aide) -> help.ANY:
  name = roast_paq(fun.Name, aid)
  args = roast_kit(fun.Args, aid)
  func = aid.func(name)
  return func(*args)
