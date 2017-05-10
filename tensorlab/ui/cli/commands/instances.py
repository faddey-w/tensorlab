from . import _tools


def setup(commands):
    parser = commands.add_parser('instance')
    subcommands = parser.add_subparsers(dest='instance_command', title='Commands')

    instance_spec = _tools.spec('{group}/{model}[/{instance}]')

    show_parser = subcommands.add_parser('show')
    show_parser.add_argument('instance_spec', type=instance_spec)

    create_parser = subcommands.add_parser('create')
    create_parser.add_argument('instance_spec', type=instance_spec)
    create_parser.add_argument('--attr', type=_tools.attr_type, nargs='*')

    update_parser = subcommands.add_parser('set')
    update_parser.add_argument('instance_spec', type=instance_spec)
    update_parser.add_argument('--attr', type=_tools.attr_type, nargs='*')

    remove_parser = subcommands.add_parser('remove')
    remove_parser.add_argument('instance_spec', type=instance_spec)
    remove_parser.add_argument('--delete-instance', dest='force',
                               action='store_true', default=False)

    mergeruns_parser = subcommands.add_parser('mergeruns')
    mergeruns_parser.add_argument('instance_spec', type=instance_spec)

    subcmd_dict = {
        'show': show_instance,
        'create': create_instance,
        'set': update_instance,
        'remove': remove_instance,
        'mergeruns': merge_runs,
    }

    return {'instance': lambda args: subcmd_dict[args.instance_command](args)}


def show_instance(args):
    raise NotImplementedError


def create_instance(args):
    raise NotImplementedError


def update_instance(args):
    raise NotImplementedError


def remove_instance(args):
    raise NotImplementedError


def merge_runs(args):
    raise NotImplementedError

