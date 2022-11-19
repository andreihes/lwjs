import typing

import lwjs.bone as bone
import lwjs.chop as chop
import lwjs.util as util

def cook(root: typing.Any) -> typing.Any:
  ctx = util.Context(root)
  return cook_deep(root, ctx)

def cook_deep(obj: typing.Any, ctx: util.Context):
  if isinstance(obj, str):
    return cook_str(obj, ctx)
  if isinstance(obj, typing.MutableMapping):
    return cook_map(obj, ctx)
  if isinstance(obj, typing.MutableSequence):
    return cook_lst(obj, ctx)
  return obj

def cook_str(obj: str, ctx: util.Context):
  hit = id(obj)
  if hit in ctx.Hits:
    return ctx.Hits[hit]
  data = roast(obj, ctx)
  if isinstance(data, str):
    ctx.Hits[id(data)] = data
  else:
    data = cook_deep(data, ctx)
  return data

def cook_map(obj: typing.MutableMapping, ctx: util.Context):
  for key, val in obj.items():
    ctx.Path.append(key)
    obj[key] = cook_deep(val, ctx)
    ctx.Path.pop()
  return obj

def cook_lst(obj: typing.MutableSequence, ctx: util.Context):
  for idx, val in enumerate(obj):
    ctx.Path.append(str(idx))
    obj[idx] = cook_deep(val, ctx)
    ctx.Path.pop()
  return obj

def roast(obj: str, ctx: util.Context):
  try:
    pin = chop.chop(obj)
  except util.BadChop as e:
    # TODO: add ctx.Path information
    raise Exception() from e
  return roast_deep(pin, ctx)

def roast_deep(dot: bone.Dot, ctx: util.Context):
  if isinstance(dot, util.PAQ):
    return roast_paq(dot, ctx)
  if isinstance(dot, bone.Kit):
    return roast_kit(dot, ctx)
  if isinstance(dot, bone.Raw):
    return dot.Raw
  if isinstance(dot, bone.Sub):
    return roast_sub(dot, ctx)
  if isinstance(dot, bone.Fun):
    return roast_fun(dot, ctx)
  # TODO: non-reachable
  raise TypeError()

def roast_paq(paq: bone.Pin|bone.Arg|bone.Quo, ctx: util.Context):
  if len(paq) == 1:
    data = roast_deep(paq[0], ctx)
    if isinstance(paq, bone.Arg):
      return util.try2pri(data)
    else:
      return data
  line = ''
  for dot in paq:
    data = roast_deep(dot, ctx)
    line += util.any2str(data)
  return line

def roast_kit(kit: bone.Kit, ctx: util.Context):
  return [ roast_paq(paq, ctx) for paq in kit ]

def roast_sub(sub: bone.Sub, ctx: util.Context):
  here = ctx.Root
  for key in roast_kit(sub.Sub, ctx):
    # TODO: keep updating ctx.Path properly
    # TODO: check key exist and raise with ctx.Path if not
    if isinstance(here, typing.MutableSequence):
      key = int(key)
      val = here[key]
      if isinstance(val, str):
        val = cook_str(val, ctx)
        here[key] = val
      here = here[key]
    elif isinstance(here, typing.MutableMapping):
      val = here[key]
      if isinstance(val, str):
        val = cook_str(val, ctx)
        here[key] = val
      here = here[key]
    else:
      raise TypeError()
  return here

def roast_fun(fun: bone.Fun, ctx: util.Context):
  name = roast_paq(fun.Name, ctx)
  args = roast_kit(fun.Args, ctx)
  func = util.func(name)
  return func(*args)
