from . import _tools


def setup(commands):
    parser = commands.add_parser('model')
    subcommands = parser.add_subparsers(dest='model_command', title='Commands')

    model_spec = _tools.spec('{group}/{model}')

    show_parser = subcommands.add_parser('show')
    show_parser.add_argument('model_spec', type=model_spec)

    create_parser = subcommands.add_parser('create')
    create_parser.add_argument('model_spec', type=model_spec)
    create_parser.add_argument('--typeinfo', '--info', '-i', '-t')
    create_parser.add_argument('--attr', type=_tools.attr_type, nargs='*')

    update_parser = subcommands.add_parser('set')
    update_parser.add_argument('model_spec', type=model_spec)
    update_parser.add_argument('--typeinfo', '--info', '-i', '-t')
    update_parser.add_argument('--attr', type=_tools.attr_type, nargs='*')

    remove_parser = subcommands.add_parser('remove')
    remove_parser.add_argument('model_spec', type=model_spec)
    remove_parser.add_argument('--delete-model', dest='force',
                               action='store_true', default=False)

    subcmd_dict = {
        'show': show_model,
        'create': create_model,
        'set': update_model,
        'remove': remove_model,
    }

    return {'model': lambda args: subcmd_dict[args.model_command](args)}


def show_model(args):
    raise NotImplementedError


def create_model(args):
    raise NotImplementedError


def update_model(args):
    raise NotImplementedError


def remove_model(args):
    raise NotImplementedError

