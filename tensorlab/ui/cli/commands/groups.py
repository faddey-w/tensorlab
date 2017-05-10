from tensorlab import exceptions
from tensorlab.storage import TensorLabStorage
from . import attrs


def setup(commands):
    parser = commands.add_parser('group')
    subcommands = parser.add_subparsers(dest='group_command', title='Commands')

    create_parser = subcommands.add_parser('create')
    create_parser.add_argument('name')

    show_parser = subcommands.add_parser('show')
    show_parser.add_argument('name', nargs='?')

    rename_parser = subcommands.add_parser('rename')
    rename_parser.add_argument('old_name')
    rename_parser.add_argument('new_name')

    delete_parser = subcommands.add_parser('delete')
    delete_parser.add_argument('name')
    delete_parser.add_argument('--delete-all-content',
                               action='store_true', default=False,
                               dest='force')

    attr_cmds = attrs.setup(subcommands)

    subcmd_dict = {
        'create': create_group,
        'show': show_groups,
        'delete': delete_group,
        'rename': rename_group,
        **attr_cmds
    }

    parser.set_defaults(
        group_function=lambda args: subcmd_dict[args.group_command])

    return {'group': lambda args: args.group_function(args)(args)}


def create_group(args):
    storage = TensorLabStorage(args.root).Open()
    group = storage.groups.new(args.name)
    group.save()
    print('Group {!r} was created'.format(group.name))


def show_groups(args):
    storage = TensorLabStorage(args.root).Open()
    if args.name:
        group = storage.groups.get(args.name)
        print('Group "{}":'.format(group.name))
        print('   Contains {} models with {} instances'
              .format(storage.groups.count_models(group),
                      storage.groups.count_instances(group)))
        for idx, attr in enumerate(storage.groups.list_attrs(group), 1):
            print('   Attribute #{}'.format(idx))
            attrs.print_attribute(attr, 6)
    else:
        groups_list = storage.groups.list()
        if groups_list:
            for group in groups_list:
                print(group.name, '({})'.format(storage.groups.count_models(group)))
        else:
            print('Storage is empty')


def delete_group(args):
    storage = TensorLabStorage(args.root).Open()
    group = storage.groups.get(args.name)
    group.delete(args.force)
    print('Group "{}" was deleted'.format(group.name))


def rename_group(args):
    storage = TensorLabStorage(args.root).Open()
    group = storage.groups.get(args.old_name)
    group.name = args.new_name
    group.save()
    print('Group "{}" was renamed into "{}"'.format(args.old_name, args.new_name))