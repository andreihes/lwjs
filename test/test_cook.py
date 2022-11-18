import pytest
import datetime

import lwjs.cook as cook

@pytest.mark.parametrize(
  ['v', 't', 'e'],
  [
    ('value', str, 'value'),
    ('$(false)', bool, False),
    ('[$(false)]', str, '[false]')
  ]
)
def test_001(v, t, e):
  r = cook.cook(v)
  assert isinstance(r, t)
  assert r == e
