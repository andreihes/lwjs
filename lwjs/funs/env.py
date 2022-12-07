import os

def env(name: str, default: str|None = None) -> str:
  if (value := os.environ.get(name, default)) is None:
    raise KeyError(f'No env var "{name}" exists')
  return value
