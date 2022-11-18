import lwjs.bone as bone
import lwjs.util as util

def chop(line: str) -> bone.Pin:
  pin = bone.Pin()
  start, index = 0, 0
  while index < len(line) and (curr := line[index]):
    # want a dollar
    if curr != '$':
      index += 1
      continue
    # only append non-empty raw dots
    if start < index:
      pin.append(bone.Raw(line[start:index]))
    # got a dollar
    rsf, index = chop_dlr(line, index)
    pin.append(rsf)
    start = index

  # append non-empty raw dot or append even
  # if it is empty in case the pin is empty
  if start < index or len(pin) == 0:
    pin.append(bone.Raw(line[start:index]))

  # finally pin holds AST for the line
  return pin

def chop_dlr(line: str, begin: int) -> tuple[util.RSF, int]:
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
  raise util.BadChop('Orphan "$"', line, begin)

def chop_sub(line: str, begin: int) -> tuple[bone.Sub, int]:
  # begin is on a confirmed '${' sequence
  kit, index = bone.Kit(), begin + 2
  while index < len(line) and (curr := line[index]):
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
    raise util.BadChop('Looks like a bug', line, index)

  # unbalanced sub
  raise util.BadChop('Unbalanced "${"', line, begin)

def chop_fun(line: str, begin: int) -> tuple[bone.Fun, int]:
  # begin is on a confirmed '$(' sequence
  kit, index = bone.Kit(), begin + 2
  while index < len(line) and (curr := line[index]):
    # verify name is not empty and done
    if curr == ')':
      if len(kit) == 0:
        raise util.BadChop('Empty "$()"', line, begin)
      return bone.Fun(kit), index + 1

    # skip whitespace and continue
    if curr == ' ':
      index += 1
      continue

    # no ')' and no ' ' starts a new pin
    # it is pin for the function name
    # it is quo for a quoted function argument
    # it is arg for a non-quoted argument
    # the context preserved for basic type
    # conversions of the function args
    if curr == "'":
      paq = bone.Pin() if len(kit) == 0 else bone.Quo()
      paq, index = chop_quote(paq, line, index)
    else:
      paq = bone.Pin() if len(kit) == 0 else bone.Arg()
      paq, index = chop_plain(paq, line, index, ' )')
    kit.append(paq)

  # unbalanced fun
  raise util.BadChop('Unbalanced "$("', line, begin)

def chop_quote(paq: util.PAQ, line: str, begin: int) -> tuple[util.PAQ, int]:
  # begin is on a confirmed "'" sequence inside of fun or sub
  start = index = begin + 1
  while index < len(line) and (curr := line[index]):
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
  raise util.BadChop('Unbalanced "\'"', line, begin)

def chop_plain(paq: util.PAQ, line: str, begin: int, seps: str) -> tuple[util.PAQ, int]:
  # begin is on a confirmed non-"'" sequence inside of fun or sub
  start = index = begin
  while index < len(line) and (curr := line[index]):
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
  raise util.BadChop('Unbalanced "{sep}"', line, begin)
