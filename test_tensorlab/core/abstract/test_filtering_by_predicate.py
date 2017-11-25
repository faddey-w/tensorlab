from ._base import StorageTestCase
from tensorlab.core import attributes
from tensorlab.core.attributeoptions import AttributeType as T
from tensorlab.core.attribute_predicates import parse_expression
from tensorlab import exceptions


class _BaseFilteringTests(StorageTestCase):
    __abstract_test__ = True

    def _make_attr(self, name, type, options='', nullable=False):
        """:rtype: attributes.Attribute"""
        raise NotImplementedError

    def _make_objects(self, *attrdicts):
        """:rtype: list"""
        raise NotImplementedError

    def _get_filtered(self, expression_str):
        """
        :type expression_str: str
        :rtype: list
        """
        raise NotImplementedError

    def test_integer_equality(self):
        self._make_attr('a1', T.Integer)
        o1, o2, o3 = self._make_objects(
            {'a1': 10},
            {'a1': 5},
            {'a1': 10},
        )
        self.assertItemsEqual(self._get_filtered('a1==10'), [o1, o3])
        self.assertItemsEqual(self._get_filtered('a1==5'), [o2])
        self.assertItemsEqual(self._get_filtered('a1==7'), [])

    def test_float_comparison(self):
        self._make_attr('a1', T.Float)
        o1, o2, o3 = self._make_objects(
            {'a1': 2.0},
            {'a1': 4.0},
            {'a1': -5.0},
        )
        self.assertItemsEqual(self._get_filtered('a1 < 3'), [o1, o3])
        self.assertItemsEqual(self._get_filtered('a1 > 2.0'), [o2])
        self.assertItemsEqual(self._get_filtered('a1 >= 2.0'), [o1, o2])
        self.assertItemsEqual(self._get_filtered('a1 < -6'), [])

    def test_enum_equality(self):
        self._make_attr('a1', T.Enum, options='qwe;asd;zxc')
        o1, o2, o3 = self._make_objects(
            {'a1': 'qwe'},
            {'a1': 'asd'},
            {'a1': 'asd'},
        )
        self.assertItemsEqual(self._get_filtered('a1=="qwe"'), [o1])
        self.assertItemsEqual(self._get_filtered('a1=="asd"'), [o2, o3])
        self.assertItemsEqual(self._get_filtered('a1=="zxc'), [])
        with self.assertRaises(exceptions.IllegalArgumentError):
            self._get_filtered('a1=="rty')

    def test_string_equality(self):
        self._make_attr('a1', T.String)
        o1, o2, o3 = self._make_objects(
            {'a1': 'qwe'},
            {'a1': 'asd'},
            {'a1': 'asd'},
        )
        self.assertItemsEqual(self._get_filtered('a1=="qwe"'), [o1])
        self.assertItemsEqual(self._get_filtered('a1=="asd"'), [o2, o3])
        self.assertItemsEqual(self._get_filtered('a1=="zxc'), [])
        self.assertItemsEqual(self._get_filtered('a1=="rty'), [])

    def test_complex_expression(self):
        self._make_attr('s1', T.String)
        self._make_attr('s2', T.String)
        self._make_attr('i', T.Integer)

        o11, o12, o13 = self._make_objects(
            {'s1': 'qwe', 's2': 'asd', 'i': 2},
            {'s1': 'qwe', 's2': 'asd', 'i': 4},
            {'s1': 'qwe', 's2': 'asd', 'i': 6},
        )
        o21, o22, o23 = self._make_objects(
            {'s1': 'qwe', 's2': 'fgh', 'i': 2},
            {'s1': 'qwe', 's2': 'fgh', 'i': 4},
            {'s1': 'qwe', 's2': 'fgh', 'i': 6},
        )
        o31, o32, o33 = self._make_objects(
            {'s1': 'rty', 's2': 'asd', 'i': 2},
            {'s1': 'rty', 's2': 'asd', 'i': 4},
            {'s1': 'rty', 's2': 'asd', 'i': 6},
        )
        o41, o42, o43 = self._make_objects(
            {'s1': 'rty', 's2': 'fgh', 'i': 2},
            {'s1': 'rty', 's2': 'fgh', 'i': 4},
            {'s1': 'rty', 's2': 'fgh', 'i': 6},
        )
        self.assertItemsEqual(
            self._get_filtered('s1 == "qwe" and i > 5 or s2 == "asd" and i < 3'),
            [o13, o23, o11, o31]
        )


class ModelFilteringTests(_BaseFilteringTests):
    __abstract_test__ = True

    def _make_attr(self, name, type, options='', nullable=False):
        return self._fixture_attr(None, name=name, runtime=False,
                                  type=type, options=options, default=None,
                                  nullable=nullable)

    def _make_objects(self, *attrdicts):
        return [
            self._fixture_model(None, 'model{}'.format(i), attrs)
            for i, attrs in enumerate(attrdicts)
        ]

    def _get_filtered(self, expression_str):
        expr = parse_expression(expression_str)
        return self.models_storage.list(None, predicate=expr)


class RunFilteringTests(_BaseFilteringTests):
    __abstract_test__ = True

    def setUp(self):
        self._model = self._fixture_model(None, 'mdl', {})

    def _make_attr(self, name, type, options='', nullable=False):
        return self._fixture_attr(None, name=name, runtime=True,
                                  type=type, options=options, default=None,
                                  nullable=nullable)

    def _make_objects(self, *attrdicts):
        return [
            self._fixture_run(self._model, attrs)
            for attrs in attrdicts
        ]

    def _get_filtered(self, expression_str):
        expr = parse_expression(expression_str)
        return self.runs_storage.list(self._model, predicate=expr)
