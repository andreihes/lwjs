''' Build AST '''

import lwjs.core.bone as bone
import lwjs.core.help as help

def chop(line: str) -> bone.Pin:
  pin = bone.Pin()
  start, index = 0, 0
  while curr := line[index:index + 1]:
    # want a dollar
    if curr != '$':
      index += 1
      continue
    # got a dollar
    # only append non-empty raw dots
    if start < index:
      pin.append(bone.Raw(line[start:index]))
    rsf, index = chop_dlr(line, index)
    pin.append(rsf)
    start = index

  # append non-empty raw dot or append even
  # if it is empty in case the pin is empty
  if start < index or len(pin) == 0:
    pin.append(bone.Raw(line[start:index]))

  # finally pin holds AST for the line
  return pin

def chop_dlr(line: str, begin: int) -> tuple[bone.RSF, int]:
  # begin is on a confirmed '$' sequence
  next = line[begin + 1:begin + 2]

  # '$$' is an escaped raw '$'
  if next == '$':
    return bone.Raw('$'), begin + 2

  # '${' is an opening for a sub
  if next == '{':
    return chop_sub(line, begin)

  # '$(' is an opening for a fun
  if next == '(':
    return chop_fun(line, begin)

  # any other sequence means orphan '$'
  raise help.BadChop('Orphan "$"', line, begin)

def chop_sub(line: str, begin: int) -> tuple[bone.Sub, int]:
  # begin is on a confirmed '${' sequence
  kit, index = bone.Kit(), begin + 2
  while curr := line[index:index + 1]:
    # preserve empty raw pin and return
    if curr == '}':
      kit.append(bone.Pin([bone.Raw('')]))
      return bone.Sub(kit), index + 1

    # preserve empty raw pin and continue
    if curr == '.':
      kit.append(bone.Pin([bone.Raw('')]))
      index += 1
      continue

    # no '}' and no '.' starts a new pin
    if curr == "'":
      pin, index = chop_quote(bone.Pin(), line, index)
    else:
      pin, index = chop_plain(bone.Pin(), line, index, '.}')

    # update kit
    kit.append(pin)
    curr = line[index:index + 1]

    # check if we hit end of sub
    if curr == '}':
      return bone.Sub(kit), index + 1

    # check if there is another pin to continue
    if curr == '.':
      index += 1
      continue

    # any other sequence is unexpected here
    raise help.Bugster()

  # unbalanced sub
  raise help.BadChop('Unbalanced "${"', line, begin)

def chop_fun(line: str, begin: int) -> tuple[bone.Fun, int]:
  # begin is on a confirmed '$(' sequence
  name, args, index = bone.Pin(), bone.Kit(), begin + 2
  while curr := line[index:index + 1]:
    # verify name is not empty and done
    if curr == ')':
      if len(name) == 0:
        raise help.BadChop('Empty "$()"', line, begin)
      return bone.Fun(name, args), index + 1

    # skip whitespace
    if curr == ' ':
      index += 1
      continue

    # init name or collect args
    if len(name) == 0:
      if curr == "'":
        paq, index = chop_quote(name, line, index)
      else:
        paq, index = chop_plain(name, line, index, ' )')
    else:
      if curr == "'":
        paq, index = chop_quote(bone.Quo(), line, index)
      else:
        paq, index = chop_plain(bone.Arg(), line, index, ' )')
      args.append(paq)

  # unbalanced fun
  raise help.BadChop('Unbalanced "$("', line, begin)

def chop_quote(paq: bone.PAQ, line: str, begin: int) -> tuple[bone.PAQ, int]:
  # begin is on a confirmed "'" sequence inside of fun or sub
  start = index = begin + 1
  while curr := line[index:index + 1]:
    if curr == '$':
      if start < index:
        paq.append(bone.Raw(line[start:index]))
      rsf, index = chop_dlr(line, index)
      paq.append(rsf)
      start = index
    elif curr == "'":
      next = line[index + 1:index + 2]
      if next == "'":
        if start < index:
          paq.append(bone.Raw(line[start:index]))
        paq.append(bone.Raw("'"))
        index += 2
        start = index
      else:
        paq.append(bone.Raw(line[start:index]))
        return paq, index + 1
    else:
      index += 1

  # unexpected end of input
  raise help.BadChop('Unbalanced quote', line, begin)

def chop_plain(paq: bone.PAQ, line: str, begin: int, seps: str) -> tuple[bone.PAQ, int]:
  # begin is on a confirmed non-"'" sequence inside of fun or sub
  start = index = begin
  while curr := line[index:index + 1]:
    if curr == '$':
      if start < index:
        paq.append(bone.Raw(line[start:index]))
      rsf, index = chop_dlr(line, index)
      paq.append(rsf)
      start = index
    elif curr in seps:
      if start < index:
        paq.append(bone.Raw(line[start:index]))
      return paq, index
    else:
      index += 1

  # unexpected end of input
  raise help.BadChop('Unbalanced plain', line, begin)
