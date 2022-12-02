import pytest

import lwjs.core.cook as cook

@pytest.mark.parametrize(
  ['v', 't', 'e'],
  [
    ('value$$', str, 'value$'),
    ('$(false)', bool, False),
    ('[$(false)]', str, '[false]'),
    ('$(dump 1)', list, [{'int': 1}]),
    ('$(dump 1 2)', list, [{'int': 1}, {'int': 2}]),
    ("$(dump 1 '2')", list, [{'int': 1}, {'str': '2'}]),
    ('$(dump null)', list, [{'NoneType': None}])
  ]
)
def test_001(v, t, e):
  r = cook.cook(v)
  assert isinstance(r, t)
  assert r == e
