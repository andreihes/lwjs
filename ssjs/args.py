import re
import abc
import typing
import inspect


ArgGen = typing.TypeVar('ArgGen')


class Arg(abc.ABC, typing.Generic[ArgGen]):
    @staticmethod
    def name(obj: object) -> str:
        if not inspect.isclass(obj):
            obj = obj.__class__

        return f'{obj.__module__}.{obj.__name__}'

    @staticmethod
    def terr(selv: object, fail: object, *okay: object) -> TypeError:
        msg = f'invalid argument type for "{Arg.name(selv)}()", it must be'
        msg = f'{msg} any ["{"\", \"".join([Arg.name(ok) for ok in okay])}"]'
        msg = f'{msg} and not "{Arg.name(fail)}" as it is now'
        return TypeError(msg)

    @staticmethod
    def verr(selv: object, val: object) -> ValueError:
        msg = f'invalid argument value for "{Arg.name(selv)}()",'
        msg = f'{msg} the value "{val}" cannot be properly recognized'
        return ValueError(msg)

    def okay(self, arg: type) -> bool:
        if isinstance(arg, type):
            return issubclass(arg, Arg)

        orig = getattr(arg, '__origin__', None)
        if orig and inspect.isclass(orig):
            return issubclass(orig, Arg)

        msg = f'cannot detect if type "{self.name(arg)}" of arg'
        msg = f'{msg} is a valid subclass of "{self.name(Arg)}"'
        raise TypeError(msg)

    def args(self) -> list[type]:
        args = []
        cufr = inspect.currentframe()

        while cufr:
            selv = cufr.f_locals.get('self', None)
            if selv is not None:
                orig = getattr(selv, '__origin__', None)
                if orig is self.__class__:
                    args = getattr(selv, '__args__')
                    break
            cufr = cufr.f_back

        if not args:
            msg = f'no type args given for "{Arg.name(self)}(…)"'
            msg = f'{msg}, need smth like "{Arg.name(self)}[T](…)"'
            raise TypeError(msg)

        if miss := next(filter(lambda arg: not self.okay(arg), args), None):
            msg = f'bad type arg "{Arg.name(miss)}" when declaring'
            msg = f'{msg} "{Arg.name(self)}", must be subclass of'
            msg = f'{msg} "{Arg.name(Arg)}" and not as it is now'
            raise TypeError(msg)

        return args

    def __new__(cls, *vals: object) -> typing.Self:
        return super().__new__(cls, *vals)

    def __init__(self, *vals: object) -> None:
        super().__init__(*vals)


class Str(Arg, str):
    def __new__(cls, val: str | int | bool | float) -> typing.Self:
        if isinstance(val, str | int | bool | float):
            return super().__new__(cls, val)

        raise Arg.terr(cls, val, str, int, bool, float)

    def __init__(self, val: str | int | bool | float) -> None:
        super().__init__()


class Rex(Str):
    def __new__(cls, val: str) -> typing.Self:
        if isinstance(val, str):
            return super().__new__(cls, val)

        raise Arg.terr(cls, val, str)

    def __init__(self, val: str) -> None:
        try:
            self.rex = re.compile(val)
        except Exception as e:
            raise Arg.verr(self, val) from e

        super().__init__(val)


class Int(Arg, int):
    def __new__(cls, val: str | int | bool | float) -> typing.Self:
        if isinstance(val, str | int | bool | float):
            try:
                return super().__new__(cls, val)
            except Exception as e:
                raise Arg.verr(cls, val) from e

        raise Arg.terr(cls, val, str, int, bool, float)

    def __init__(self, val: str | int | bool | float) -> None:
        super().__init__()


class Flt(Arg, float):
    def __new__(cls, val: str | int | bool | float) -> typing.Self:
        if isinstance(val, str | int | bool | float):
            try:
                return super().__new__(cls, val)
            except Exception as e:
                raise Arg.verr(cls, val) from e

        raise Arg.terr(cls, val, str, int, bool, float)

    def __init__(self, val: str | int | bool | float) -> None:
        super().__init__()


class Flg(Arg, int):
    def __new__(cls, val: str | int | bool | float) -> typing.Self:
        if isinstance(val, str):
            if val.lower() in ('true', 'yes', 't', 'y', 'sure'):
                val = True
            elif val.lower() in ('false', 'no', 'f', 'n', 'nope'):
                val = False
            else:
                try:
                    val = float(val)
                except Exception as e:
                    raise Arg.verr(cls, val) from e

        if isinstance(val, int | bool | float):
            if bool(val):
                return super().__new__(cls, 1)
            else:
                return super().__new__(cls, 0)

        raise Arg.terr(cls, val, str | int | bool | float)

    def __init__(self, val: str | int | bool | float) -> None:
        super().__init__()


ValGen = typing.TypeVar('ValGen', bound=Arg)


class Lst(Arg, list[ValGen]):
    def __new__(cls, val: list | tuple) -> typing.Self:
        if isinstance(val, list | tuple):
            return super().__new__(cls)

        raise Arg.terr(cls, val, list, tuple)

    def __init__(self, val: list | tuple) -> None:
        varg = self.args()[0]
        super().__init__([varg(itm) for itm in val])


KeyGen = typing.TypeVar('KeyGen', bound=Arg)


class Dct(Arg, dict[KeyGen, ValGen]):
    def __new__(cls, val: dict) -> typing.Self:
        if isinstance(val, dict):
            return super().__new__(cls, False, val)

        raise Arg.terr(cls, val, dict)

    def __init__(self, val: dict) -> None:
        args = self.args()
        karg, varg = args[0], args[1]
        super().__init__({karg(key): varg(val) for key, val in val.items()})


class Args:
    def __init__(self, args: dict[str, object]) -> None:
        if not isinstance(args, dict):
            raise Arg.terr(self, args, dict)

        for key, val in args.items():
            if not isinstance(key, str):
                raise Arg.terr(self, key, str)
            if val is None or not isinstance(val, object):
                raise Arg.terr(self, val, object)

        self.args = args

    def seek(self, key: str, arg: type[ValGen]) -> ValGen | None:
        val = self.args.pop(key, None)
        if val is None:
            return None
        return arg(val)

    def pull(self, key: str, arg: type[ValGen]) -> ValGen:
        val = self.seek(key, arg)
        if val is None:
            raise KeyError(key)
        return val
