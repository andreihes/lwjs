import pytest

import lwjs.core.chop as chop
import lwjs.core.bone as bone
import lwjs.core.help as help

def test_empty():
  pins = chop.chop('')
  assert len(pins) == 1
  raw = pins[0]
  assert isinstance(raw, bone.Raw)
  assert raw.Raw == ''

@pytest.mark.parametrize('line', ['$$', '$$abc', 'abc$$', 'a$$$$b', 'abc $$$$$$ xyz'])
def test_pass_raws(line):
  outs = ''
  pins = chop.chop(line)
  for pin in pins:
    assert isinstance(pin, bone.Raw)
    outs += pin.Raw.replace('$', '$$')
  assert outs == line

@pytest.mark.xfail(raises = help.BadChop, strict = True)
@pytest.mark.parametrize('line', ['$', '$abc', 'abc$', 'a$$$b', 'abc $$$$$ xyz'])
def test_fail_raws(line):
  outs = ''
  pins = chop.chop(line)
  for pin in pins:
    assert isinstance(pin, bone.Raw)
    outs += pin.Raw.replace('$', '$$')
  assert outs == line
