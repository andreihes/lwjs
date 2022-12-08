''' Recursive cooker '''

import lwjs.core.bone as bone
import lwjs.core.chop as chop
import lwjs.core.help as help

def cook(obj: help.ANY, aid: help.Aide|None = None) -> help.ANY:
  if aid is None:
    aid = help.Aide()
  aid.Root = obj
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
    pin = chop.chop(obj, aid.Dofr)
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
    if isinstance(paq, bone.Arg):
      if isinstance(data, str):
        data = aid.to_any(data)
    return data
  line = ''
  for dot in paq:
    data = roast_deep(dot, aid)
    line += aid.to_str(data)
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
    try:
      val = aid.nget(here, key)
    except Exception as e:
      msg = f'Sub error on index "{idx}", key "{key}"'
      raise help.BadCook(msg, aid.Path, f'${{{".".join(path)}}}') from e
    if isinstance(val, str):
      val = cook_str(val, aid)
      aid.nset(here, key, val)
    here =  aid.nget(here, key)
  aid.Crcs.pop()
  return here

def roast_fun(fun: bone.Fun, aid: help.Aide) -> help.ANY:
  name = roast_paq(fun.Name, aid)
  args = roast_kit(fun.Args, aid)
  call, func = aid.load(name)
  if call:
    return func(*args)
  else:
    return func
