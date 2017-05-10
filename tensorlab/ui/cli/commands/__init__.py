import argparse
from tensorlab import config, exceptions
from . import root, groups, attrs, models, instances, views

SECTIONS = [
    root,
    groups,
    attrs,
    models,
    instances,
    views,
]


def make_parser(sections=None):
    if sections is None:
        sections = SECTIONS

    parser = _CustomizedArgumentParser()
    parser.add_argument('--root', default=None)
    parser.set_defaults(accepts_unknown=False)
    commands = parser.add_subparsers(dest='root_command', title='Commands')

    cmd_map = {}

    for section in sections:
        cmd_map.update(section.setup(commands))

    return parser, lambda args: cmd_map[args.root_command]


def check_root(args):
    if args.root is None:
        args.root = config.infer_tensorlab_root()
    if args.root is None:
        if args.root_command == 'init':
            args.root = config.get_default_tensorlab_root()
        else:
            raise exceptions.StorageInstantiationError(
                  "cannot find a TensorLab root neither in current directory nor"
                  " in any parent directory, and TENSORLAB variable is not set. "
                  "Please, change into the correct directory or specify the path."
            )


class _CustomizedArgumentParser(argparse.ArgumentParser):

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            if args.accepts_unknown:
                args.unknown_args = argv
            else:
                msg = 'unrecognized arguments: %s'
                self.error(msg % ' '.join(argv))
        else:
            args.unknown_args = None
        return args
