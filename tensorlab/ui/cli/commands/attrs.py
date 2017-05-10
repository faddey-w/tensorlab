from tensorlab import exceptions
from tensorlab.storage import TensorLabStorage
from tensorlab.core.groups import Attribute, AttributeTarget, AttributeType
from ._tools import spec


def setup(commands):
    parser = commands.add_parser('attr')
    subcommands = parser.add_subparsers(dest='attr_command', title='Commands')

    def_attr_parser = subcommands.add_parser('define')
    def_attr_parser.add_argument('attr_spec', type=spec('{group}/{attr}'))
    def_attr_parser.add_argument('--type', '-t', type=AttributeType)
    def_attr_parser.add_argument('--target', '--tgt', type=AttributeTarget)
    def_attr_parser.add_argument('--options', '--opt', default='')
    def_attr_parser.add_argument('--default')
    def_attr_parser.add_argument('--nullable', '--null', action='store_true', default=None)
    def_attr_parser.add_argument('--non-null', action='store_false', dest='nullable')

    remove_attr_parser = subcommands.add_parser('remove')
    remove_attr_parser.add_argument('attr_spec', type=spec('{group}/{attr}'))

    subcmd_dict = {
        'define': define_attr,
        'remove': remove_attr,
    }

    parser.set_defaults(
        attr_function=lambda args: subcmd_dict[args.attr_command])

    return {'attr': lambda args: args.attr_function(args)}


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


def print_attribute(attr: Attribute, indent=0):
    tab = ' '*indent
    print(tab, 'name:', attr.name)
    print(tab, 'target:', attr.target.name)
    print(tab, 'type:', attr.type.name, '(nullable)' if attr.nullable else '')
    if attr.default:
        print(tab, 'default:', attr.default)
    print(tab, 'options:', attr.options)
