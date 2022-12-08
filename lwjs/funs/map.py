import lwjs.core.help as help

real_map = map

def map(func: help.FUN, *iters: help.SEQ) -> help.SEQ:
  return list(real_map(func, *iters))
