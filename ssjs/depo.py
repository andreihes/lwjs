import pkgutil
import inspect
import importlib
import ssjs.base as base


DEPO: dict[str, type[base.Kind]] = {}


def pkg(pn: str, pfx: str) -> None:
    for m in pkgutil.iter_modules([pn.replace('.', '/')]):
        nn = f'{pn}.{m.name}'
        if m.ispkg:
            pkg(nn, pfx)
        else:
            mod(nn, pfx)


def mod(mn: str, pfx: str) -> None:
    m = importlib.import_module(mn)
    for _, clazz in inspect.getmembers(m, inspect.isclass):
        if issubclass(clazz, base.Kind) and hasattr(clazz, '__ssjs.kind__'):
            knd(clazz, pfx)


def knd(cls: type[base.Knd], pfx: str) -> None:
    if not pfx:
        raise ValueError('pfx is null or empty')

    cn = cls.__name__
    cm = cls.__module__
    ck = getattr(cls, '__ssjs.kind__', None)
    cr = pfx in ('ssjs', 'kind', 'ssjs.kind') or pfx.startswith('ssjs.kind.')

    if cm.startswith('ssjs.') != cr:  # xor xD
        raise ValueError(f'pfx "{pfx}" is not okay for "ssjs.*" kinds')

    if cm.startswith('ssjs.') and cr:
        raise ValueError(f'pfx "{pfx}" is reserved for "ssjs.kind.*" kinds')

    if not issubclass(cls, base.Kind):
        raise TypeError(f'kind "{cm}.{cn}" must subclass "ssjs.base.Kind"')

    if not ck:
        raise AttributeError(f'kind "{cm}.{cn}" misses "@ssjs.base.kind"')

    global DEPO
    if cr:
        DEPO[f'{ck}'] = cls
        DEPO[f'{cm}.{ck}'] = cls
        DEPO[f'ssjs.{ck}'] = cls
        DEPO[f'kind.{ck}'] = cls
        DEPO[f'ssjs.kind.{ck}'] = cls
    else:
        DEPO[f'{pfx}.{ck}'] = cls
