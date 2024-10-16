import re
import pytest
import ssjs.args as args


@pytest.mark.parametrize('val', ['42', 42, True, 42.42])
def test_str_pass(val) -> None:
    astr = args.Str(val)
    assert astr == str(val)
    assert type(astr) is args.Str


@pytest.mark.parametrize('val', [[], {}, None])
def test_str_fail_terr(val) -> None:
    with pytest.raises(TypeError, match='invalid argument type'):
        args.Str(val)


@pytest.mark.parametrize('val', ['^[a-z]+$'])
def test_rex_pass(val) -> None:
    arex = args.Rex(val)
    assert arex == val
    assert type(arex) is args.Rex
    assert isinstance(arex.rex, re.Pattern)


@pytest.mark.parametrize('val', [42, True, 42.42, [], {}, None])
def test_rex_fail_terr(val) -> None:
    with pytest.raises(TypeError, match='invalid argument type'):
        args.Rex(val)


def test_rex_fail_verr() -> None:
    with pytest.raises(ValueError, match='invalid argument value'):
        args.Rex('^[a-z$')


@pytest.mark.parametrize('val', ['42', 42, True, 42.42])
def test_int_pass(val) -> None:
    aint = args.Int(val)
    assert aint == int(val)
    assert type(aint) is args.Int


@pytest.mark.parametrize('val', [[], {}, None])
def test_int_fail_terr(val) -> None:
    with pytest.raises(TypeError, match='invalid argument type'):
        args.Int(val)


def test_int_fail_verr() -> None:
    with pytest.raises(ValueError, match='invalid argument value'):
        args.Int('x42x')


@pytest.mark.parametrize('val', ['42', 42, True, 42.42])
def test_flt_pass(val) -> None:
    aflt = args.Flt(val)
    assert aflt == pytest.approx(float(val))
    assert type(aflt) is args.Flt


@pytest.mark.parametrize('val', [[], {}, None])
def test_flt_fail_terr(val) -> None:
    with pytest.raises(TypeError, match='invalid argument type'):
        args.Flt(val)


def test_flt_fail_verr() -> None:
    with pytest.raises(ValueError, match='invalid argument value'):
        args.Flt('42.x42x')


@pytest.mark.parametrize('val', ['true', 'yes', 't', 'y', 'sure', '42', '42.42', 42, True, 42.42])
def test_flg_pass_1(val) -> None:
    aflg = args.Flg(val)
    assert aflg == 1
    assert type(aflg) is args.Flg


@pytest.mark.parametrize('val', ['false', 'no', 'f', 'n', 'nope', '0', '0.0', 0, False, 0.0])
def test_flg_pass_0(val) -> None:
    aflg = args.Flg(val)
    assert aflg == 0
    assert type(aflg) is args.Flg


@pytest.mark.parametrize('val', [[], {}, None])
def test_flg_fail_terr(val) -> None:
    with pytest.raises(TypeError, match='invalid argument type'):
        args.Flg(val)


def test_flg_fail_verr() -> None:
    with pytest.raises(ValueError, match='invalid argument value'):
        args.Flt('42.x42x')


def test_lst_pass() -> None:
    l1 = args.Lst[args.Int]([1, '2'])
    assert l1 == [1, 2]
    assert type(l1) is args.Lst

    l2 = args.Lst[args.Str](('3', 4))
    assert l2 == ['3', '4']
    assert type(l2) is args.Lst

    l3 = args.Lst[args.Lst[args.Int]]([l1, l2])
    assert l3 == [[1, 2], [3, 4]]
    assert type(l3) is args.Lst

    l4 = args.Lst[args.Lst[args.Lst[args.Str]]]([l3, [('5', 6), [7, '8']]])
    assert l4 == [[['1', '2'], ['3', '4']], [['5', '6'], ['7', '8']]]
    assert type(l4) is args.Lst


@pytest.mark.parametrize('val', ['42', 42, True, 42.42, {}, None])
def test_lst_fail_terr(val) -> None:
    with pytest.raises(TypeError, match='invalid argument type'):
        args.Lst(val)


def test_lst_fail_targ() -> None:
    with pytest.raises(TypeError, match='no type args'):
        args.Lst([])

    with pytest.raises(TypeError, match='bad type arg'):
        args.Lst[int]([])  # type: ignore


def test_dct_pass() -> None:
    ...
