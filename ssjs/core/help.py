import io
import json
import typing


Any = typing.Any
TextIO = typing.TextIO
Mapping = typing.Mapping
BinaryIO = typing.BinaryIO
TBIO = TextIO | BinaryIO
Schema = Any

# class Schema(typing.TypedDict):
#    ...


class BadSsjs(Exception):
    pass


def jsonc_load(source: TBIO):
    ''''''

    lines = io.StringIO()
    for line in source:
        if not line.strip().startswith('//'):
            lines.write(line)

    lines.seek(0)
    return json.load(lines)
