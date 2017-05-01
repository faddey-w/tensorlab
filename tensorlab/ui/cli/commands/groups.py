from tensorlab import exceptions
from tensorlab.storage import TensorLabStorage
from tensorlab.core.groups import Attribute, AttributeTarget, AttributeType


def setup_arg_parser(subcommands):
    parser = subcommands.add_parser('group')
    commands = parser.add_subparsers(dest='subcommand', title='Commands')

    create_parser = commands.add_parser('create')
    create_parser.add_argument('name')

    show_parser = commands.add_parser('show')
    show_parser.add_argument('name', nargs='?')

    def_attr_parser = commands.add_parser('def-attr')
    def_attr_parser.add_argument('name')
    def_attr_parser.add_argument('--group', '-g', required=True)
    def_attr_parser.add_argument('--type', '-t', type=AttributeType)
    def_attr_parser.add_argument('--target', '--tgt', type=AttributeTarget)
    def_attr_parser.add_argument('--options', '--opt', default='')
    def_attr_parser.add_argument('--default')
    def_attr_parser.add_argument('--nullable', '--null', action='store_true', default=None)
    def_attr_parser.add_argument('--non-null', action='store_false', dest='nullable')

    remove_attr_parser = commands.add_parser('rem-attr')
    remove_attr_parser.add_argument('name')
    remove_attr_parser.add_argument('--group', '-g', required=True)

    rename_parser = commands.add_parser('rename')
    rename_parser.add_argument('old_name')
    rename_parser.add_argument('new_name')

    delete_parser = commands.add_parser('delete')
    delete_parser.add_argument('name')
    delete_parser.add_argument('--delete-all-content',
                               action='store_true', default=False,
                               dest='force')


def interpret(args):
    COMMANDS[args.subcommand](args)


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
            print_attribute(attr, 6)
    else:
        groups_list = storage.groups.list()
        if groups_list:
            for group in groups_list:
                print(group.name, '({})'.format(storage.groups.count_models(group)))
        else:
            print('Storage is empty')


def rename_group(args):
    storage = TensorLabStorage(args.root).Open()
    group = storage.groups.get(args.old_name)
    group.name = args.new_name
    group.save()
    print('Group "{}" was renamed into "{}"'.format(args.old_name, args.new_name))


def define_attr(args):
    storage = TensorLabStorage(args.root).Open()

    group = storage.groups.get(args.group)
    attr = group.get_attrs().get(args.name)
    action = 'update' if attr else 'create'
    if not attr:
        if not args.type:
            raise exceptions.IllegalArgumentError("--type is required for new attributes")
        if not args.target:
            raise exceptions.IllegalArgumentError("--target is required for new attributes")
        attr = Attribute(
            storage=storage.groups,
            name=args.name,
            type=args.type,
            target=args.target,
            default=args.default,
            options=args.options or '',
            nullable=args.nullable,
        )
    else:
        if args.type:
            raise exceptions.IllegalArgumentError("Attribute type cannot be changed")
        if args.target:
            raise exceptions.IllegalArgumentError("Attribute target cannot be changed")
        if args.default:
            attr.default = args.default
        if args.options is not None:
            attr.options = args.options
        if args.nullable is not None:
            attr.nullable = args.nullable

    if args.options is not None and not attr.type.validate_options(args.options):
        raise exceptions.IllegalArgumentError("Invalid options for type {}: {}"
                                              .format(attr.type.name, args.options))

    [attr] = group.update_attrs(attr)
    print('Attribute of group "{}" was {}d:'.format(group.name, action))
    print_attribute(attr, 3)


def remove_attr(args):
    storage = TensorLabStorage(args.root).Open()

    group = storage.groups.get(args.group)
    attr = group.get_attrs().get(args.name)

    [n_usages] = storage.groups.n_attribute_usages(group, attr)
    storage.groups.delete_attrs(group, attr)

    print('Removed attribute "{}" and {} its usages'
          .format(attr.name, n_usages))


def delete_group(args):
    storage = TensorLabStorage(args.root).Open()
    group = storage.groups.get(args.name)
    group.delete(args.force)
    print('Group "{}" was deleted'.format(group.name))


COMMANDS = {
    'create': create_group,
    'show': show_groups,
    'rename': rename_group,
    'def-attr': define_attr,
    'rem-attr': remove_attr,
    'delete': delete_group,
}


def print_attribute(attr: Attribute, indent=0):
    tab = ' '*indent
    print(tab, 'name:', attr.name)
    print(tab, 'target:', attr.target.name)
    print(tab, 'type:', attr.type.name, '(nullable)' if attr.nullable else '')
    if attr.default:
        print(tab, 'default:', attr.default)
    print(tab, 'options:', attr.options)
