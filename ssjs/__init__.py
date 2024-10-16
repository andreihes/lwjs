import typing
import ssjs.base as base
import ssjs.depo as depo


def init() -> None:
    '''send all ssjs-naative kinds to depo'''

    depo.pkg('ssjs.kind', 'ssjs')


@typing.overload
def more(*, pfx: str, pn: str) -> None:
    '''send all kinds from `pn` package to depo with `pfx` prefix'''
    ...


@typing.overload
def more(*, pfx: str, mn: str) -> None:
    '''send all kinds from `mn` module to depo with `pfx` prefix'''
    ...


@typing.overload
def more(*, pfx: str, cls: type[base.Knd]) -> None:
    '''send `cls` kind to depo with `pfx` prefix'''
    ...


def more(**kwargs) -> None:
    pfx = kwargs['pfx']
    if pn := kwargs.get('pn'):
        return depo.pkg(pn, pfx)
    if mn := kwargs.get('mn'):
        return depo.mod(mn, pfx)
    if cls := kwargs.get('cls'):
        return depo.knd(cls, pfx)
