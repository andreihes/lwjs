import lwjs.core.help as help

omap = map

def map(func: help.FUN, *iters: help.SEQ) -> help.SEQ:
  return list(omap(func, *iters))
