import re
import json
import typing
import importlib
import functools

class BadChop(Exception):
  def __init__(self, msg: str, line: str, index: int) -> None:
    # TODO: shorten long lines
    super().__init__(f'{msg}. Index {index}: "{line}"')
