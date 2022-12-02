'''
Parses all input as JSON
'''

import json as real_json

def json(text: str|None) -> dict|list|str|None:
  if text is None:
    return None
  else:
    return real_json.loads(text)
