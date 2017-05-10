from . import _tools


def setup(commands):
    parser = commands.add_parser('view')
    subcommands = parser.add_subparsers(dest='view_command', title='Commands')

    make_parser = subcommands.add_parser('make')
    make_parser.add_argument('name')
    make_parser.add_argument('--group', '-g')
    make_parser.add_argument('--attr', type=_tools.attr_type, nargs='*')
    make_parser.add_argument('--alias', type=_tools.attr_type, nargs='*')
    make_parser.add_argument('--order', type=_tools.comma_separated_list_type)

    remove_parser = subcommands.add_parser('remove')
    remove_parser.add_argument('name')

    board_run_parser = subcommands.add_parser('board')
    board_run_parser.add_argument('name')
    board_run_parser.set_defaults(accepts_unknown=True)

    subcmd_dict = {
        'make': make_view,
        'remove': remove_view,
        'board': run_tensorboard,
    }

    return {'view': lambda args: subcmd_dict[args.view_command](args)}


def make_view(args):
    raise NotImplementedError


def remove_view(args):
    raise NotImplementedError


def run_tensorboard(args):
    raise NotImplementedError
