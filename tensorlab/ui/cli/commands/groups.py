from tensorlab.storage import TensorLabStorage


def setup_arg_parser(subcommands):
    parser = subcommands.add_parser('group')
    commands = parser.add_subparsers(dest='subcommand', title='Commands')

    create_parser = commands.add_parser('create')
    create_parser.add_argument('name')

    commands.add_parser('show')


def interpret(args):
    COMMANDS[args.subcommand](args)


def create_group(args):
    storage = TensorLabStorage(args.root).Open()
    group = storage.groups.new(args.name)
    group.save()
    print('Group {!r} was created'.format(group.name))


def show_groups(args):
    storage = TensorLabStorage(args.root).Open()
    groups_list = storage.groups.list()
    if groups_list:
        for group in groups_list:
            print(group.name, '({})'.format(storage.groups.count_models(group)))
    else:
        print('Storage is empty')


COMMANDS = {
    'create': create_group,
    'show': show_groups,
}
