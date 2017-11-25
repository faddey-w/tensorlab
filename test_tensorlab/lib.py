import unittest
import collections


class TestCaseMetaclass(type):

    def __new__(mcs, name, bases, attrs):
        attrs.setdefault('__abstract_test__', False)
        return super(TestCaseMetaclass, mcs).__new__(mcs, name, bases, attrs)

    def __dir__(cls):
        attrs = super(TestCaseMetaclass, cls).__dir__()
        if cls.__abstract_test__:
            attrs = [name for name in attrs if not name.startswith('test')]
        return attrs


class TestCase(unittest.TestCase, metaclass=TestCaseMetaclass):

    def assertItemsEqual(self, collection1, collection2, msg=None):
        cnt1 = collections.Counter(collection1)
        cnt2 = collections.Counter(collection2)
        self.assertEqual(dict(cnt1), dict(cnt2), msg)

