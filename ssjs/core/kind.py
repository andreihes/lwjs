import ssjs.core.help as help


class Kind:
    @staticmethod
    def load_kind(key: str) -> help.Any:
        return None

    def __init__(self, kind: str, opts: help.Mapping) -> None:
        if len(kind) < 4:
            raise help.BadSsjs(f'bad kind "{kind}" (too short)')

        if kind[0] not in ('!', '?', '@'):
            raise help.BadSsjs(f'bad kind "{kind}" (bad miss flag)')

        self.IsMiss = kind[0] in ('?', '@')
        self.OnMiss = kind[0] == '@'

        if kind[1] not in ('!', '?', '@'):
            raise help.BadSsjs(f'bad kind "{kind}" (bad null flag)')

        self.IsNull = kind[1] in ('?', '@')
        self.OnNull = kind[1] == '@'

        self.KindKey = kind[3:]
        try:
            self.KindFun = Kind.load_kind(self.KindKey)
        except Exception as e:
            raise help.BadSsjs(f'bad kind "{kind}" (bad ssjs kind)') from e
