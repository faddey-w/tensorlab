import enum


class AttributeTarget(enum.Enum):
    Model = 'Model'
    Instance = 'Instance'
    Run = 'Run'


class AttributeType(enum.Enum):
    Integer = 'Integer'
    Float = 'Float'
    String = 'String'
    Enum = 'Enum'

    def encode(self, value, options):
        encoder_name = '_encode_'+self.name.lower()
        encoder = getattr(self, encoder_name)
        return encoder(value, options)

    def decode(self, string, options):
        decoder_name = '_decode_'+self.name.lower()
        decoder = getattr(self, decoder_name)
        return decoder(string, options)

    def _encode_integer(self, value, options):
        if int(value) != value:
            raise TypeError('Expected integer, got {}'.format(value))
        value = int(value)
        if options == 'positive':
            if value < 0:
                raise ValueError('Expected positive integer, got {}'.format(value))
        elif options == 'negative':
            if value > 0:
                raise ValueError('Expected negative integer, got {}'.format(value))
        else:
            if options != '':
                raise ValueError('Unexpected option string')
        return str(value)

    def _encode_float(self, value, options):
        if float(value) != value:
            raise TypeError('Expected float, got {}'.format(value))
        return str(float(value))

    def _encode_string(self, value, options):
        return str(value)

    def _encode_enum(self, value, options):
        options = options.split(';')
        if value not in options:
            raise ValueError("Expected one of {}, got {}"
                             .format(', '.join(options), value))
        return str(value)

    def _decode_integer(self, string, options):
        return int(string)

    def _decode_float(self, string, options):
        return float(string)

    def _decode_string(self, string, options):
        return string

    def _decode_enum(self, string, options):
        return string




