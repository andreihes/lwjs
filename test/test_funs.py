import pytest

import lwjs.core.cook as cook

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
