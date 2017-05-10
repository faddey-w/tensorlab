import re


def make_registry():
    def register_subcommand(key):
        def decorator(function):
            if key in command_dict:
                raise KeyError('Subcommand "{}" already exists'.format(key))
            command_dict[key] = function
            return function

        return decorator
    command_dict = {}
    return command_dict, register_subcommand


def attr_type(s):
    key_value = s.split('=')
    if len(key_value) != 2:
        raise ValueError('Expected format: "key=value"')
    return key_value


def comma_separated_list_type(s):
    return s.split(',')


class SpecDef:

    _NAME_PATTERN = re.compile(r'\{\w+\}')
    _OPTIONAL_PATTERN = re.compile(r'\[[\w/\{\}]+\]')

    def __init__(self, pattern):
        parts = _split_with_delim(pattern, self._OPTIONAL_PATTERN)

        regex = ''
        names = []
        for part, is_optional in parts:
            if is_optional:
                part = part[1:-1]
            part_parts = _split_with_delim(part, self._NAME_PATTERN)
            regex_part = ''
            for part_part, is_name in part_parts:
                if is_name:
                    name = part_part[1:-1]
                    regex_part += '(?P<{}>\\w+)'.format(name)
                    names.append(name)
                else:
                    regex_part += part_part
            if is_optional:
                regex_part = '({})?'.format(regex_part)
            regex += regex_part

        self.pattern = pattern
        self.regex = re.compile(regex)
        self.names = tuple(names)

    def __call__(self, string):
        match = self.regex.match(string)
        if not match:
            raise ValueError('Expected pattern: "{}"'.format(self.pattern))
        return SpecMatch(self.names, {
            name: match.group(name)
            for name in self.names
        })


spec = SpecDef


class SpecMatch:

    def __init__(self, names, attributes):
        self.__names = names
        for attr, val in attributes.items():
            setattr(self, attr, val)

    def __repr__(self):
        return 'SpecMatch({})'.format(
            ', '.join('{}={!r}'.format(name, getattr(self, name))
                      for name in self.__names)
        )


def _split_with_delim(string, delimiter):
    parts = []
    next_idx = 0
    delimiter = re.compile(delimiter)
    for delim_match in delimiter.finditer(string):
        string_part = string[next_idx:delim_match.start()]
        next_idx = delim_match.end()
        parts.append((string_part, False))
        parts.append((delim_match.group(), True))
    parts.append((string[next_idx:], False))
    return parts
