import argparse


_root_parser = argparse.ArgumentParser()
_root_parser.add_argument('--root', default=None)
_sections = _root_parser.add_subparsers(dest='command_section')

_sections.add_parser('init')
_sections.add_parser('show')
# _project_parser = _sections.add_parser('project')
# _project_parser.add_argument('command', choices=['init', 'show'])
# _project_parser.add_argument('path', default=None)


def parse_args(argv=None):
    return _root_parser.parse_args(argv)
