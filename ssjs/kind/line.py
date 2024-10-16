import ssjs.args as args
import ssjs.base as base


@base.kind('line')
class Line(base.Kind):
    def __init__(self, arg: args.Args) -> None:
        self.min = arg.seek('min', args.Int)
        self.max = arg.seek('max', args.Int)
        self.rex = arg.seek('rex', args.Rex)

    def fixes(self, ctx: base.Ctx) -> base.FixItr:
        if not isinstance(ctx.data, str):
            yield base.Fix('data is not a line')
            return

        if self.min and len(ctx.data) < self.min:
            yield base.Fix('line is too short')

        if self.max and len(ctx.data) > self.max:
            yield base.Fix('line is too long')

        if self.rex and not self.rex.rex.match(ctx.data):
            yield base.Fix('line does not match')
