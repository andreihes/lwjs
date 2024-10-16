import os
import json
import pytest

import lwjs.core.cook as cook

@pytest.mark.parametrize(
['d', 'r'],
[
  ("$(calc 1+11)", 12),
  ("$(calc 1 + 11)", 12),
  ("$(calc 1 + 11  )", 12),
  ("$(  calc 1 + 11  )", 12),
  ("$(calc 2*2)", 4),
  ("$(calc 2/2)", 1),
  ("$(calc '(2 + 2) * 2')", 8),
  ("$(calc 2 + 2 * 2)", 6)
])
def test_calc(d, r):
  v = cook.cook(d)
  assert v == r

@pytest.mark.parametrize(
  ['d', 'r'],
  [
    ('', None),
    ('today + 0 d', None),
    ('today+0d', None),
    ('2000-01-01 +10 days', '2000-01-11'),
    ('2000-01-31 +1 month', '2000-02-29'),
    ('2001-01-31 +1 month', '2001-02-28'),
    ('2000-12-31 -1 month', '2000-11-30'),
    ('2000-12-30 -1 month', '2000-11-30'),
    ('2000-02-29 +1 year', '2001-02-28')
  ]
)
def test_date(d, r):
  s = '$(date ' + d + ')'
  v = cook.cook(s)
  if r is not None:
    assert v == r

def test_dump():
  d = "$(dump 1 '2' x 'a b')"
  v = cook.cook(d)
  assert v == [{'int': 1}, {'str': '2'}, {'str': 'x'}, {'str': 'a b'}]

def test_env_pass():
  d = "$(env SOME_NON_EXISTING_VARIABLE x)"
  v = cook.cook(d)
  assert v == 'x'

@pytest.mark.parametrize('v', ['', 'null'])
@pytest.mark.xfail(raises = KeyError, strict = True)
def test_env_fail(v):
  d = f"$(env SOME_NON_EXISTING_VARIABLE {v})"
  cook.cook(d)

def test_false():
  d = { 'k1': '$(false)', 'k2': '[$(false)]' }
  v = cook.cook(d)
  assert v == { 'k1': False, 'k2': '[false]' }

def test_json_pass():
  d = '$(json \'{ "k1": 1, "k2": [ 1, 2, { "sk1": true } ] }\')'
  v = cook.cook(d)
  assert v == { 'k1': 1, 'k2': [ 1, 2, { 'sk1': True } ] }

@pytest.mark.xfail(raises = json.decoder.JSONDecodeError, strict = True)
def test_json_fail():
  d = '$(json \' { "no closing": true \')'
  cook.cook(d)

def test_map():
  d = { 'lst': ['yesterday', 'today', 'tomorrow'], 'r': "$(map $(@date) ${lst})" }
  cook.cook(d)
  d = { 'lst': ['2020-01-01 + 1m', '1900-12-31 + 1d'], 'r': "$(map $(@date) ${lst})" }
  v = cook.cook(d)
  assert v['r'] == [ '2020-02-01', '1901-01-01' ]

def test_nvl():
  d = { 'k1': 'v1', 'k2': None, 'k3': 'v3' }
  v = cook.cook({'d': d, 'r': '$(nvl ${d.k1} ${d.k2} ${d.k3})'})
  assert v['r'] == 'v1'
  v = cook.cook({'d': d, 'r': '$(nvl ${d.k3} ${d.k2} ${d.k1})'})
  assert v['r'] == 'v3'
  v = cook.cook({'d': d, 'r': '$(nvl ${d.k2} ${d.k3} ${d.k1})'})
  assert v['r'] == 'v3'
  v = cook.cook({'d': d, 'r': '$(nvl ${d.k2} ${d.k1} ${d.k3})'})
  assert v['r'] == 'v1'
  v = cook.cook({'d': d, 'r': '$(nvl ${d.k1} ${d.k3} ${d.k2})'})
  assert v['r'] == 'v1'
  v = cook.cook({'d': d, 'r': '$(nvl ${d.k3} ${d.k1} ${d.k2})'})
  assert v['r'] == 'v3'

def test_read():
  d = f"$(read '{__file__}')"
  v = cook.cook(d)
  assert type(v) == str and v.count('def test_read()') > 0

def test_true():
  d = { 'k1': '$(true)', 'k2': '[$(true)]' }
  v = cook.cook(d)
  assert v == { 'k1': True, 'k2': '[true]' }

def test_void():
  d = { 'k1': '$(void)', 'k2': '[$(void)]' }
  v = cook.cook(d)
  assert v == { 'k1': None, 'k2': '[null]' }
