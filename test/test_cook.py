import pytest

import lwjs

@pytest.mark.parametrize(
  ['v', 't', 'e'],
  [
    ('value', str, 'value'),
    ('$(false)', bool, False),
    ('[$(false)]', str, '[false]')
  ]
)
def test_001(v, t, e):
  r = lwjs.cook(v)
  assert isinstance(r, t)
  assert r == e
