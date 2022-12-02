import lwjs.core.bone
import lwjs.core.chop
import lwjs.core.help
import lwjs.core.cook

def chop(line: str) -> lwjs.core.bone.Pin:
  return lwjs.core.chop.chop(line)

def cook(data: lwjs.core.help.ANY) -> lwjs.core.help.ANY:
  return lwjs.core.cook.cook(data)
