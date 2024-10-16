import abc
import typing


class Ctx:
    def __init__(self, data: object) -> None:
        self.data = data


class Fix:
    def __init__(self, msg: str) -> None:
        self.msg = msg


FixItr: typing.TypeAlias = typing.Iterator[Fix]


class Kind(abc.ABC):
    @abc.abstractmethod
    def __init__(self, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def fixes(self, ctx: Ctx) -> FixItr:
        pass


Knd = typing.TypeVar('Knd', bound=Kind)


def kind(name: str) -> typing.Callable[[type[Knd]], type[Knd]]:
    if not name:
        raise ValueError('kind name cannot be null or empty')

    def deco(clazz: type[Knd]) -> type[Knd]:
        if not issubclass(clazz, Kind):
            cn = clazz.__name__
            cm = clazz.__module__
            raise TypeError(f'class "{cm}.{cn}" is not a subclass of "ssjs.base.Kind"')
        setattr(clazz, '__ssjs.kind__', name)
        return clazz
    return deco
