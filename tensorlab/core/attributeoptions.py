import enum
from tensorlab import exceptions


class AttributeType(enum.Enum):
    """
    Defines type of attribute's values.
    Also provides utility code for serializing and deserializing values
    that is useful when working with databases
    or when parsing command line arguments.
    """
    Integer = 'Integer'
    Float = 'Float'
    String = 'String'
    Enum = 'Enum'

    def validate_options(self, options):
        if self == AttributeType.Integer:
            return options in ('positive', 'negative', '')
        elif self == AttributeType.Enum:
            return all(map(str.isidentifier, options.split(';')))
        else:
            return options == ''

    def encode(self, value, options):
        encoder_name = '_encode_'+self.name.lower()
        encoder = getattr(self, encoder_name)
        return encoder(value, options)

    def decode(self, string, options):
        decoder_name = '_decode_'+self.name.lower()
        decoder = getattr(self, decoder_name)
        return decoder(string, options)

    def _encode_integer(self, value, options):
        int_value = _cast(value, int)
        if options == 'positive':
            if int_value < 0:
                raise exceptions.IllegalArgumentError(
                    'Expected positive integer, got {!r}'.format(value))
        elif options == 'negative':
            if int_value > 0:
                raise exceptions.IllegalArgumentError(
                    'Expected negative integer, got {!r}'.format(value))
        return str(value)

    def _encode_float(self, value, options):
        float_value = _cast(value, float)
        return str(float_value)

    def _encode_string(self, value, options):
        return str(value)

    def _encode_enum(self, value, options):
        options = options.split(';')
        if value not in options:
            raise exceptions.IllegalArgumentError(
                    "Expected one of {}, got {!r}"
                    .format(', '.join(options), value))
        return str(value)

    def _decode_integer(self, string, options):
        return _cast(string, int)

    def _decode_float(self, string, options):
        return _cast(string, float)

    def _decode_string(self, string, options):
        return string

    def _decode_enum(self, string, options):
        return string


def _cast(value, type):
    try:
        return type(value)
    except (ValueError, TypeError) as exc:
        raise exceptions.IllegalArgumentError(str(exc))

