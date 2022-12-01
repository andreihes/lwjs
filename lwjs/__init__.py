import lwjs.core.bone
import lwjs.core.chop
import lwjs.core.util
import lwjs.core.cook

def chop(line: str) -> lwjs.core.bone.Pin:
  return lwjs.core.chop.chop(line)

def cook(root: lwjs.core.util.ANY) -> lwjs.core.util.ANY:
  return lwjs.core.cook.cook(root)
