from tensorlab import config, exceptions
from .cmd_parse import parse_args
from .commands import COMMANDS


def main():
    args = parse_args()
    if args.root is None:
        args.root = config.infer_tensorlab_root()
    if args.root is None:
        if args.command_section == 'init':
            args.root = config.get_default_tensorlab_root()
        else:
            print("ERROR: cannot find a TensorLab root neither in current directory "
                  "nor in any parent directory, and TENSORLAB variable is not set. "
                  "Please, change into correct directory or specify the path.")
            return 1
    command = COMMANDS[args.command_section]
    try:
        command(args)
    except exceptions.TensorLabError as err:
        print('ERROR:')
        print(err.message)
        return 1
    else:
        return 0
