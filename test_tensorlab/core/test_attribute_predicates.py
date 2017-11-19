from test_tensorlab.lib import TestCase
from tensorlab.core.attribute_predicates import (
    parse_expression,
    Identifier,
    Literal,
    BinaryOperation,
    UnaryOperation,
    Op
)


class TestPredicatesParsing(TestCase):

    def test_identifier(self):
        self.assertEqual(parse_expression('var'), Identifier('var'))
        self.assertEqual(parse_expression('(var)'), Identifier('var'))

    def test_int_literal(self):
        self.assertEqual(parse_expression('15'), Literal(15))
        self.assertEqual(parse_expression('-108'), Literal(-108))

    def test_float_literal(self):
        self.assertEqual(parse_expression('15.3'), Literal(15.3))
        self.assertEqual(parse_expression('(-0.9)'), Literal(-0.9))

    def test_string_literal(self):
        self.assertEqual(parse_expression('\"value\"'), Literal('value'))
        self.assertEqual(parse_expression('\'test\''), Literal('test'))
        self.assertEqual(parse_expression('( \'qwerty\') '), Literal('qwerty'))
        self.assertEqual(parse_expression('\"value\''), None)

    def test_unary_operation(self):
        self.assertEqual(parse_expression('not test'),
                         UnaryOperation(Op.Not, Identifier('test')))
        self.assertEqual(
            parse_expression('not not (not 10)'),
            UnaryOperation(Op.Not,
                           UnaryOperation(Op.Not,
                                          UnaryOperation(Op.Not,
                                                         Literal(10))))
        )

    def test_binary_operation(self):
        self.assertEqual(parse_expression('10 <= qwe'),
                         BinaryOperation(Op.Le, Literal(10), Identifier('qwe')))
        self.assertEqual(
            parse_expression('not test > 15'),
            UnaryOperation(Op.Not,
                           BinaryOperation(Op.Gt,
                                           Identifier('test'),
                                           Literal(15))))
        self.assertEqual(parse_expression('not(X == 150)'),
                         UnaryOperation(Op.Not,
                                        BinaryOperation(Op.Eq, Identifier('X'),
                                                        Literal(150))))
        self.assertEqual(parse_expression('X == 150 or Y < 20.0'),
                         BinaryOperation(Op.Or,
                                         BinaryOperation(Op.Eq,
                                                         Identifier('X'),
                                                         Literal(150)),
                                         BinaryOperation(Op.Lt,
                                                         Identifier('Y'),
                                                         Literal(20.0))))
        self.assertEqual(parse_expression('(X == 150) or (Y < 20.0)'),
                         BinaryOperation(Op.Or,
                                         BinaryOperation(Op.Eq,
                                                         Identifier('X'),
                                                         Literal(150)),
                                         BinaryOperation(Op.Lt,
                                                         Identifier('Y'),
                                                         Literal(20.0))))

