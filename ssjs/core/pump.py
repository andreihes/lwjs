import ssjs.core.help as help
import ssjs.core.kind as kind


def load(source: help.TBIO) -> help.Schema:
    '''TODO'''

    schema = help.jsonc_load(source)
    if not isinstance(schema, help.Mapping) or len(schema) != 1:
        raise help.BadSsjs('ssjs root must be a single key mapping')

    key, val = next(iter(schema.items()))
    if not isinstance(val, help.Mapping):
        raise help.BadSsjs('ssjs root value must be a mapping')

    return kind.Kind(key, val)


def vrfy():
    ...


def pump(schema: help.Schema, object: help.Any) -> help.Any:
    ...
