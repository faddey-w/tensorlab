from test_tensorlab import TestCase

from tensorlab.core.attributeoptions import AttributeType
from tensorlab import exceptions


class AttributeTypeOptionValidationTests(TestCase):

    def test_integer_validate(self):
        validate = AttributeType.Integer.validate_options

        self.assertTrue(validate(''))
        self.assertTrue(validate('positive'))
        self.assertTrue(validate('negative'))

        self.assertFalse(validate('negative;positive'))
        self.assertFalse(validate('negativepositive'))
        self.assertFalse(validate('negative-positive'))
        self.assertFalse(validate(' positive'))
        self.assertFalse(validate(';negative'))

    def test_enum_validate(self):
        validate = AttributeType.Enum.validate_options

        self.assertTrue(validate('one;two;three'))
        self.assertTrue(validate('name1;name2'))
        self.assertTrue(validate('name'))
        self.assertTrue(validate('q1;q2;q3;q4;q5'))

        self.assertFalse(validate(''))
        self.assertFalse(validate('name1;name2;123'))
        self.assertFalse(validate('name1;name2;'))
        self.assertFalse(validate(' ;positive'))

    def _test_other_types(self, att_type):
        validate = att_type.validate_options

        self.assertTrue(validate(''))
        self.assertFalse(validate('anythingelse'))

    def test_float_validate(self):
        self._test_other_types(AttributeType.Float)

    def test_string_validate(self):
        self._test_other_types(AttributeType.String)


class AttributeTypeEncodingTests(TestCase):

    def test_encode_integer(self):
        encode = AttributeType.Integer.encode

        self.assertEqual(encode(0, ''), '0')
        self.assertEqual(encode('345', ''), '345')

        self.assertEqual(encode(111, ''), '111')
        self.assertEqual(encode(-222, ''), '-222')
        self.assertEqual(encode(333, 'positive'), '333')
        self.assertEqual(encode(-444, 'negative'), '-444')

        self.assertRaises(exceptions.IllegalArgumentError,
                          encode, 555, 'negative')
        self.assertRaises(exceptions.IllegalArgumentError,
                          encode, -666, 'positive')
        self.assertRaises(exceptions.IllegalArgumentError,
                          encode, object(), '')

    def test_encode_float(self):
        encode = AttributeType.Float.encode

        self.assertEqual(encode(0.0, ''), '0.0')
        self.assertEqual(encode(1.23, ''), '1.23')
        self.assertEqual(encode(-0.5, ''), '-0.5')
        self.assertEqual(encode(12e-10, ''), '1.2e-09')

        self.assertEqual(encode('-4.44', ''), '-4.44')
        self.assertEqual(encode(' -5.43', ''), '-5.43')

        self.assertRaises(exceptions.IllegalArgumentError,
                          encode, '@!#$', '')
        self.assertRaises(exceptions.IllegalArgumentError,
                          encode, 'qwerty', '')
        self.assertRaises(exceptions.IllegalArgumentError,
                          encode, object(), '')

    def test_encode_string(self):
        encode = AttributeType.String.encode

        self.assertEqual(encode(10, ''), '10')
        self.assertEqual(encode('hello', ''), 'hello')

        class dummy:
            def __str__(self):
                return 'dummy-object'
        self.assertEqual(encode(dummy(), ''), 'dummy-object')

    def test_encode_enum(self):
        encode = AttributeType.Enum.encode

        self.assertEqual(encode('name1', 'name1;name2'), 'name1')

        self.assertRaises(exceptions.IllegalArgumentError,
                          encode, 'name1', 'name3;name4')


class AttributeTypeDecodingTests(TestCase):

    def test_decode_integer(self):
        decode = AttributeType.Integer.decode

        self.assertEqual(decode('100', ''), 100)

        # decoding assumes that encoded value is valid
        self.assertEqual(decode('-10', 'positive'), -10)

        self.assertRaises(exceptions.IllegalArgumentError,
                          decode, '12.0', '')
        self.assertRaises(exceptions.IllegalArgumentError,
                          decode, '"10"', '')
        self.assertRaises(exceptions.IllegalArgumentError,
                          decode, 'hello', '')

    def test_decode_float(self):
        decode = AttributeType.Float.decode

        self.assertEqual(decode('1.2e-09', ''), 1.2e-09)
        self.assertEqual(decode('-100.4', ''), -100.4)

        self.assertRaises(exceptions.IllegalArgumentError,
                          decode, '"10"', '')
        self.assertRaises(exceptions.IllegalArgumentError,
                          decode, 'hello', '')

    def _test_decode_enum_or_string(self, attr_type):
        decode = attr_type.decode

        # decoding trusts to input and thinks it's always valid encoded string
        self.assertEqual(decode('value', ''), 'value')
        self.assertEqual(decode('option1', 'option1;option2'), 'option1')

        # it even doesn't do anything with its argument
        value = object()
        self.assertIs(decode(value, ''), value)

    def test_decode_enum(self):
        self._test_decode_enum_or_string(AttributeType.Enum)

    def test_decode_string(self):
        self._test_decode_enum_or_string(AttributeType.String)
