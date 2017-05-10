from tensorlab import exceptions
from .commands import make_parser, check_root


def main():
    parser, get_command = make_parser()
    args = parser.parse_args()
    command = get_command(args)
    try:
        check_root(args)
        command(args)
    except exceptions.TensorLabError as err:
        print('ERROR:', err.message)
        return 1
    else:
        return 0
