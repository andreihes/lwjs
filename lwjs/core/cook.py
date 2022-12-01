''' Recursive cooker '''

import lwjs.core.bone as bone
import lwjs.core.chop as chop
import lwjs.core.util as util

def cook(aid: util.Aide) -> util.ANY:
  return cook_deep(aid.Root, aid)

def cook_deep(obj: util.ANY, aid: util.Aide) -> util.ANY:
  if isinstance(obj, str):
    return cook_str(obj, aid)
  if isinstance(obj, util.MAP):
    return cook_map(obj, aid)
  if isinstance(obj, util.SEQ):
    return cook_seq(obj, aid)
  return obj

def cook_str(obj: str, aid: util.Aide) -> util.ANY:
  hit = id(obj)
  if hit in aid.Hits:
    return aid.Hits[hit]
  cut = roast(obj, aid)
  if isinstance(cut, str):
    aid.Hits[id(cut)] = cut
  else:
    cut = cook_deep(cut, aid)
  return cut

def cook_map(obj: util.MAP, aid: util.Aide) -> util.MAP:
  for key, val in obj.items():
    aid.Path.append(key)
    obj[key] = cook_deep(val, aid)
    aid.Path.pop()
  return obj

def cook_seq(obj: util.SEQ, aid: util.Aide) -> util.SEQ:
  for idx, val in enumerate(obj):
    aid.Path.append(str(idx))
    obj[idx] = cook_deep(val, aid)
    aid.Path.pop()
  return obj

def roast(obj: str, aid: util.Aide) -> util.ANY:
  try:
    pin = chop.chop(obj)
  except Exception as e:
    raise util.BadCook('Unroastable', aid.Path) from e
  return roast_deep(pin, aid)

def roast_deep(dot: bone.Dot, aid: util.Aide) -> util.ANY:
  if isinstance(dot, bone.PAQ):
    return roast_paq(dot, aid)
  if isinstance(dot, bone.Kit):
    return roast_kit(dot, aid)
  if isinstance(dot, bone.Raw):
    return dot.Raw
  if isinstance(dot, bone.Sub):
    return roast_sub(dot, aid)
  if isinstance(dot, bone.Fun):
    return roast_fun(dot, aid)
  raise util.Bugster()

def roast_paq(paq: bone.PAQ, aid: util.Aide) -> util.ANY:
  if len(paq) == 1:
    data = roast_deep(paq[0], aid)
    return aid.str2any(data) if isinstance(paq, bone.Arg) else data
  line = ''
  for dot in paq:
    data = roast_deep(dot, aid)
    line += aid.any2str(data)
  return line

def roast_kit(kit: bone.Kit, aid: util.Aide) -> list[util.ANY]:
  return [ roast_paq(paq, aid) for paq in kit ]

def roast_sub(sub: bone.Sub, aid: util.Aide) -> util.ANY:
  here = aid.Root
  for key in roast_kit(sub.Sub, aid):
    if isinstance(here, util.SEQ):
      key = int(key)
      val = here[key]
      if isinstance(val, str):
        val = cook_str(val, aid)
        here[key] = val
      here = here[key]
    elif isinstance(here, util.MAP):
      val = here[key]
      if isinstance(val, str):
        val = cook_str(val, aid)
        here[key] = val
      here = here[key]
    else:
      raise util.BadCook(f'Unable to sub on "{key}"', aid.Path)
  return here

def roast_fun(fun: bone.Fun, aid: util.Aide) -> util.ANY:
  name = roast_paq(fun.Name, aid)
  args = roast_kit(fun.Args, aid)
  func = aid.func(name)
  return func(*args)
