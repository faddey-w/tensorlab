import argparse
from . import commands


_root_parser = argparse.ArgumentParser()
_root_parser.add_argument('--root', default=None)
_commands = _root_parser.add_subparsers(dest='command', title='Commands')

_commands.add_parser('init')
_commands.add_parser('show')

commands.groups.setup_arg_parser(_commands)


def parse_args(argv=None):
    return _root_parser.parse_args(argv)
